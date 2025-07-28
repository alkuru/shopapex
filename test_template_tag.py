#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.template import Template, Context
from catalog.templatetags.brand_extras import brand_highlight

def test_template_tag():
    """Тестирует тег brand_highlight"""
    
    print("🧪 Тестирование тега brand_highlight...")
    
    # Тест 1: Прямой вызов функции
    print("\n1️⃣ Прямой вызов функции:")
    test_brands = ['Mann', 'MANN', 'mann', 'Automann', 'DENCKERMANN']
    for brand in test_brands:
        result = brand_highlight(brand)
        print(f"   '{brand}' -> '{result}'")
    
    # Тест 2: Тег в шаблоне
    print("\n2️⃣ Тег в шаблоне:")
    template_string = """
    {% load brand_extras %}
    <strong class="{{ brand|brand_highlight }}">{{ brand }}</strong>
    """
    template = Template(template_string)
    
    for brand in test_brands:
        context = Context({'brand': brand})
        result = template.render(context)
        print(f"   '{brand}' -> {result}")
    
    # Тест 3: Проверка реальных данных
    print("\n3️⃣ Реальные данные из базы:")
    from catalog.models import AutoKontinentProduct
    
    mann_products = AutoKontinentProduct.objects.filter(brand__iexact='mann')[:3]
    for product in mann_products:
        result = brand_highlight(product.brand)
        print(f"   '{product.brand}' -> '{result}'")

if __name__ == '__main__':
    test_template_tag() 