import os
import sys
import django
import json

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def normalize_brand(brand_name):
    return str(brand_name).strip().lower().replace(' ', '').replace('-', '').replace('/', '')

def main():
    print("=== ДИАГНОСТИКА БРЕНДОВ MIKADO ===")
    
    # Проверяем общую статистику
    total_products = MikadoProduct.objects.count()
    print(f"Всего товаров Mikado: {total_products}")
    
    if total_products == 0:
        print("❌ В базе нет товаров Mikado!")
        return
    
    # Получаем уникальные бренды
    all_brands = list(MikadoProduct.objects.values_list('brand', flat=True).distinct())
    print(f"Уникальных брендов: {len(all_brands)}")
    
    print("\n=== ПЕРВЫЕ 20 БРЕНДОВ ===")
    for i, brand in enumerate(all_brands[:20]):
        count = MikadoProduct.objects.filter(brand=brand).count()
        print(f"{i+1:2d}. '{brand}' ({count} товаров)")
    
    # Проверяем маппинг
    print("\n=== ПРОВЕРКА МАППИНГА ===")
    
    # Загружаем brand_analysis_results.json
    mapping_file = 'brand_analysis_results.json'
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            brand_data = json.load(f)
        
        # Создаем маппинг
        brand_mapping = {}
        for item in brand_data.get('exact_matches', []):
            if item.get('autokontinent') and item.get('autosputnik'):
                old_norm = normalize_brand(item['autokontinent'])
                brand_mapping[old_norm] = item['autosputnik']
        
        # Добавляем специальные маппинги
        special_mappings = {
            normalize_brand('Mahle'): 'Knecht/Mahle',
            normalize_brand('Mahle kolben'): 'Knecht/Mahle', 
            normalize_brand('Knecht'): 'Knecht/Mahle',
            normalize_brand('Mann'): 'MANN-FILTER',
            normalize_brand('Mann-Filter'): 'MANN-FILTER',
            normalize_brand('Bosch'): 'BOSCH',
            normalize_brand('Filtron'): 'FILTRON',
            normalize_brand('Sakura'): 'Sakura',
            normalize_brand('Fram'): 'FRAM',
        }
        brand_mapping.update(special_mappings)
        
        print(f"Загружено маппингов: {len(brand_mapping)}")
        
        # Проверяем какие бренды Mikado могут быть обновлены
        matches_found = 0
        for brand in all_brands[:10]:  # Проверяем первые 10
            brand_norm = normalize_brand(brand)
            
            # Проверяем точное соответствие
            if brand_norm in brand_mapping:
                new_brand = brand_mapping[brand_norm]
                count = MikadoProduct.objects.filter(brand=brand).count()
                print(f"✅ '{brand}' -> '{new_brand}' ({count} товаров)")
                matches_found += 1
            else:
                # Проверяем частичные совпадения
                partial_match = None
                for norm_key, mapped_brand in brand_mapping.items():
                    if norm_key in brand_norm or brand_norm in norm_key:
                        partial_match = mapped_brand
                        break
                
                if partial_match:
                    count = MikadoProduct.objects.filter(brand=brand).count()
                    print(f"🔶 '{brand}' -> '{partial_match}' (частичное, {count} товаров)")
                    matches_found += 1
                else:
                    count = MikadoProduct.objects.filter(brand=brand).count()
                    print(f"❌ '{brand}' - соответствие не найдено ({count} товаров)")
        
        print(f"\nНайдено соответствий: {matches_found}")
        
    else:
        print("❌ Файл brand_analysis_results.json не найден!")
    
    print("\n=== НОРМАЛИЗОВАННЫЕ БРЕНДЫ ===")
    for brand in all_brands[:10]:
        norm = normalize_brand(brand)
        print(f"'{brand}' -> '{norm}'")

if __name__ == '__main__':
    main() 