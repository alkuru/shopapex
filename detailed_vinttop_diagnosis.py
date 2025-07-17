#!/usr/bin/env python
"""
Детальная диагностика API VintTop.ru с полным логированием запросов
"""
import os
import sys
import django
import requests
import hashlib
import json

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def detailed_api_diagnosis():
    """Детальная диагностика API с полным логированием"""
    
    print("🔍 Получение настроек поставщика...")
    
    try:
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Поставщик: {supplier.name}")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Пароль: {'*' * len(supplier.api_password)}")
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик не найден!")
        return
    
    # Подготавливаем данные для запроса
    login = supplier.api_login
    password = supplier.api_password
    api_url = supplier.api_url
    
    print(f"\n🔧 Подготовка запроса...")
    print(f"   Исходный пароль: {password}")
    
    # Создаем MD5 хэш пароля
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    print(f"   MD5 хэш пароля: {password_hash}")
    
    # Тест 1: Запрос информации о пользователе
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 1: Получение информации о пользователе")
    print(f"="*60)
    
    user_info_url = f"{api_url}/cp/users"
    user_params = {
        'userlogin': login,
        'userpsw': password_hash
    }
    
    print(f"📤 Запрос:")
    print(f"   URL: {user_info_url}")
    print(f"   Параметры: {user_params}")
    
    try:
        response = requests.get(user_info_url, params=user_params, timeout=30)
        print(f"📥 Ответ:")
        print(f"   Статус: {response.status_code}")
        print(f"   Заголовки: {dict(response.headers)}")
        print(f"   Тело ответа: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   JSON данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Не удалось распарсить JSON")
        
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 2: Запрос списка брендов
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 2: Получение списка брендов")
    print(f"="*60)
    
    brands_url = f"{api_url}/search/brands"
    brands_params = {
        'userlogin': login,
        'userpsw': password_hash
    }
    
    print(f"📤 Запрос:")
    print(f"   URL: {brands_url}")
    print(f"   Параметры: {brands_params}")
    
    try:
        response = requests.get(brands_url, params=brands_params, timeout=30)
        print(f"📥 Ответ:")
        print(f"   Статус: {response.status_code}")
        print(f"   Заголовки: {dict(response.headers)}")
        print(f"   Тело ответа: {response.text[:500]}...")  # Первые 500 символов
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Количество брендов: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Первые 3 бренда: {data[:3]}")
            except:
                print(f"   Не удалось распарсить JSON")
        
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 3: Поиск по артикулу
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 3: Поиск по артикулу")
    print(f"="*60)
    
    articles_url = f"{api_url}/search/articles"
    test_article = "0986424815"  # Bosch артикул
    articles_params = {
        'userlogin': login,
        'userpsw': password_hash,
        'number': test_article
    }
    
    print(f"📤 Запрос:")
    print(f"   URL: {articles_url}")
    print(f"   Параметры: {articles_params}")
    
    try:
        response = requests.get(articles_url, params=articles_params, timeout=30)
        print(f"📥 Ответ:")
        print(f"   Статус: {response.status_code}")
        print(f"   Заголовки: {dict(response.headers)}")
        print(f"   Тело ответа: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   JSON данные: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            except:
                print(f"   Не удалось распарсить JSON")
        
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 4: Альтернативные эндпоинты
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 4: Проверка альтернативных эндпоинтов")
    print(f"="*60)
    
    alternative_endpoints = [
        "/api/cp/users",
        "/cp/user",
        "/api/search/brands",
        "/search/brand",
        "/api/brands",
        "/brands"
    ]
    
    for endpoint in alternative_endpoints:
        test_url = f"{api_url}{endpoint}"
        params = {
            'userlogin': login,
            'userpsw': password_hash
        }
        
        print(f"\n🔗 Тестируем: {test_url}")
        try:
            response = requests.get(test_url, params=params, timeout=10)
            print(f"   Статус: {response.status_code}")
            if response.status_code != 404:
                print(f"   Ответ: {response.text[:100]}...")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    print(f"\n" + "="*60)
    print(f"📋 РЕЗЮМЕ ДИАГНОСТИКИ")
    print(f"="*60)
    print(f"✅ Настройки поставщика проверены")
    print(f"✅ MD5 хэширование пароля выполнено") 
    print(f"✅ Запросы к различным эндпоинтам отправлены")
    print(f"📝 Проанализируйте ответы выше для диагностики проблем")

if __name__ == "__main__":
    print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА API VINTTOP.RU")
    print("=" * 60)
    detailed_api_diagnosis()
