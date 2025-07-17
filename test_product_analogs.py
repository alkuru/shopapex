#!/usr/bin/env python
"""
Тестовый скрипт для проверки API поиска аналогов автозапчастей
"""

import requests
import json
import time
import os
import sys
import django

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django окружение
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_product_analogs_api():
    """Тестируем API поиска аналогов"""
    print("🔍 Тестирование API поиска аналогов автозапчастей")
    print("="*60)
    
    # URL для тестирования
    base_url = "http://127.0.0.1:8000"
    api_url = f"{base_url}/catalog/product-analogs/"
    
    # Тестовые артикулы для поиска
    test_articles = [
        "0986452062",  # Тормозные колодки BOSCH
        "BP1518",      # Тормозные колодки BOSCH
        "F026407006",  # Воздушный фильтр BOSCH  
        "1457434310",  # Масляный фильтр BOSCH
        "25-143800"    # Тормозные колодки ATE
    ]
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n{i}. Тестируем поиск аналогов для артикула: {article}")
        print("-" * 50)
        
        # Параметры запроса
        params = {
            'article': article,
            'limit': 10
        }
        
        try:
            # Делаем запрос к API
            response = requests.get(api_url, params=params, timeout=30)
            
            print(f"📡 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Найдено аналогов: {len(data.get('results', []))}")
                print(f"📊 Общее количество: {data.get('count', 0)}")
                
                # Показываем первые несколько результатов
                results = data.get('results', [])[:3]
                for j, analog in enumerate(results, 1):
                    print(f"\n   {j}. {analog.get('brand_name', 'N/A')} - {analog.get('article', 'N/A')}")
                    print(f"      Название: {analog.get('name', 'N/A')}")
                    print(f"      Цена: {analog.get('price', 'N/A')} руб.")
                    print(f"      Наличие: {analog.get('availability', 'N/A')}")
                    print(f"      Поставщик: {analog.get('supplier_name', 'N/A')}")
                
                if len(data.get('results', [])) > 3:
                    print(f"   ... и ещё {len(data.get('results', [])) - 3} аналогов")
                    
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Детали: {error_data}")
                except:
                    print(f"   Текст ошибки: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Таймаут запроса (30 сек)")
        except requests.exceptions.ConnectionError:
            print("🔌 Ошибка подключения к серверу")
        except Exception as e:
            print(f"💥 Неожиданная ошибка: {e}")
        
        # Пауза между запросами
        if i < len(test_articles):
            print("\n⏳ Пауза 2 сек...")
            time.sleep(2)

def test_supplier_method():
    """Тестируем метод поиска аналогов на уровне модели"""
    print("\n\n🧪 Тестирование метода модели Supplier.get_product_analogs")
    print("="*65)
    
    try:
        # Получаем активного поставщика
        supplier = Supplier.objects.filter(is_active=True).first()
        
        if not supplier:
            print("❌ Не найден активный поставщик")
            return
            
        print(f"🏢 Используем поставщика: {supplier.name}")
        
        # Тестовый артикул
        test_article = "0986452062"
        print(f"🔍 Ищем аналоги для артикула: {test_article}")
        
        # Вызываем метод
        result = supplier.get_product_analogs(test_article, limit=5)
        
        if result.get('success'):
            analogs = result.get('analogs', [])
            print(f"✅ Найдено аналогов: {len(analogs)}")
            
            for i, analog in enumerate(analogs[:3], 1):
                print(f"\n   {i}. {analog.get('brand')} - {analog.get('article')}")
                print(f"      Название: {analog.get('name', 'N/A')}")
                print(f"      Цена: {analog.get('price', 'N/A')}")
                print(f"      Наличие: {analog.get('availability', 'N/A')}")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
    except Exception as e:
        print(f"💥 Ошибка при тестировании модели: {e}")

def check_server_status():
    """Проверяем, работает ли сервер"""
    print("🌐 Проверка статуса сервера...")
    
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер работает")
            return True
        else:
            print(f"⚠️ Сервер отвечает с кодом: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не отвечает")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке сервера: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛА ПОИСКА АНАЛОГОВ")
    print("="*60)
    print(f"⏰ Время запуска: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем сервер
    if check_server_status():
        # Тестируем API
        test_product_analogs_api()
        
        # Тестируем метод модели
        test_supplier_method()
        
        print("\n\n🎉 Тестирование завершено!")
        print("="*40)
        print("📝 Результаты можно найти выше")
        print("🔧 При необходимости внесите исправления в код")
    else:
        print("\n❌ Не удалось подключиться к серверу Django")
        print("🚨 Убедитесь, что сервер запущен:")
        print("   python manage.py runserver")
