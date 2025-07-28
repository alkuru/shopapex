import os
import requests
import hashlib

API_HOST = os.environ.get('VIN_API_HOST')
API_LOGIN = os.environ.get('VIN_API_LOGIN')
API_PASSWORD = os.environ.get('VIN_API_PASSWORD')

# Пароль должен быть в md5-хэше!
def get_md5_hash(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

API_URL = f"https://{API_HOST}/search/articles/"

def normalize_brand(brand):
    if not brand:
        return None
    # Нормализуем бренд для поиска
    normalized = brand.strip().lower().replace(' ', '').replace('-', '').replace('/', '')
    
    # Особые случаи для бренда Mann
    if normalized in ['mann', 'mannfilter']:
        return 'MANN-FILTER'
    
    # Особые случаи для бренда Mahle
    if normalized in ['mahle', 'knechtmahle']:
        return 'Knecht/Mahle'
    
    return brand

def get_purchase_price(article, brand=None):
    """
    Получить закупочную цену для артикула через API ABCP
    """
    params = {
        'userlogin': API_LOGIN,
        'userpsw': get_md5_hash(API_PASSWORD),
        'number': article,
        'format': 'json',
    }
    if brand:
        params['brand'] = normalize_brand(brand)
    
    print(f"\n🔍 Поиск цены для {article}, бренд: {brand} -> {normalize_brand(brand)}")
    
    response = requests.get(API_URL, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict):
            items = data.get('search', [])
        elif isinstance(data, list):
            items = data
        else:
            items = []
        
        print(f"📦 Найдено предложений: {len(items)}")
        
        # Фильтрация по бренду и поиск минимальной цены
        norm_brand = normalize_brand(brand) if brand else None
        brand_items = []
        
        for i, item in enumerate(items):
            item_brand = item.get('brand', '').strip()
            item_price = item.get('price', 0)
            print(f"  {i+1}. Бренд: '{item_brand}' -> Цена: {item_price}")
            
            if norm_brand:
                # Нормализуем оба бренда для сравнения
                item_brand_norm = normalize_brand(item_brand)
                if item_brand_norm == norm_brand:
                    brand_items.append(item)
                    print(f"    ✅ Совпадение: '{item_brand}' -> '{item_brand_norm}' == '{norm_brand}'")
                elif item_brand == norm_brand:
                    # Дополнительная проверка для прямого соответствия
                    brand_items.append(item)
                    print(f"    ✅ Прямое совпадение с {norm_brand}")
                elif brand.lower().replace(' ', '').replace('-', '') in item_brand.lower().replace(' ', '').replace('-', '') or item_brand.lower().replace(' ', '').replace('-', '') in brand.lower().replace(' ', '').replace('-', ''):
                    # Проверка на частичное вхождение
                    brand_items.append(item)
                    print(f"    ✅ Частичное совпадение: '{item_brand}' содержит '{brand}'")
        
        print(f"🎯 Подходящих по бренду: {len(brand_items)}")
        
        # Если есть предложения по бренду — ищем минимальную цену
        if brand_items:
            min_item = min(brand_items, key=lambda x: float(x['price']))
            print(f"💰 Минимальная цена по бренду: {min_item['price']}")
            return float(min_item['price'])
        
        print("❌ Предложений по нужному бренду не найдено")
        return None
    
    print(f"❌ API вернул код: {response.status_code}")
    # Если не найдено — пробуем артикул без пробелов и слэшей
    alt_article = article.replace(' ', '').replace('/', '').upper()
    if alt_article != article:
        params['number'] = alt_article
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                items = data.get('search', [])
            elif isinstance(data, list):
                items = data
            else:
                items = []
            found = None
            if norm_brand:
                for item in items:
                    item_brand = item.get('brand', '').strip().upper().replace(' ', '').replace('-', '')
                    if item_brand == norm_brand.replace('-', '').upper():
                        found = item
                        break
            if not found and items:
                found = items[0]
            if found:
                return float(found['price'])
    return None
