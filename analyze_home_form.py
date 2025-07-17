#!/usr/bin/env python
"""
Анализ HTML формы поиска на главной странице
"""
import os
import django
import requests
from bs4 import BeautifulSoup
import re

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def analyze_home_page_form():
    """Детальный анализ формы поиска на главной странице"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Анализ формы поиска на главной странице ===\n")
    
    try:
        response = requests.get(base_url + "/")
        if response.status_code != 200:
            print(f"❌ Ошибка загрузки главной страницы: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем все формы
        forms = soup.find_all('form')
        print(f"Найдено форм на главной странице: {len(forms)}\n")
        
        for i, form in enumerate(forms, 1):
            print(f"--- Форма {i} ---")
            
            # Атрибуты формы
            method = form.get('method', 'get')
            action = form.get('action', '')
            css_class = form.get('class', [])
            
            print(f"Метод: {method}")
            print(f"Action: {action}")
            print(f"CSS классы: {css_class}")
            
            # Все поля ввода
            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"Полей ввода: {len(inputs)}")
            
            for j, inp in enumerate(inputs, 1):
                tag_name = inp.name
                input_type = inp.get('type', 'text')
                input_name = inp.get('name', '')
                input_value = inp.get('value', '')
                placeholder = inp.get('placeholder', '')
                
                print(f"  Поле {j}: <{tag_name} type='{input_type}' name='{input_name}' value='{input_value}' placeholder='{placeholder}'>")
            
            # Кнопки
            buttons = form.find_all(['button', 'input[type="submit"]'])
            print(f"Кнопок: {len(buttons)}")
            
            for j, btn in enumerate(buttons, 1):
                btn_type = btn.get('type', '')
                btn_text = btn.get_text(strip=True) if btn.name == 'button' else btn.get('value', '')
                print(f"  Кнопка {j}: type='{btn_type}' text='{btn_text}'")
            
            print()
        
        # Проверяем конкретную форму поиска товаров
        search_form = None
        for form in forms:
            # Ищем форму с полем name="q"
            q_input = form.find('input', {'name': 'q'})
            if q_input:
                search_form = form
                break
        
        if search_form:
            print("--- Детальный анализ формы поиска товаров ---")
            action = search_form.get('action', '')
            method = search_form.get('method', 'get')
            
            print(f"Action URL: {action}")
            print(f"Метод: {method}")
            
            # Проверяем, является ли action правильным URL
            if action.startswith('/catalog/search'):
                print("✅ Action URL правильный")
            elif 'catalog' in action and 'search' in action:
                print("⚠️  Action URL содержит правильные части, но может быть неточным")
            else:
                print("❌ Action URL неправильный")
            
            # Проверяем метод
            if method.lower() == 'get':
                print("✅ Метод GET правильный для поиска")
            else:
                print(f"⚠️  Метод {method} может быть проблемой")
            
            # Проверяем поле поиска
            q_input = search_form.find('input', {'name': 'q'})
            if q_input:
                print("✅ Поле 'q' найдено")
                input_type = q_input.get('type', 'text')
                if input_type == 'text':
                    print("✅ Тип поля 'text' правильный")
                else:
                    print(f"⚠️  Тип поля '{input_type}' может быть проблемой")
            else:
                print("❌ Поле 'q' НЕ найдено")
        else:
            print("❌ Форма поиска товаров НЕ найдена на главной странице")
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")


def compare_with_catalog_page():
    """Сравнение с формой на странице каталога"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n=== Сравнение с формой на странице каталога ===\n")
    
    try:
        response = requests.get(base_url + "/catalog/")
        if response.status_code != 200:
            print(f"❌ Ошибка загрузки страницы каталога: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем форму поиска
        search_form = None
        forms = soup.find_all('form')
        
        for form in forms:
            q_input = form.find('input', {'name': 'q'})
            if q_input:
                search_form = form
                break
        
        if search_form:
            print("Форма поиска на странице каталога:")
            action = search_form.get('action', '')
            method = search_form.get('method', 'get')
            
            print(f"Action: {action}")
            print(f"Метод: {method}")
            
            q_input = search_form.find('input', {'name': 'q'})
            if q_input:
                input_type = q_input.get('type', 'text')
                placeholder = q_input.get('placeholder', '')
                print(f"Поле q: type='{input_type}' placeholder='{placeholder}'")
            
            print("✅ Форма поиска найдена на странице каталога")
        else:
            print("❌ Форма поиска НЕ найдена на странице каталога")
            
    except Exception as e:
        print(f"❌ Ошибка анализа каталога: {e}")


if __name__ == "__main__":
    analyze_home_page_form()
    compare_with_catalog_page()
    
    print("\n=== Следующие шаги ===")
    print("1. Если форма найдена и настроена правильно:")
    print("   - Проблема может быть в JavaScript")
    print("   - Или в настройках браузера")
    print("   - Попробуйте в другом браузере")
    print()
    print("2. Если форма неправильная:")
    print("   - Нужно исправить шаблон cms/home.html")
    print("   - Проверить URL в action")
    print()
    print("3. Для окончательной проверки откройте в браузере:")
    print("   http://127.0.0.1:8000 - и попробуйте поиск")
    print("   http://127.0.0.1:8000/catalog/ - и сравните")
