#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_django_api():
    """Тестирует связь Django с FastAPI"""
    
    print("=== Тест связи Django с FastAPI ===\n")
    
    # Тестируем поиск OC47 через веб-интерфейс
    try:
        url = "http://localhost/catalog/search/"
        params = {"q": "OC47", "brand": "Knecht/Mahle"}
        
        print(f"Запрос к Django: {url}")
        print(f"Параметры: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Ищем информацию о складах
            if "ЦС АК СЕВ" in content:
                print("✅ НАЙДЕН 'ЦС АК СЕВ' в ответе Django!")
            else:
                print("❌ 'ЦС АК СЕВ' НЕ найден в ответе Django")
                
            if "ЦС АК" in content:
                print("✅ НАЙДЕН 'ЦС АК' в ответе Django")
            else:
                print("❌ 'ЦС АК' НЕ найден в ответе Django")
                
            # Ищем товар OC47
            if "OC47" in content:
                print("✅ Товар OC47 найден в ответе")
            else:
                print("❌ Товар OC47 НЕ найден в ответе")
                
        else:
            print(f"Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"Ошибка запроса: {e}")

if __name__ == "__main__":
    test_django_api() 