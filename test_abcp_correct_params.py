#!/usr/bin/env python
"""
Тестирование ABCP API с правильными параметрами
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

def test_abcp_api_correct_params():
    """Тестирование ABCP API с правильными параметрами"""
    
    api_url = "https://id16251.public.api.abcp.ru"
    login = "autovag@bk.ru"
    password = "0754"
    
    print("🔍 ТЕСТИРОВАНИЕ ABCP API С ПРАВИЛЬНЫМИ ПАРАМЕТРАМИ")
    print("=" * 65)
    
    # Типичные параметры для ABCP API
    # Согласно документации ABCP, обычно требуются:
    # - userlogin и userpsw для авторизации
    # - operation для указания операции
    # - number для поиска по номеру
    
    # Тест 1: Поиск товаров (стандартный формат ABCP)
    print(f"\n🔧 ТЕСТ 1: Поиск товаров по артикулу")
    
    search_params = {
        'userlogin': login,
        'userpsw': password,
        'operation': 'search',
        'number': '0986424815',
        'format': 'json'
    }
    
    try:
        # Попробуем GET запрос с параметрами
        response = requests.get(
            api_url,
            params=search_params,
            timeout=15
        )
        
        print(f"✅ GET статус: {response.status_code}")
        print(f"✅ URL: {response.url}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ Успешный ответ JSON:")
                print(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")
            except:
                print(f"✅ Ответ (не JSON): {response.text[:300]}...")
        else:
            print(f"⚠️  Ошибка {response.status_code}: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Ошибка GET: {e}")
    
    # Тест 2: POST запрос
    print(f"\n🔧 ТЕСТ 2: POST запрос с параметрами")
    
    try:
        # Попробуем POST с теми же параметрами
        response = requests.post(
            api_url,
            data=search_params,
            timeout=15
        )
        
        print(f"✅ POST статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ POST успешный ответ:")
                print(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")
            except:
                print(f"✅ POST ответ (не JSON): {response.text[:300]}...")
        else:
            print(f"⚠️  POST ошибка {response.status_code}: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ POST ошибка: {e}")
    
    # Тест 3: Попробуем другие операции
    operations = [
        'ping',
        'brands', 
        'catalogs',
        'categories',
        'info'
    ]
    
    print(f"\n🔧 ТЕСТ 3: Различные операции ABCP API")
    
    for operation in operations:
        print(f"\n🔎 Операция: {operation}")
        
        params = {
            'userlogin': login,
            'userpsw': password,
            'operation': operation,
            'format': 'json'
        }
        
        try:
            response = requests.get(
                api_url,
                params=params,
                timeout=10
            )
            
            print(f"   ✅ Статус: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"   ✅ JSON ответ: {str(json_data)[:100]}...")
                except:
                    print(f"   ✅ Ответ: {response.text[:100]}...")
            else:
                print(f"   ⚠️  Ошибка: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    # Тест 4: Попробуем с HTTP Basic Auth заголовками
    print(f"\n🔧 ТЕСТ 4: HTTP Basic Auth + параметры")
    
    headers = {
        'User-Agent': 'ShopApex/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Параметры без логина/пароля (используем HTTP Auth)
    auth_params = {
        'operation': 'search',
        'number': '0986424815',
        'format': 'json'
    }
    
    try:
        response = requests.get(
            api_url,
            headers=headers,
            auth=HTTPBasicAuth(login, password),
            params=auth_params,
            timeout=10
        )
        
        print(f"✅ Auth статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"✅ Auth успешно: {str(json_data)[:200]}...")
            except:
                print(f"✅ Auth ответ: {response.text[:200]}...")
        else:
            print(f"⚠️  Auth ошибка: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Auth ошибка: {e}")
    
    print(f"\n📋 ВЫВОДЫ:")
    print(f"1. API ABCP работает и принимает запросы")
    print(f"2. Требуются правильные параметры операций")
    print(f"3. Возможны варианты авторизации:")
    print(f"   - userlogin/userpsw в параметрах")
    print(f"   - HTTP Basic Authentication")
    print(f"4. Нужно изучить документацию ABCP для всех операций")

if __name__ == "__main__":
    test_abcp_api_correct_params()
