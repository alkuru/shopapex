#!/usr/bin/env python
"""
Детальная диагностика запросов к ABCP API
Проверяем различные параметры и форматы запросов
"""

import os
import sys
import django
import hashlib
import requests
import json
from urllib.parse import urljoin

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def md5_hash(text):
    """Создание MD5 хэша для пароля"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def test_abcp_request(supplier, endpoint, params, description):
    """Тестирование запроса к ABCP API"""
    print(f"\n🔍 {description}")
    print("=" * 50)
    
    # Подготавливаем URL
    url = urljoin(supplier.api_url.rstrip('/') + '/', endpoint.lstrip('/'))
    
    # Подготавливаем данные для запроса
    request_data = {
        'userlogin': supplier.api_login,
        'userpsw': md5_hash(supplier.api_password),
        **params
    }
    
    print(f"URL: {url}")
    print(f"Параметры: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            url,
            data=request_data,
            timeout=30,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'ShopApex/1.0'
            }
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Успешный ответ:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return True, data
            except json.JSONDecodeError:
                print(f"⚠️ Ответ не в формате JSON:")
                print(f"Содержимое: {response.text[:500]}...")
                return False, response.text
        else:
            print(f"❌ Ошибка HTTP {response.status_code}")
            print(f"Содержимое ответа: {response.text}")
            return False, None
            
    except requests.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False, None

def main():
    print("🚀 ДЕТАЛЬНАЯ ДИАГНОСТИКА ABCP API")
    print("=" * 60)
    
    # Получаем поставщика
    try:
        supplier = Supplier.objects.get(name="VintTop.ru")
        print(f"✅ Найден поставщик: {supplier.name}")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Пароль (MD5): {md5_hash(supplier.api_password)}")
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return
    
    # Тест 1: Проверка аутентификации (brands)
    test_abcp_request(
        supplier,
        '/search/brands/',
        {},
        "ТЕСТ 1: Получение списка брендов (проверка аутентификации)"
    )
    
    # Тест 2: Информация о пользователе
    test_abcp_request(
        supplier,
        '/cp/userinfo/',
        {},
        "ТЕСТ 2: Получение информации о пользователе"
    )
    
    # Тест 3: Поиск по артикулу
    test_abcp_request(
        supplier,
        '/search/articles/',
        {
            'number': '0986424558',  # Тестовый артикул Bosch
            'brand': 'BOSCH'
        },
        "ТЕСТ 3: Поиск по артикулу"
    )
    
    # Тест 4: Поиск по артикулу без бренда
    test_abcp_request(
        supplier,
        '/search/articles/',
        {
            'number': '0986424558'
        },
        "ТЕСТ 4: Поиск по артикулу без указания бренда"
    )
    
    # Тест 5: Поиск аналогов
    test_abcp_request(
        supplier,
        '/search/articles/',
        {
            'number': '0986424558',
            'brand': 'BOSCH',
            'use_online_analogs': '1'
        },
        "ТЕСТ 5: Поиск с аналогами"
    )

if __name__ == "__main__":
    main()
