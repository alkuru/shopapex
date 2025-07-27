#!/usr/bin/env python3
"""
Тестирование артикула CA31110 - проверка отображения товаров из AutoKontinent и AutoSputnik
"""
import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import AutoKontinentProduct

def test_ca31110():
    """
    Тестирует артикул CA31110
    """
    print("=== ТЕСТИРОВАНИЕ АРТИКУЛА CA31110 ===\n")
    
    # Проверяем, есть ли товар в базе AutoKontinent
    try:
        ak_product = AutoKontinentProduct.objects.get(article='CA31110')
        print(f"✅ Найден в AutoKontinent:")
        print(f"   Бренд: {ak_product.brand}")
        print(f"   Название: {ak_product.name}")
        print(f"   Наличие СПб: {ak_product.stock_spb}")
        print(f"   Наличие МСК: {ak_product.stock_msk}")
        print(f"   Цена: {ak_product.price}")
    except AutoKontinentProduct.DoesNotExist:
        print("❌ Товар CA31110 НЕ найден в базе AutoKontinent")
        return
    
    # Тестируем поиск через веб
    print("\n=== ТЕСТИРОВАНИЕ ВЕБ-ПОИСКА ===")
    test_web_search('CA31110', ak_product.brand)

def test_web_search(article, brand):
    """
    Тестирует веб-поиск для конкретного артикула
    """
    try:
        url = "http://web:8000/catalog/search/"
        params = {
            'q': article,
            'brand': brand
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем все товары с этим артикулом
            product_rows = soup.find_all('tr')
            all_products = []
            autokontinent_products = []
            autosputnik_products = []
            
            for row in product_rows:
                cells = row.find_all('td')
                if len(cells) >= 7:
                    article_cell = cells[0]
                    warehouse_cell = cells[5]
                    
                    if article_cell and article in article_cell.get_text():
                        all_products.append(row)
                        
                        if warehouse_cell and 'ЦС АК' in warehouse_cell.get_text():
                            autokontinent_products.append(row)
                        elif warehouse_cell and 'сторонний' in warehouse_cell.get_text():
                            autosputnik_products.append(row)
            
            print(f"📊 Статистика поиска:")
            print(f"   Всего товаров {article}: {len(all_products)}")
            print(f"   AutoKontinent товаров: {len(autokontinent_products)}")
            print(f"   AutoSputnik товаров: {len(autosputnik_products)}")
            
            # Показываем все найденные товары
            if all_products:
                print(f"\n📋 Все товары {article} на странице:")
                for i, row in enumerate(all_products, 1):
                    cells = row.find_all('td')
                    if len(cells) >= 7:
                        article_text = cells[0].get_text().strip()
                        brand_text = cells[1].get_text().strip()
                        name_text = cells[2].get_text().strip()
                        availability = cells[3].get_text().strip()
                        delivery_time = cells[4].get_text().strip()
                        warehouse = cells[5].get_text().strip()
                        price = cells[6].get_text().strip()
                        
                        print(f"   {i}. {article_text} {brand_text}")
                        print(f"      {name_text}")
                        print(f"      Наличие: {availability}, Срок: {delivery_time}")
                        print(f"      Склад: {warehouse}, Цена: {price}")
                        print()
            
            # Проверяем порядок товаров
            print(f"🔍 Проверка порядка товаров:")
            if autokontinent_products:
                first_ak = autokontinent_products[0]
                cells = first_ak.find_all('td')
                if len(cells) >= 7:
                    warehouse = cells[5].get_text().strip()
                    print(f"   ✅ Первый AutoKontinent товар: {warehouse}")
            else:
                print(f"   ❌ AutoKontinent товары не найдены")
            
            if autosputnik_products:
                first_as = autosputnik_products[0]
                cells = first_as.find_all('td')
                if len(cells) >= 7:
                    warehouse = cells[5].get_text().strip()
                    print(f"   ✅ Первый AutoSputnik товар: {warehouse}")
            else:
                print(f"   ❌ AutoSputnik товары не найдены")
            
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_without_autokontinent():
    """
    Тестирует поиск после удаления товара из AutoKontinent
    """
    print("\n=== ТЕСТИРОВАНИЕ БЕЗ AUTOKONTINENT ===")
    print("⚠️  ВНИМАНИЕ: Этот тест удалит товар CA31110 из базы AutoKontinent!")
    
    response = input("Продолжить? (y/n): ")
    if response.lower() != 'y':
        print("Тест отменен")
        return
    
    try:
        # Удаляем товар из AutoKontinent
        AutoKontinentProduct.objects.filter(article='CA31110').delete()
        print("✅ Товар CA31110 удален из базы AutoKontinent")
        
        # Тестируем поиск
        test_web_search('CA31110', '')
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    test_ca31110()
    # test_without_autokontinent()  # Раскомментировать для тестирования без AutoKontinent 