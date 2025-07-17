#!/usr/bin/env python
"""
Тестирование базовых операций ABCP API согласно документации
Используем стандартные методы API без /search/ префикса
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

def test_abcp_operation(supplier, operation, params, description):
    """Тестирование операции ABCP API"""
    print(f"\n🔍 {description}")
    print("=" * 50)
    
    # Подготавливаем данные для запроса
    request_data = {
        'userlogin': supplier.api_login,
        'userpsw': md5_hash(supplier.api_password),
        'operation': operation,
        **params
    }
    
    print(f"URL: {supplier.api_url}")
    print(f"Операция: {operation}")
    print(f"Параметры: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            supplier.api_url,
            data=request_data,
            timeout=30,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'ShopApex/1.0'
            }
        )
        
        print(f"Статус: {response.status_code}")
        
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
    print("🚀 ТЕСТИРОВАНИЕ БАЗОВЫХ ОПЕРАЦИЙ ABCP API")
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
    
    # Тест 1: Информация о пользователе
    test_abcp_operation(
        supplier,
        'userinfo',
        {},
        "ТЕСТ 1: Получение информации о пользователе (userinfo)"
    )
    
    # Тест 2: Список брендов
    test_abcp_operation(
        supplier,
        'brands',
        {},
        "ТЕСТ 2: Получение списка брендов (brands)"
    )
    
    # Тест 3: Поиск по артикулу
    test_abcp_operation(
        supplier,
        'articles',
        {
            'number': '0986424558',
            'brand': 'BOSCH'
        },
        "ТЕСТ 3: Поиск по артикулу (articles)"
    )
    
    # Тест 4: Поиск по артикулу без бренда
    test_abcp_operation(
        supplier,
        'articles',
        {
            'number': '0986424558'
        },
        "ТЕСТ 4: Поиск по артикулу без бренда (articles)"
    )
    
    # Тест 5: Поиск детальной информации
    test_abcp_operation(
        supplier,
        'search',
        {
            'number': '0986424558',
            'brand': 'BOSCH'
        },
        "ТЕСТ 5: Поиск детальной информации (search)"
    )

if __name__ == "__main__":
    main()
