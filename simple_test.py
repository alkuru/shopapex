#!/usr/bin/env python
"""
Простой тест для проверки endpoint'а
"""
import requests
import json

def test_endpoint():
    url = "http://127.0.0.1:8000/api/product-analogs/test123/"
    
    print(f"Проверяем URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Статус: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Содержимое: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print("Не удалось распарсить JSON")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_endpoint()
