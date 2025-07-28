import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

import json

def load_autosputnik_brands():
    """Загружает бренды из файла АвтоСпутника"""
    try:
        with open('brands_data/response_1753575298222.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('error') is None and 'data' in data:
            brands = [item['name'] for item in data['data']]
            print(f"Загружено {len(brands)} брендов из АвтоСпутника")
            return brands
        else:
            print("Ошибка в структуре файла АвтоСпутника")
            return []
    except Exception as e:
        print(f"Ошибка загрузки брендов АвтоСпутника: {e}")
        return []

def load_existing_brands():
    """Загружает существующие бренды из brand_analysis_results.json"""
    try:
        if os.path.exists('brand_analysis_results.json'):
            with open('brand_analysis_results.json', 'r', encoding='utf-8') as f:
                existing_mapping = json.load(f)
            
            # Получаем уникальные бренды из ключей
            brands = list(existing_mapping.keys())
            print(f"Загружено {len(brands)} брендов из существующего файла")
            return brands
        else:
            print("Файл brand_analysis_results.json не найден")
            return []
    except Exception as e:
        print(f"Ошибка загрузки существующих брендов: {e}")
        return []

def normalize_brand_name(brand_name):
    """Нормализует название бренда для сравнения"""
    if not brand_name:
        return ""
    
    # Приводим к нижнему регистру и убираем лишние пробелы
    normalized = brand_name.lower().strip()
    
    # Убираем специальные символы, оставляем только буквы, цифры и пробелы
    import re
    normalized = re.sub(r'[^\w\s]', '', normalized)
    
    # Убираем множественные пробелы
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()

def find_best_match(autokontinent_brand, autosputnik_brands):
    """Находит лучшее соответствие бренда АвтоКонтинента в списке АвтоСпутника"""
    normalized_ak = normalize_brand_name(autokontinent_brand)
    
    if not normalized_ak:
        return None
    
    # Точное совпадение
    for as_brand in autosputnik_brands:
        if normalize_brand_name(as_brand) == normalized_ak:
            return as_brand
    
    # Частичное совпадение (содержит)
    for as_brand in autosputnik_brands:
        normalized_as = normalize_brand_name(as_brand)
        if normalized_ak in normalized_as or normalized_as in normalized_ak:
            return as_brand
    
    # Поиск по ключевым словам
    keywords = normalized_ak.split()
    for as_brand in autosputnik_brands:
        normalized_as = normalize_brand_name(as_brand)
        as_keywords = normalized_as.split()
        
        # Если есть общие ключевые слова
        common_keywords = set(keywords) & set(as_keywords)
        if len(common_keywords) >= min(len(keywords), len(as_keywords)) * 0.7:
            return as_brand
    
    return None

def create_perfect_mapping():
    """Создает идеальный маппинг брендов"""
    print("Начинаем создание идеального маппинга брендов...")
    
    # Загружаем бренды
    autosputnik_brands = load_autosputnik_brands()
    autokontinent_brands = load_existing_brands()
    
    if not autosputnik_brands or not autokontinent_brands:
        print("Не удалось загрузить бренды")
        return
    
    # Создаем маппинг
    brand_mapping = {}
    matched_count = 0
    unmatched_count = 0
    
    print(f"\nОбрабатываем {len(autokontinent_brands)} брендов АвтоКонтинента...")
    
    for ak_brand in autokontinent_brands:
        best_match = find_best_match(ak_brand, autosputnik_brands)
        
        if best_match:
            brand_mapping[ak_brand] = best_match
            matched_count += 1
            print(f"✓ {ak_brand} -> {best_match}")
        else:
            # Если не найдено соответствие, оставляем как есть
            brand_mapping[ak_brand] = ak_brand
            unmatched_count += 1
            print(f"✗ {ak_brand} -> {ak_brand} (не найдено соответствие)")
    
    # Сохраняем результат
    with open('brand_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(brand_mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== РЕЗУЛЬТАТ ===")
    print(f"Всего брендов: {len(autokontinent_brands)}")
    print(f"Найдено соответствий: {matched_count}")
    print(f"Не найдено соответствий: {unmatched_count}")
    print(f"Процент соответствия: {matched_count/len(autokontinent_brands)*100:.1f}%")
    print(f"\nМаппинг сохранен в brand_analysis_results.json")

if __name__ == "__main__":
    create_perfect_mapping() 