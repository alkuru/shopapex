#!/usr/bin/env python
"""
Детальное тестирование подключения к API vinttop.ru
"""
import os
import sys
import django
import requests
import json

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_different_endpoints():
    """Тестирует различные варианты подключения к API"""
    
    # Параметры подключения
    host = "46.226.167.12"
    login = "autovag@bk.ru"
    password = "0754"
    
    # Различные варианты URL и портов
    test_configs = [
        {"url": f"http://{host}", "desc": "HTTP порт 80"},
        {"url": f"https://{host}", "desc": "HTTPS порт 443"},
        {"url": f"http://{host}:8080", "desc": "HTTP порт 8080"},
        {"url": f"http://{host}:3000", "desc": "HTTP порт 3000"},
        {"url": f"http://{host}:5000", "desc": "HTTP порт 5000"},
        {"url": f"http://{host}:8000", "desc": "HTTP порт 8000"},
    ]
    
    # Различные endpoint'ы для тестирования
    endpoints = [
        "/",
        "/api",
        "/panel",
        "/panel/order/status",
        "/panel/parts/search/test",
        "/status",
        "/health",
    ]
    
    print("🔍 Тестирование различных вариантов подключения к vinttop.ru")
    print("=" * 70)
    
    for config in test_configs:
        base_url = config["url"]
        description = config["desc"]
        
        print(f"\n📡 Тестирую {description}: {base_url}")
        print("-" * 50)
        
        for endpoint in endpoints:
            test_url = base_url + endpoint
            
            try:
                # Тест без авторизации
                print(f"   🔗 {endpoint:<25} ", end="")
                
                response = requests.get(test_url, timeout=5)
                status = response.status_code
                
                if status == 200:
                    print(f"✅ {status} - OK")
                    try:
                        data = response.json()
                        if isinstance(data, dict) and len(str(data)) < 200:
                            print(f"      📄 Ответ: {data}")
                    except:
                        content = response.text[:100]
                        if content.strip():
                            print(f"      📄 Контент: {content}...")
                            
                elif status == 401:
                    print(f"🔐 {status} - Требуется авторизация")
                    
                    # Попробуем с авторизацией
                    try:
                        auth_response = requests.get(test_url, auth=(login, password), timeout=5)
                        auth_status = auth_response.status_code
                        
                        if auth_status == 200:
                            print(f"      ✅ С авторизацией: {auth_status} - OK")
                            try:
                                auth_data = auth_response.json()
                                if isinstance(auth_data, dict) and len(str(auth_data)) < 200:
                                    print(f"      📄 Данные: {auth_data}")
                            except:
                                auth_content = auth_response.text[:100]
                                if auth_content.strip():
                                    print(f"      📄 Контент: {auth_content}...")
                        else:
                            print(f"      ❌ С авторизацией: {auth_status}")
                            
                    except Exception as e:
                        print(f"      ❌ Ошибка авторизации: {str(e)[:50]}")
                        
                elif status in [403, 404, 405]:
                    print(f"⚠️  {status} - Endpoint недоступен")
                    
                elif status in [500, 502, 503]:
                    print(f"🔥 {status} - Ошибка сервера")
                    
                else:
                    print(f"❓ {status} - Неизвестный статус")
                    
            except requests.exceptions.ConnectTimeout:
                print(f"⏱️  Таймаут подключения")
                
            except requests.exceptions.ConnectionError as e:
                if "Connection refused" in str(e) or "10061" in str(e):
                    print(f"🚫 Соединение отклонено")
                else:
                    print(f"❌ Ошибка соединения: {str(e)[:30]}")
                    
            except requests.exceptions.SSLError:
                print(f"🔒 Ошибка SSL/TLS")
                
            except Exception as e:
                print(f"❌ Ошибка: {str(e)[:30]}")
    
    print("\n" + "=" * 70)
    print("🔧 Тестирование альтернативных методов авторизации")
    print("=" * 70)
    
    # Тестируем возможные рабочие URL с разными методами авторизации
    working_configs = [
        f"http://{host}",
        f"http://{host}:8080",
        f"https://{host}",
    ]
    
    test_endpoints = [
        "/panel/order/status",
        "/api/order/status", 
        "/order/status",
        "/status",
    ]
    
    for base_url in working_configs:
        print(f"\n📡 Тестирую авторизацию для: {base_url}")
        print("-" * 50)
        
        for endpoint in test_endpoints:
            test_url = base_url + endpoint
            print(f"   🔗 {endpoint:<20} ", end="")
            
            # Метод 1: Basic Auth
            try:
                response = requests.get(test_url, auth=(login, password), timeout=5)
                if response.status_code == 200:
                    print(f"✅ Basic Auth работает!")
                    try:
                        data = response.json()
                        print(f"      📄 Данные: {data}")
                        break
                    except:
                        pass
                        
            except:
                pass
            
            # Метод 2: POST с данными
            try:
                post_data = {"login": login, "password": password}
                response = requests.post(test_url, data=post_data, timeout=5)
                if response.status_code == 200:
                    print(f"✅ POST данные работают!")
                    break
                    
            except:
                pass
                
            # Метод 3: Headers
            try:
                headers = {"Authorization": f"Basic {login}:{password}"}
                response = requests.get(test_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Header авторизация работает!")
                    break
                    
            except:
                pass
                
            print(f"❌ Не удалось подключиться")

if __name__ == "__main__":
    test_different_endpoints()
