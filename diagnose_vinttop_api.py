#!/usr/bin/env python
"""
Детальная диагностика API vinttop.ru
"""
import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def test_api_detailed():
    """Детальное тестирование API"""
    
    api_url = "http://178.208.92.49"
    login = "autovag@bk.ru"
    password = "0754"
    
    print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА API")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Логин: {login}")
    print(f"Пароль: {password}")
    
    # Тест 1: Базовое подключение без авторизации
    print(f"\n🔧 ТЕСТ 1: Базовое подключение")
    try:
        response = requests.get(api_url, timeout=10)
        print(f"✅ Статус код: {response.status_code}")
        print(f"✅ Заголовки ответа:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        content = response.text[:500]  # Первые 500 символов
        print(f"✅ Содержимое (первые 500 символов):")
        print(f"   {content}")
        
    except Exception as e:
        print(f"❌ Ошибка базового подключения: {e}")
    
    # Тест 2: Подключение с авторизацией
    print(f"\n🔧 ТЕСТ 2: Подключение с HTTP Basic Auth")
    try:
        response = requests.get(
            api_url, 
            auth=HTTPBasicAuth(login, password),
            timeout=10
        )
        print(f"✅ Статус код: {response.status_code}")
        print(f"✅ Заголовки ответа:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        content = response.text[:500]
        print(f"✅ Содержимое (первые 500 символов):")
        print(f"   {content}")
        
    except Exception as e:
        print(f"❌ Ошибка авторизованного подключения: {e}")
    
    # Тест 3: Попробуем различные эндпоинты
    endpoints = [
        "/",
        "/api",
        "/api/",
        "/search",
        "/api/search",
        "/products", 
        "/api/products",
        "/staff",
        "/api/staff"
    ]
    
    print(f"\n🔧 ТЕСТ 3: Проверка возможных эндпоинтов")
    for endpoint in endpoints:
        full_url = api_url + endpoint
        print(f"\n🔎 Тестируем: {full_url}")
        
        try:
            response = requests.get(
                full_url,
                auth=HTTPBasicAuth(login, password),
                timeout=5
            )
            print(f"   ✅ Статус: {response.status_code}")
            
            # Пробуем определить тип контента
            content_type = response.headers.get('content-type', '')
            print(f"   ✅ Тип контента: {content_type}")
            
            if 'json' in content_type.lower():
                try:
                    json_data = response.json()
                    print(f"   ✅ JSON: {str(json_data)[:100]}...")
                except:
                    print(f"   ⚠️  Не удалось парсить JSON")
            else:
                content = response.text[:100]
                print(f"   ✅ Текст: {content}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Тайм-аут")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    # Тест 4: Проверим методы HTTP
    print(f"\n🔧 ТЕСТ 4: Проверка HTTP методов")
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    
    for method in methods:
        print(f"\n🔎 Тестируем {method}: {api_url}")
        try:
            if method == 'GET':
                response = requests.get(api_url, auth=HTTPBasicAuth(login, password), timeout=5)
            elif method == 'POST':
                response = requests.post(api_url, auth=HTTPBasicAuth(login, password), timeout=5)
            elif method == 'PUT':
                response = requests.put(api_url, auth=HTTPBasicAuth(login, password), timeout=5)
            elif method == 'DELETE':
                response = requests.delete(api_url, auth=HTTPBasicAuth(login, password), timeout=5)
            
            print(f"   ✅ {method} статус: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ {method} ошибка: {e}")

if __name__ == "__main__":
    test_api_detailed()
