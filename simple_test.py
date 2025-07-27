#!/usr/bin/env python3
"""
Простой тест - проверяем, что теперь показываются товары из обоих источников
"""

import requests

def test_simple():
    print("=== ПРОСТОЙ ТЕСТ ===")
    
    # Тестируем артикул CA31110 (который есть в AutoKontinent)
    article = "CA31110"
    
    print(f"Тестируем артикул: {article}")
    
    # 1. Проверяем FastAPI
    print("\n1. FastAPI unified_search:")
    try:
        response = requests.get("http://fastapi:8001/unified_search", params={"article": article}, timeout=10)
        data = response.json()
        
        if data.get('status') == 'ok':
            results = data.get('data', [])
            print(f"   Найдено товаров: {len(results)}")
            
            ak_count = sum(1 for item in results if item.get('source') == 'autokontinent_db')
            sp_count = sum(1 for item in results if item.get('source') == 'autosputnik')
            
            print(f"   AutoKontinent: {ak_count}")
            print(f"   AutoSputnik: {sp_count}")
            
            # Показываем все товары
            for i, item in enumerate(results):
                print(f"   {i+1}. {item['article']} | {item['brand']} | {item['source']} | {item['price']}")
        else:
            print(f"   Ошибка: {data.get('message')}")
            
    except Exception as e:
        print(f"   Ошибка FastAPI: {e}")
    
    # 2. Проверяем Django web
    print("\n2. Django web search:")
    try:
        response = requests.get("http://web:8000/catalog/search/", params={"q": article}, timeout=10)
        print(f"   Статус: {response.status_code}")
        
        # Считаем упоминания
        ak_mentions = response.text.count('ЦС АК') + response.text.count('ЦС АКМСК')
        sp_mentions = response.text.count('AutoSputnik')
        article_mentions = response.text.count(article)
        
        print(f"   Упоминаний {article}: {article_mentions}")
        print(f"   Упоминаний AutoKontinent: {ak_mentions}")
        print(f"   Упоминаний AutoSputnik: {sp_mentions}")
        
    except Exception as e:
        print(f"   Ошибка Django: {e}")
    
    print("\n=== РЕЗУЛЬТАТ ===")
    if sp_count > 0:
        print("✅ УСПЕХ: Теперь показываются товары из AutoSputnik!")
    else:
        print("❌ ПРОБЛЕМА: Товары AutoSputnik не показываются")

if __name__ == "__main__":
    test_simple()
