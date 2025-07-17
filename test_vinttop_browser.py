#!/usr/bin/env python
"""
Тестирование API vinttop.ru с симуляцией браузера
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

def test_api_with_browser_headers():
    """Тестирование API с заголовками браузера"""
    
    api_url = "http://178.208.92.49"
    login = "autovag@bk.ru"
    password = "0754"
    
    # Заголовки для симуляции браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print("🌐 ТЕСТИРОВАНИЕ API С ЗАГОЛОВКАМИ БРАУЗЕРА")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"Логин: {login}")
    
    # Тест 1: Базовый запрос с заголовками браузера
    print(f"\n🔧 ТЕСТ 1: Запрос с User-Agent браузера")
    try:
        response = requests.get(
            api_url,
            headers=headers,
            auth=HTTPBasicAuth(login, password),
            timeout=10
        )
        print(f"✅ Статус код: {response.status_code}")
        print(f"✅ Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        content = response.text
        print(f"✅ Размер ответа: {len(content)} символов")
        
        # Проверяем, есть ли признаки API
        if 'json' in response.headers.get('content-type', '').lower():
            try:
                json_data = response.json()
                print(f"✅ JSON успешно распарсен: {str(json_data)[:200]}...")
            except:
                print(f"⚠️  Не удалось распарсить JSON")
        elif 'robot check' in content.lower():
            print(f"⚠️  Все еще получаем Robot Check")
        else:
            print(f"✅ Получили другой контент (первые 200 символов):")
            print(f"   {content[:200]}...")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Попробуем создать сессию (имитация полноценного браузера)
    print(f"\n🔧 ТЕСТ 2: Использование сессии")
    try:
        session = requests.Session()
        session.headers.update(headers)
        session.auth = HTTPBasicAuth(login, password)
        
        # Сначала получим главную страницу
        response = session.get(api_url, timeout=10)
        print(f"✅ Первый запрос - статус: {response.status_code}")
        
        # Попробуем найти возможные API эндпоинты в HTML
        content = response.text.lower()
        api_indicators = ['api', 'json', 'ajax', 'webservice', 'service']
        
        found_indicators = []
        for indicator in api_indicators:
            if indicator in content:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"✅ Найдены API индикаторы: {', '.join(found_indicators)}")
        else:
            print(f"⚠️  API индикаторы не найдены")
            
        # Попробуем различные API эндпоинты с сессией
        api_endpoints = [
            '/api.php',
            '/webservice.php', 
            '/service.php',
            '/ajax.php',
            '/rest.php',
            '/api/v1',
            '/ws',
            '/webservice'
        ]
        
        print(f"\n🔍 Проверка API эндпоинтов с сессией:")
        for endpoint in api_endpoints:
            full_url = api_url + endpoint
            try:
                resp = session.get(full_url, timeout=5)
                content_type = resp.headers.get('content-type', '')
                
                if resp.status_code == 200:
                    if 'json' in content_type.lower():
                        print(f"   ✅ {endpoint}: JSON API найден!")
                        try:
                            json_data = resp.json()
                            print(f"      Данные: {str(json_data)[:100]}...")
                        except:
                            print(f"      Не удалось распарсить JSON")
                    elif resp.status_code != 404:
                        print(f"   ⚠️  {endpoint}: статус {resp.status_code}, тип {content_type}")
                elif resp.status_code == 404:
                    print(f"   ❌ {endpoint}: не найден")
                else:
                    print(f"   ⚠️  {endpoint}: статус {resp.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ {endpoint}: тайм-аут")
            except Exception as e:
                print(f"   ❌ {endpoint}: ошибка {e}")
        
    except Exception as e:
        print(f"❌ Ошибка с сессией: {e}")
    
    # Тест 3: Попробуем POST запросы (возможно, API работает только через POST)
    print(f"\n🔧 ТЕСТ 3: POST запросы для API")
    
    post_data = {
        'action': 'test',
        'method': 'ping'
    }
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            auth=HTTPBasicAuth(login, password),
            data=post_data,
            timeout=10
        )
        print(f"✅ POST статус: {response.status_code}")
        print(f"✅ POST Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if 'json' in response.headers.get('content-type', '').lower():
            try:
                json_data = response.json()
                print(f"✅ POST JSON: {str(json_data)[:200]}...")
            except:
                print(f"⚠️  POST: не удалось распарсить JSON")
        else:
            content = response.text[:200]
            print(f"✅ POST контент: {content}...")
            
    except Exception as e:
        print(f"❌ POST ошибка: {e}")

if __name__ == "__main__":
    test_api_with_browser_headers()
