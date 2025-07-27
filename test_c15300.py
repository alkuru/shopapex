#!/usr/bin/env python3
"""
Тестовый скрипт для проверки группировки товаров C15300
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем функцию группировки
from catalog.utils_sputnik import group_offers
import requests

# Получаем реальные данные от API
print("Получаем данные от API для C15300...")
response = requests.get("http://fastapi:8001/unified_search?article=C15300&brand=MANN-FILTER")
data = response.json()
items = data.get('data', [])

print(f"Получено товаров: {len(items)}")

# Тестируем группировку
print("\nТестируем группировку товаров...")
groups = group_offers(items)

print(f"Количество групп: {len(groups)}")
for i, group in enumerate(groups):
    print(f"\nГруппа {i}:")
    print(f"  Артикул: {group.get('articul')}")
    print(f"  Бренд: {group.get('brand')}")
    print(f"  Видимых товаров: {len(group.get('visible', []))}")
    print(f"  Скрытых товаров: {len(group.get('hidden', []))}")
    print(f"  hidden_shown: {group.get('hidden_shown', 0)}")
    
    if group.get('visible'):
        print("  Видимые товары:")
        for item in group.get('visible', []):
            print(f"    - {item.get('article')} {item.get('brand')} ({item.get('source')}) - {item.get('warehouse')}")
    
    if group.get('hidden'):
        print("  Скрытые товары:")
        for item in group.get('hidden', []):
            print(f"    - {item.get('article')} {item.get('brand')} ({item.get('source')}) - {item.get('warehouse')}")

# Проверяем, сколько товаров C15300
c15300_items = [item for item in items if item.get('article') == 'C15300']
print(f"\nТоваров с артикулом C15300: {len(c15300_items)}")

# Проверяем группу C15300
c15300_group = None
for group in groups:
    if group.get('articul') == 'C15300':
        c15300_group = group
        break

if c15300_group:
    print(f"\nГруппа C15300:")
    print(f"  Видимых товаров: {len(c15300_group.get('visible', []))}")
    print(f"  Скрытых товаров: {len(c15300_group.get('hidden', []))}")
    print(f"  hidden_shown: {c15300_group.get('hidden_shown', 0)}")
    print(f"  Всего товаров в группе: {len(c15300_group.get('visible', [])) + len(c15300_group.get('hidden', []))}")
else:
    print("\nГруппа C15300 не найдена!") 