#!/usr/bin/env python
"""
Детальная диагностика API VintTop.ru (ABCP)
"""
import os
import sys
import hashlib
import requests
import json
from urllib.parse import urljoin

# Добавляем путь к Django проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex.settings')

import django
django.setup()

from catalog.models import Supplier

def test_manual_request():
    """Тестируем запрос вручную"""
    print("🔍 РУЧНОЕ ТЕСТИРОВАНИЕ ЗАПРОСА К ABCP API")
    print("=" * 60)
    
    # Параметры из базы
    login = "autovag@bk.ru"
    password = "0754"
    base_url = "https://id16251.public.api.abcp.ru"
    
    # MD5 пароль
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    print(f"✅ Логин: {login}")
    print(f"✅ Пароль: {password} -> MD5: {password_md5}")
    print(f"✅ Базовый URL: {base_url}")
    print()
    
    # Тест 1: Проверка /search/brands/
    print("🧪 ТЕСТ 1: /search/brands/")
    print("-" * 40)
    
    brands_url = urljoin(base_url, "/search/brands/")
    brands_params = {
        'userlogin': login,
        'userpsw': password_md5,
        'format': 'json'
    }
    
    print(f"URL: {brands_url}")
    print(f"Параметры: {brands_params}")
    print()
    
    try:
        response = requests.get(brands_url, params=brands_params, timeout=30)
        print(f"HTTP Статус: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("❌ Ответ не является валидным JSON")
        print()
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        print()
    
    # Тест 2: Проверка /cp/user/
    print("🧪 ТЕСТ 2: /cp/user/ (информация о пользователе)")
    print("-" * 40)
    
    user_url = urljoin(base_url, "/cp/user/")
    user_params = {
        'userlogin': login,
        'userpsw': password_md5,
        'format': 'json'
    }
    
    print(f"URL: {user_url}")
    print(f"Параметры: {user_params}")
    print()
    
    try:
        response = requests.get(user_url, params=user_params, timeout=30)
        print(f"HTTP Статус: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("❌ Ответ не является валидным JSON")
        print()
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        print()
    
    # Тест 3: Проверка без MD5 (возможно, они принимают обычный пароль)
    print("🧪 ТЕСТ 3: /search/brands/ БЕЗ MD5")
    print("-" * 40)
    
    brands_params_plain = {
        'userlogin': login,
        'userpsw': password,  # Без MD5
        'format': 'json'
    }
    
    print(f"URL: {brands_url}")
    print(f"Параметры: {brands_params_plain}")
    print()
    
    try:
        response = requests.get(brands_url, params=brands_params_plain, timeout=30)
        print(f"HTTP Статус: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print("❌ Ответ не является валидным JSON")
        print()
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        print()
    
    # Тест 4: Попробуем другие возможные логины
    print("🧪 ТЕСТ 4: Альтернативные логины")
    print("-" * 40)
    
    alternative_logins = [
        "Autovag@bk.ru",  # С заглавной буквы
        "autovag@bk.ru",  # Весь в нижнем регистре
        "AUTOVAG@BK.RU",  # Весь в верхнем регистре
    ]
    
    for alt_login in alternative_logins:
        print(f"Тестируем логин: {alt_login}")
        alt_params = {
            'userlogin': alt_login,
            'userpsw': password_md5,
            'format': 'json'
        }
        
        try:
            response = requests.get(brands_url, params=alt_params, timeout=10)
            print(f"  HTTP Статус: {response.status_code}")
            if response.status_code != 200:
                print(f"  Ответ: {response.text[:200]}")
            else:
                print(f"  ✅ Успешно!")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        print()

def test_supplier_methods():
    """Тестируем методы Supplier"""
    print("🧪 ТЕСТИРОВАНИЕ МЕТОДОВ SUPPLIER")
    print("=" * 60)
    
    try:
        supplier = Supplier.objects.get(name="VintTop.ru")
        print(f"✅ Найден поставщик: {supplier.name}")
        print()
        
        # Тест подключения
        print("🔗 Тест подключения...")
        is_connected, message = supplier.test_api_connection()
        print(f"Результат: {is_connected}")
        print(f"Сообщение: {message}")
        print()
        
        # Тест поиска по артикулу
        print("🔍 Тест поиска по артикулу 'NGK'...")
        try:
            results = supplier.search_products_by_article("NGK")
            print(f"Результаты: {results}")
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
        print()
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")

if __name__ == "__main__":
    print("🚀 ДЕТАЛЬНАЯ ДИАГНОСТИКА API VINTTOP")
    print("=" * 60)
    print()
    
    test_manual_request()
    test_supplier_methods()
    
    print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА")
