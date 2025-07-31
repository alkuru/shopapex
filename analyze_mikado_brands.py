#!/usr/bin/env python
import pandas as pd
import requests
import json

def get_autosputnik_brands():
    """Получаем список брендов от АвтоСпутника"""
    try:
        # API АвтоСпутника
        API_URL = 'https://newapi.auto-sputnik.ru'
        LOGIN = '89219520754'
        PASSWORD = '89219520754'
        
        # Получаем токен
        token_url = f'{API_URL}/users/login'
        token_data = {'login': LOGIN, 'password': PASSWORD}
        token_response = requests.post(token_url, json=token_data, timeout=10)
        
        if token_response.status_code != 200:
            print("❌ Ошибка получения токена АвтоСпутника")
            return set()
        
        token = token_response.json().get('token')
        if not token:
            print("❌ Токен не получен")
            return set()
        
        # Получаем бренды
        brands_url = f'{API_URL}/products/getbrands'
        headers = {'Authorization': f'Bearer {token}'}
        brands_response = requests.get(brands_url, headers=headers, timeout=30)
        
        if brands_response.status_code != 200:
            print("❌ Ошибка получения брендов")
            return set()
        
        brands_data = brands_response.json()
        autosputnik_brands = set()
        
        if isinstance(brands_data, list):
            for brand_info in brands_data:
                if isinstance(brand_info, dict) and 'name' in brand_info:
                    autosputnik_brands.add(brand_info['name'])
                elif isinstance(brand_info, str):
                    autosputnik_brands.add(brand_info)
        
        print(f"✅ Получено {len(autosputnik_brands)} брендов от АвтоСпутника")
        return autosputnik_brands
        
    except Exception as e:
        print(f"❌ Ошибка получения брендов АвтоСпутника: {e}")
        return set()

def analyze_mikado_brands():
    """Анализируем бренды Mikado и сравниваем с АвтоСпутником"""
    
    print("=== АНАЛИЗ БРЕНДОВ MIKADO ===")
    
    # Читаем прайс Mikado
    file_path = "import/SPB-MSK_0033749_250725.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        print(f"Загружен прайс Mikado: {len(df)} товаров")
        
        # Извлекаем уникальные бренды из Mikado
        mikado_brands = set(df['Бренд'].dropna().astype(str).str.strip())
        print(f"Уникальных брендов в Mikado: {len(mikado_brands)}")
        
        # Получаем бренды АвтоСпутника
        autosputnik_brands = get_autosputnik_brands()
        
        if not autosputnik_brands:
            print("❌ Не удалось получить бренды АвтоСпутника")
            return
        
        # Функция нормализации для сравнения
        def normalize_brand(brand):
            return str(brand).lower().strip().replace(' ', '').replace('-', '').replace('/', '').replace('_', '')
        
        # Создаем нормализованные множества
        mikado_normalized = {normalize_brand(b): b for b in mikado_brands}
        autosputnik_normalized = {normalize_brand(b): b for b in autosputnik_brands}
        
        # Анализ соответствий
        exact_matches = []
        partial_matches = []
        no_matches = []
        
        print("\n=== ПОИСК СООТВЕТСТВИЙ ===")
        
        for mikado_norm, mikado_original in mikado_normalized.items():
            found_match = False
            
            # Точное соответствие
            if mikado_norm in autosputnik_normalized:
                autosputnik_brand = autosputnik_normalized[mikado_norm]
                exact_matches.append({
                    'mikado': mikado_original,
                    'autosputnik': autosputnik_brand,
                    'type': 'exact'
                })
                found_match = True
            else:
                # Частичное соответствие
                for as_norm, as_original in autosputnik_normalized.items():
                    if (mikado_norm in as_norm or as_norm in mikado_norm) and len(mikado_norm) > 2:
                        partial_matches.append({
                            'mikado': mikado_original,
                            'autosputnik': as_original,
                            'type': 'partial'
                        })
                        found_match = True
                        break
            
            if not found_match:
                no_matches.append(mikado_original)
        
        print(f"✅ Точных соответствий: {len(exact_matches)}")
        print(f"🔶 Частичных соответствий: {len(partial_matches)}")
        print(f"❌ Без соответствий: {len(no_matches)}")
        
        # Сохраняем результат анализа
        result = {
            'exact_matches': exact_matches,
            'partial_matches': partial_matches,
            'no_matches': no_matches,
            'stats': {
                'total_mikado_brands': len(mikado_brands),
                'total_autosputnik_brands': len(autosputnik_brands),
                'exact_matches_count': len(exact_matches),
                'partial_matches_count': len(partial_matches),
                'no_matches_count': len(no_matches)
            }
        }
        
        # Сохраняем в файл
        output_file = 'mikado_brand_analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Результат сохранен в {output_file}")
        
        # Показываем примеры
        print(f"\n=== ПРИМЕРЫ ТОЧНЫХ СООТВЕТСТВИЙ ===")
        for match in exact_matches[:10]:
            print(f"  '{match['mikado']}' -> '{match['autosputnik']}'")
        
        print(f"\n=== ПРИМЕРЫ ЧАСТИЧНЫХ СООТВЕТСТВИЙ ===")
        for match in partial_matches[:10]:
            print(f"  '{match['mikado']}' -> '{match['autosputnik']}'")
        
        print(f"\n=== ПРИМЕРЫ БЕЗ СООТВЕТСТВИЙ ===")
        for brand in no_matches[:10]:
            print(f"  '{brand}'")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    analyze_mikado_brands() 