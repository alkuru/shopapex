import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct
from django.db import transaction

def normalize_article(article):
    """Нормализация артикула для сравнения"""
    if not article:
        return ''
    return str(article).strip().lower().replace(' ', '').replace('-', '').replace('.', '')

def load_original_file():
    """Загрузка оригинального файла Mikado"""
    print("=== ЗАГРУЗКА ОРИГИНАЛЬНОГО ФАЙЛА ===")
    
    file_path = 'import/SPB-MSK_0033749_250725.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден!")
        return None
        
    df = pd.read_excel(file_path)
    print(f"✅ Загружено {len(df)} строк из файла")
    
    # Создаем словарь: нормализованный артикул -> данные
    article_mapping = {}
    
    for _, row in df.iterrows():
        orig_article = str(row['Код товара']).strip()
        brand = str(row['Бренд']).strip()
        name = str(row['Наименование товара']).strip()
        stock_spb = int(row.get('Кол-во СПб', 0) or 0)
        stock_msk = int(row.get('Кол-во МСК', 0) or 0)
        price = float(row.get('Цена', 0) or 0)
        multiplicity = int(row.get('Кратность', 1) or 1)
        unit = str(row.get('Ед. Изм.', 'шт')).strip()
        
        norm_article = normalize_article(orig_article)
        
        if norm_article:
            article_mapping[norm_article] = {
                'article': orig_article,
                'brand': brand,
                'name': name,
                'stock_quantity': stock_spb + stock_msk,
                'price': price,
                'multiplicity': multiplicity,
                'unit': unit
            }
    
    print(f"✅ Создан маппинг для {len(article_mapping)} артикулов")
    return article_mapping

def fix_articles():
    """Безопасное исправление артикулов и брендов"""
    print("=== БЕЗОПАСНОЕ ИСПРАВЛЕНИЕ АРТИКУЛОВ И БРЕНДОВ ===")
    
    # Загружаем маппинг
    original_mapping = load_original_file()
    if not original_mapping:
        return
    
    # Создаем лог-файл
    log_file = f'mikado_fixes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    stats = {
        'total': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    print("\n=== НАЧИНАЕМ ИСПРАВЛЕНИЕ ===")
    
    with open(log_file, 'w', encoding='utf-8') as log:
        def write_log(message):
            print(message)
            log.write(message + "\n")
            log.flush()
        
        # Получаем все товары из базы
        products = MikadoProduct.objects.all()
        total = products.count()
        stats['total'] = total
        
        write_log(f"Всего товаров в базе: {total}")
        
        # Обрабатываем каждый товар
        for idx, product in enumerate(products, 1):
            try:
                norm_article = normalize_article(product.article)
                
                if norm_article in original_mapping:
                    orig_data = original_mapping[norm_article]
                    
                    changes = []
                    if product.article != orig_data['article']:
                        changes.append(f"артикул: {product.article} -> {orig_data['article']}")
                    if product.brand != orig_data['brand']:
                        changes.append(f"бренд: {product.brand} -> {orig_data['brand']}")
                    
                    if changes:
                        try:
                            with transaction.atomic():
                                # Проверяем, нет ли дубликата
                                duplicate = MikadoProduct.objects.filter(
                                    article=orig_data['article'],
                                    brand=orig_data['brand']
                                ).exclude(id=product.id).first()
                                
                                if duplicate:
                                    write_log(f"⚠️ ПРОПУЩЕН {product.article} ({product.brand}): " + \
                                            f"уже есть товар {duplicate.article} ({duplicate.brand})")
                                    stats['skipped'] += 1
                                    continue
                                
                                # Обновляем товар
                                old_article = product.article
                                old_brand = product.brand
                                
                                product.article = orig_data['article']
                                product.brand = orig_data['brand']
                                product.name = orig_data['name']
                                product.stock_quantity = orig_data['stock_quantity']
                                product.price = orig_data['price']
                                product.multiplicity = orig_data['multiplicity']
                                product.unit = orig_data['unit']
                                product.save()
                                
                                write_log(f"✅ ИСПРАВЛЕН {old_article} ({old_brand}): {', '.join(changes)}")
                                stats['updated'] += 1
                        
                        except Exception as e:
                            write_log(f"❌ ОШИБКА {product.article}: {str(e)}")
                            stats['errors'] += 1
                    
                if idx % 1000 == 0:
                    write_log(f"Прогресс: {idx}/{total} " + \
                            f"(обновлено: {stats['updated']}, " + \
                            f"пропущено: {stats['skipped']}, " + \
                            f"ошибок: {stats['errors']})")
            
            except Exception as e:
                write_log(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
                stats['errors'] += 1
        
        # Итоговая статистика
        write_log("\n=== ИТОГОВЫЙ РЕЗУЛЬТАТ ===")
        write_log(f"Всего обработано: {stats['total']}")
        write_log(f"Обновлено: {stats['updated']}")
        write_log(f"Пропущено: {stats['skipped']}")
        write_log(f"Ошибок: {stats['errors']}")
    
    print(f"\n✅ Лог сохранен в {log_file}")
    return stats

if __name__ == "__main__":
    print("=== БЕЗОПАСНОЕ ИСПРАВЛЕНИЕ MIKADO ===")
    stats = fix_articles()
    
    if stats:
        print("\n=== РЕКОМЕНДАЦИИ ===")
        print(f"1. Проверьте лог-файл")
        print(f"2. Убедитесь, что все товары обновлены корректно")
        print(f"3. Запустите проверку артикулов снова") 