#!/usr/bin/env python
"""
Детальная диагностика API id16251.public.api.abcp.ru
"""
import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth
import json

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def diagnose_abcp_api():
    """Детальная диагностика API ABCP"""
    
    api_url = "https://id16251.public.api.abcp.ru"
    login = "autovag@bk.ru"
    password = "0754"
    
    print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА ABCP API")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"Логин: {login}")
    print(f"Пароль: {password}")
    
    # Заголовки для API запросов
    headers = {
        'User-Agent': 'ShopApex/1.0 (AutoParts Integration)',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    }
    
    # Тест 1: Базовое подключение
    print(f"\n🔧 ТЕСТ 1: Базовое подключение")
    try:
        response = requests.get(
            api_url,
            headers=headers,
            auth=HTTPBasicAuth(login, password),
            timeout=10
        )
        print(f"✅ Статус код: {response.status_code}")
        print(f"✅ Заголовки ответа:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print(f"✅ Размер ответа: {len(response.text)} символов")
        
        # Пробуем распарсить JSON
        try:
            json_data = response.json()
            print(f"✅ JSON успешно распарсен:")
            print(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")
        except:
            content = response.text[:500]
            print(f"✅ Текстовый ответ (первые 500 символов):")
            print(f"   {content}")
            
    except Exception as e:
        print(f"❌ Ошибка базового подключения: {e}")
    
    # Тест 2: Попробуем различные эндпоинты ABCP API
    endpoints = [
        "/",
        "/ping", 
        "/test",
        "/status",
        "/brands",
        "/search",
        "/catalogs",
        "/products",
        "/articles",
        "/parts"
    ]
    
    print(f"\n🔧 ТЕСТ 2: Проверка эндпоинтов ABCP API")
    for endpoint in endpoints:
        full_url = api_url + endpoint
        print(f"\n🔎 Тестируем: {endpoint}")
        
        try:
            response = requests.get(
                full_url,
                headers=headers,
                auth=HTTPBasicAuth(login, password),
                timeout=5
            )
            
            print(f"   ✅ Статус: {response.status_code}")
            content_type = response.headers.get('content-type', '')
            print(f"   ✅ Content-Type: {content_type}")
            
            if response.status_code == 200:
                if 'json' in content_type.lower():
                    try:
                        json_data = response.json()
                        print(f"   ✅ JSON: {str(json_data)[:100]}...")
                    except:
                        print(f"   ⚠️  Не удалось распарсить JSON")
                else:
                    content = response.text[:100]
                    print(f"   ✅ Текст: {content}...")
            elif response.status_code == 400:
                print(f"   ⚠️  Bad Request - возможно нужны параметры")
            elif response.status_code == 401:
                print(f"   🔐 Unauthorized - проблемы с авторизацией")
            elif response.status_code == 404:
                print(f"   ❌ Not Found")
            else:
                print(f"   ⚠️  Неожиданный статус")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Тайм-аут")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: POST запросы с параметрами
    print(f"\n🔧 ТЕСТ 3: POST запросы с параметрами")
    
    # Типичные параметры для поиска в ABCP API
    search_params = {
        "number": "0986424815",  # Тестовый артикул
        "type": "article"
    }
    
    try:
        response = requests.post(
            api_url + "/search",
            headers=headers,
            auth=HTTPBasicAuth(login, password),
            json=search_params,
            timeout=10
        )
        
        print(f"✅ POST /search статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ POST JSON результат: {str(json_data)[:200]}...")
            except:
                print(f"⚠️  POST: не удалось распарсить JSON")
        else:
            print(f"⚠️  POST ошибка: {response.status_code}")
            print(f"    Ответ: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ POST ошибка: {e}")
    
    # Тест 4: Попробуем с параметрами в URL
    print(f"\n🔧 ТЕСТ 4: GET с параметрами в URL")
    
    try:
        params = {
            'number': '0986424815',
            'format': 'json'
        }
        
        response = requests.get(
            api_url + "/search",
            headers=headers,
            auth=HTTPBasicAuth(login, password),
            params=params,
            timeout=10
        )
        
        print(f"✅ GET с параметрами статус: {response.status_code}")
        print(f"✅ URL запроса: {response.url}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ GET результат: {str(json_data)[:200]}...")
            except:
                print(f"⚠️  GET: не удалось распарсить JSON")
        else:
            print(f"⚠️  GET ошибка: {response.status_code}")
            print(f"    Ответ: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ GET ошибка: {e}")
    
    print(f"\n📋 РЕКОМЕНДАЦИИ:")
    print(f"1. Если получили 400 - проверьте формат запроса")
    print(f"2. Если получили 401 - проверьте логин/пароль")
    print(f"3. Если получили 200 - API работает, нужно изучить формат ответа")
    print(f"4. Изучите документацию ABCP API для правильных эндпоинтов")

if __name__ == "__main__":
    diagnose_abcp_api()
