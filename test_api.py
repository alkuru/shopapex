import requests
import json

# Тестируем FastAPI напрямую
url = "http://localhost:8001/search?article=K1311A"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Статус:", data.get('status'))
    print("Количество товаров:", len(data.get('data', [])))
    
    # Показываем все уникальные склады
    warehouses = set()
    for item in data.get('data', []):
        warehouse = item.get('warehouse', '').strip()
        if warehouse:
            warehouses.add(warehouse)
    
    print("Все склады:", sorted(warehouses))
    
    # Показываем первые 3 товара
    print("\nПервые 3 товара:")
    for i, item in enumerate(data.get('data', [])[:3]):
        print(f"{i+1}. Артикул: {item.get('article')}, Склад: '{item.get('warehouse')}', Наличие: {item.get('availability')}")
else:
    print("Ошибка:", response.status_code, response.text) 