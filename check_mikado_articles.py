import os
import django
import pandas as pd
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def normalize_article(article):
    """Нормализация артикула для сравнения"""
    if not article:
        return ''
    return str(article).strip().lower().replace(' ', '').replace('-', '').replace('.', '')

def load_original_file():
    """Загрузка оригинального файла Mikado"""
    print("=== ЗАГРУЗКА ОРИГИНАЛЬНОГО ФАЙЛА ===")
    
    # Путь к файлу в папке import
    file_path = 'import/SPB-MSK_0033749_250725.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден!")
        return None
        
    df = pd.read_excel(file_path)
    print(f"✅ Загружено {len(df)} строк из файла")
    
    # Создаем словарь: нормализованный артикул -> оригинальный артикул + бренд
    article_mapping = {}
    
    for _, row in df.iterrows():
        orig_article = str(row['Код товара']).strip()
        brand = str(row['Бренд']).strip()
        norm_article = normalize_article(orig_article)
        
        if norm_article:
            article_mapping[norm_article] = {
                'article': orig_article,
                'brand': brand
            }
    
    print(f"✅ Создан маппинг для {len(article_mapping)} артикулов")
    return article_mapping

def check_articles():
    """Проверка артикулов в базе"""
    print("\n=== ПРОВЕРКА АРТИКУЛОВ В БАЗЕ ===")
    
    # Загружаем маппинг из оригинального файла
    original_mapping = load_original_file()
    if not original_mapping:
        return
    
    # Получаем все артикулы и бренды из базы
    db_products = MikadoProduct.objects.values('article', 'brand')
    print(f"✅ Получено {len(db_products)} товаров из базы")
    
    # Статистика
    stats = {
        'total': len(db_products),
        'matched': 0,
        'mismatched': 0,
        'mismatches': []
    }
    
    # Проверяем каждый артикул
    for product in db_products:
        db_article = product['article']
        db_brand = product['brand']
        norm_db = normalize_article(db_article)
        
        if norm_db in original_mapping:
            orig_data = original_mapping[norm_db]
            
            if db_article != orig_data['article'] or db_brand != orig_data['brand']:
                stats['mismatched'] += 1
                stats['mismatches'].append({
                    'db_article': db_article,
                    'db_brand': db_brand,
                    'orig_article': orig_data['article'],
                    'orig_brand': orig_data['brand']
                })
            else:
                stats['matched'] += 1
        else:
            stats['mismatched'] += 1
            stats['mismatches'].append({
                'db_article': db_article,
                'db_brand': db_brand,
                'orig_article': 'НЕ НАЙДЕН',
                'orig_brand': 'НЕ НАЙДЕН'
            })
    
    # Выводим результаты
    print("\n=== РЕЗУЛЬТАТЫ ПРОВЕРКИ ===")
    print(f"Всего товаров: {stats['total']}")
    print(f"Точных совпадений: {stats['matched']}")
    print(f"Несовпадений: {stats['mismatched']}")
    
    if stats['mismatched'] > 0:
        print("\n=== НЕСОВПАДАЮЩИЕ ТОВАРЫ ===")
        for mismatch in stats['mismatches'][:20]:  # Показываем первые 20
            print(f"В базе: {mismatch['db_article']} ({mismatch['db_brand']}) | " + \
                  f"Оригинал: {mismatch['orig_article']} ({mismatch['orig_brand']})")
        
        if len(stats['mismatches']) > 20:
            print(f"... и еще {len(stats['mismatches']) - 20} несовпадений")
            
        # Создаем маппинг для исправления
        print("\n=== СОЗДАНИЕ МАППИНГА ===")
        mapping_file = 'mikado_article_mapping.txt'
        
        with open(mapping_file, 'w', encoding='utf-8') as f:
            f.write("DB_ARTICLE\tDB_BRAND\tORIG_ARTICLE\tORIG_BRAND\n")
            for mismatch in stats['mismatches']:
                if mismatch['orig_article'] != 'НЕ НАЙДЕН':
                    f.write(f"{mismatch['db_article']}\t{mismatch['db_brand']}\t" + \
                           f"{mismatch['orig_article']}\t{mismatch['orig_brand']}\n")
        
        print(f"✅ Маппинг сохранен в {mapping_file}")
        
        # Предлагаем SQL для исправления
        print("\n=== SQL ДЛЯ ИСПРАВЛЕНИЯ ===")
        print("-- Пример SQL для обновления артикулов и брендов:")
        for mismatch in stats['mismatches'][:5]:
            if mismatch['orig_article'] != 'НЕ НАЙДЕН':
                print(f"UPDATE catalog_mikadosproduct " + \
                      f"SET article = '{mismatch['orig_article']}', " + \
                      f"brand = '{mismatch['orig_brand']}' " + \
                      f"WHERE article = '{mismatch['db_article']}' AND " + \
                      f"brand = '{mismatch['db_brand']}';")
        print("-- ...")
    
    return stats

if __name__ == "__main__":
    print("=== ПРОВЕРКА АРТИКУЛОВ MIKADO ===")
    stats = check_articles()
    
    if stats:
        print("\n=== ИТОГ ===")
        accuracy = (stats['matched'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"Точность артикулов: {accuracy:.2f}%")
        
        if stats['mismatched'] > 0:
            print("\n=== РЕКОМЕНДАЦИИ ===")
            print("1. Проверьте mikado_article_mapping.txt")
            print("2. Используйте SQL-запросы для исправления артикулов и брендов")
            print("3. После исправления перезапустите проверку") 