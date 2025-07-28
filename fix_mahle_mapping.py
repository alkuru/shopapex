#!/usr/bin/env python3
"""
Скрипт для исправления маппинга Mahle
"""

import json

def fix_mahle_mapping():
    """Исправляет маппинг Mahle на Knecht/Mahle"""
    try:
        # Загружаем текущий маппинг
        with open('brand_analysis_results.json', 'r', encoding='utf-8') as f:
            brand_mapping = json.load(f)
        
        print("Исправляем маппинг Mahle...")
        
        # Исправляем Mahle
        if "Mahle" in brand_mapping:
            brand_mapping["Mahle"] = "Knecht/Mahle"
            print("✓ Mahle -> Knecht/Mahle")
        
        # Исправляем Mahle kolben
        if "Mahle kolben" in brand_mapping:
            brand_mapping["Mahle kolben"] = "Knecht/Mahle"
            print("✓ Mahle kolben -> Knecht/Mahle")
        
        # Сохраняем исправленный маппинг
        with open('brand_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(brand_mapping, f, ensure_ascii=False, indent=2)
        
        print("Маппинг исправлен и сохранен!")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    fix_mahle_mapping() 