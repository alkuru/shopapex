import os
import django
import json
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def create_complete_mapping():
    """Создание полного маппинга брендов Mikado"""
    print("=== СОЗДАНИЕ ПОЛНОГО МАППИНГА БРЕНДОВ MIKADO ===")
    
    # Основные правильные маппинги
    correct_mappings = {
        # Zimmermann
        'Zimmermann': 'Otto Zimmermann',
        'ZIMMERMANN': 'Otto Zimmermann',
        
        # Victor Reinz
        'Victor Reinz': 'REINZ',
        'VICTOR REINZ': 'REINZ',
        'VictorReinz': 'REINZ',
        
        # Другие важные маппинги
        'MANN-FILTER': 'MANN-FILTER',
        'Mann': 'MANN-FILTER',
        'Mannol': 'Mannol',
        'Febi': 'Febi',
        'Febi Bilstein': 'Febi',
        'FEBI BILSTEIN': 'Febi',
        'Liqui Moly': 'Liqui Moly',
        'LIQUI MOLY': 'Liqui Moly',
        'LIQUI MOLLY': 'Liqui Moly',
        'NGK': 'NGK',
        'Bosch': 'Bosch',
        'BOSCH': 'Bosch',
        'Sachs': 'Sachs',
        'SACHS': 'Sachs',
        'Brembo': 'Brembo',
        'BREMBO': 'Brembo',
        'TRW': 'TRW',
        'Textar': 'Textar',
        'TEXTAR': 'Textar',
        'ATE': 'ATE',
        'Ate': 'ATE',
        'Valeo': 'Valeo',
        'VALEO': 'Valeo',
        'Continental': 'Continental',
        'CONTINENTAL': 'Continental',
        'Mahle': 'Knecht/Mahle',
        'MAHLE': 'Knecht/Mahle',
        'Knecht': 'Knecht/Mahle',
        'KNECHT': 'Knecht/Mahle',
        'Filtron': 'Filtron',
        'FILTRON': 'Filtron',
        'Gates': 'Gates',
        'GATES': 'Gates',
        'Dayco': 'Dayco',
        'DAYCO': 'Dayco',
        'SKF': 'SKF',
        'Skf': 'SKF',
        'FAG': 'FAG',
        'Fag': 'FAG',
        'INA': 'INA',
        'Ina': 'INA',
        'NTN': 'NTN',
        'Ntn': 'NTN',
        'NSK': 'NSK',
        'Nsk': 'NSK',
        'Timken': 'Timken',
        'TIMKEN': 'Timken',
        'Lemforder': 'LEMFÖRDER',
        'LEMFORDER': 'LEMFÖRDER',
        'LEMFÖRDER': 'LEMFÖRDER',
        'Lemförder': 'LEMFÖRDER',
        'Monroe': 'Monroe',
        'MONROE': 'Monroe',
        'Bilstein': 'Bilstein',
        'BILSTEIN': 'Bilstein',
        'KYB': 'KYB',
        'Kyb': 'KYB',
        'Mobil': 'Mobiletron',
        'MOBIL': 'Mobiletron',
        'Mobiletron': 'Mobiletron',
        'MOBILETRON': 'Mobiletron',
        'Champion': 'CHAMPION',
        'CHAMPION': 'CHAMPION',
        'Denso': 'Denso',
        'DENSO': 'Denso',
        'Hella': 'Hella',
        'HELLA': 'Hella',
        'Osram': 'Osram',
        'OSRAM': 'Osram',
        'Philips': 'Philips',
        'PHILIPS': 'Philips',
        'Magneti Marelli': 'Magneti Marelli',
        'MAGNETI MARELLI': 'Magneti Marelli',
        'Pierburg': 'Pierburg',
        'PIERBURG': 'Pierburg',
        'Swag': 'SWAG',
        'SWAG': 'SWAG',
        'Corteco': 'Corteco',
        'CORTECO': 'Corteco',
        'Elring': 'Elring',
        'ELRING': 'Elring',
        'Goetze': 'Goetze',
        'GOETZE': 'Goetze',
        'REINZ': 'REINZ',
        'Reinz': 'REINZ'
    }
    
    # Получаем все уникальные бренды из базы Mikado
    mikado_brands = list(MikadoProduct.objects.values_list('brand', flat=True).distinct())
    print(f"✅ Найдено {len(mikado_brands)} уникальных брендов в базе Mikado")
    
    # Создаем финальный маппинг
    final_mapping = {}
    
    # Добавляем правильные маппинги
    final_mapping.update(correct_mappings)
    
    # Для брендов, которых нет в маппинге, оставляем как есть
    for brand in mikado_brands:
        if brand not in final_mapping:
            # Для неизвестных брендов - оставляем как есть
            final_mapping[brand] = brand
    
    print(f"✅ Создан финальный маппинг для {len(final_mapping)} брендов")
    
    # Сохраняем маппинг
    with open('mikado_complete_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(final_mapping, f, ensure_ascii=False, indent=2)
    
    print("✅ Маппинг сохранен в mikado_complete_mapping.json")
    
    # Показываем примеры маппинга
    print("\n=== ПРИМЕРЫ МАППИНГА ===")
    for old_brand, new_brand in list(correct_mappings.items())[:10]:
        print(f"'{old_brand}' -> '{new_brand}'")
    
    return final_mapping

if __name__ == "__main__":
    create_complete_mapping() 