#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.test import RequestFactory
from django.template.loader import render_to_string
from catalog.web_views import product_search

def test_django_view():
    """Тестирует Django view напрямую"""
    
    print("🧪 Тестирование Django view...")
    
    # Создаем тестовый запрос
    factory = RequestFactory()
    request = factory.get('/catalog/search/?q=C15300&brand=Mann')
    
    # Вызываем view
    response = product_search(request)
    
    print(f"   Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        # Получаем HTML
        html_content = response.content.decode('utf-8')
        
        # Ищем бренды Mann
        if 'brand-mann' in html_content:
            print("   ✅ CSS класс 'brand-mann' найден в HTML")
        else:
            print("   ❌ CSS класс 'brand-mann' НЕ найден в HTML")
        
        # Ищем бренд Mann
        if 'Mann' in html_content:
            print("   ✅ Бренд 'Mann' найден в HTML")
        else:
            print("   ❌ Бренд 'Mann' НЕ найден в HTML")
        
        # Сохраняем HTML для анализа
        with open('/tmp/test_search.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("   📄 HTML сохранен в /tmp/test_search.html")
        
    else:
        print(f"   ❌ Ошибка: {response.status_code}")

if __name__ == '__main__':
    test_django_view() 