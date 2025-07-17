#!/usr/bin/env python
"""
Тестирование различных URL и форматов ABCP API
Проверяем разные варианты базового URL
"""

import os
import sys
import django
import hashlib
import requests
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def md5_hash(text):
    """Создание MD5 хэша для пароля"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def test_url_variant(base_url, login, password, description):
    """Тестирование варианта URL"""
    print(f"\n🔍 {description}")
    print("=" * 50)
    print(f"URL: {base_url}")
    
    # Подготавливаем данные для запроса
    request_data = {
        'userlogin': login,
        'userpsw': md5_hash(password),
        'operation': 'userinfo'
    }
    
    print(f"Параметры: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            base_url,
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
                return True
            except json.JSONDecodeError:
                print(f"⚠️ Ответ не в формате JSON:")
                print(f"Содержимое: {response.text[:500]}...")
                return False
        else:
            print(f"❌ Ошибка HTTP {response.status_code}")
            print(f"Содержимое ответа: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False

def main():
    print("🚀 ТЕСТИРОВАНИЕ РАЗЛИЧНЫХ URL ABCP API")
    print("=" * 60)
    
    # Получаем поставщика
    try:
        supplier = Supplier.objects.get(name="VintTop.ru")
        login = supplier.api_login
        password = supplier.api_password
        print(f"✅ Найден поставщик: {supplier.name}")
        print(f"   Логин: {login}")
        print(f"   Пароль (MD5): {md5_hash(password)}")
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return
    
    # Различные варианты URL для тестирования
    url_variants = [
        "https://id16251.public.api.abcp.ru",           # Текущий URL
        "https://id16251.api.abcp.ru",                  # Без public
        "https://api.abcp.ru/id16251",                  # Другая структура
        "https://abcp.ru/api/id16251",                  # Еще вариант
        "https://id16251.abcp.ru/api",                  # Субдомен
        "https://vinttop.ru/api/abcp",                  # Через vinttop.ru
    ]
    
    success_count = 0
    
    for i, url in enumerate(url_variants, 1):
        success = test_url_variant(
            url, 
            login, 
            password, 
            f"ВАРИАНТ {i}: {url}"
        )
        if success:
            success_count += 1
    
    print(f"\n🎯 РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    print(f"Протестировано URL: {len(url_variants)}")
    print(f"Успешных подключений: {success_count}")
    
    if success_count == 0:
        print("\n❌ НИ ОДИН URL НЕ РАБОТАЕТ!")
        print("💡 Возможные причины:")
        print("   1. Аккаунт не активирован для API")
        print("   2. Неправильные учетные данные")
        print("   3. IP адрес не добавлен в белый список")
        print("   4. API временно недоступно")
        print("   5. Требуется другой формат авторизации")
        print("\n📞 Рекомендация: Обратиться в техподдержку VintTop.ru")

if __name__ == "__main__":
    main()
