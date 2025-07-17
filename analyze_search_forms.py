#!/usr/bin/env python
"""
Детальный анализ HTML форм поиска на главной странице и странице каталога
"""
import os
import django
import requests
from bs4 import BeautifulSoup

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def analyze_search_forms():
    """Анализ форм поиска"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Детальный анализ форм поиска ===\n")
    
    # 1. Главная страница
    print("1. Анализ главной страницы (/)...")
    try:
        response = requests.get(base_url + "/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем все формы
            forms = soup.find_all('form')
            print(f"   Найдено форм: {len(forms)}")
            
            # Анализируем каждую форму
            search_forms = []
            for i, form in enumerate(forms):
                method = form.get('method', 'get').lower()
                action = form.get('action', '')
                
                # Ищем поля ввода
                inputs = form.find_all('input')
                search_inputs = []
                for inp in inputs:
                    if inp.get('name') in ['q', 'query', 'search']:
                        search_inputs.append(inp.get('name'))
                
                print(f"   Форма {i+1}:")
                print(f"     - Метод: {method}")
                print(f"     - Action: {action}")
                print(f"     - Поля поиска: {search_inputs}")
                
                if search_inputs:
                    search_forms.append({
                        'method': method,
                        'action': action,
                        'fields': search_inputs
                    })
            
            if search_forms:
                print(f"   ✅ Найдено {len(search_forms)} форм поиска")
            else:
                print("   ❌ Формы поиска не найдены")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print()
    
    # 2. Страница каталога
    print("2. Анализ страницы каталога (/catalog/)...")
    try:
        response = requests.get(base_url + "/catalog/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем все формы
            forms = soup.find_all('form')
            print(f"   Найдено форм: {len(forms)}")
            
            # Анализируем каждую форму
            search_forms = []
            for i, form in enumerate(forms):
                method = form.get('method', 'get').lower()
                action = form.get('action', '')
                
                # Ищем поля ввода
                inputs = form.find_all('input')
                search_inputs = []
                for inp in inputs:
                    if inp.get('name') in ['q', 'query', 'search']:
                        search_inputs.append(inp.get('name'))
                
                print(f"   Форма {i+1}:")
                print(f"     - Метод: {method}")
                print(f"     - Action: {action}")
                print(f"     - Поля поиска: {search_inputs}")
                
                if search_inputs:
                    search_forms.append({
                        'method': method,
                        'action': action,
                        'fields': search_inputs
                    })
            
            if search_forms:
                print(f"   ✅ Найдено {len(search_forms)} форм поиска")
            else:
                print("   ❌ Формы поиска не найдены")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print()
    
    # 3. Тестируем конкретную отправку формы
    print("3. Тест отправки формы с главной страницы...")
    try:
        # Получаем CSRF токен если нужен
        session = requests.Session()
        response = session.get(base_url + "/")
        
        # Отправляем поиск
        search_response = session.get(base_url + "/catalog/search/", params={'q': 'тест'})
        print(f"   Статус поиска: {search_response.status_code}")
        
        if search_response.status_code == 200:
            print("   ✅ Поиск работает")
            if 'тест' in search_response.text.lower():
                print("   ✅ Запрос обрабатывается")
            else:
                print("   ⚠️  Запрос обрабатывается, но результаты не видны")
        else:
            print(f"   ❌ Ошибка поиска: {search_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")


if __name__ == "__main__":
    analyze_search_forms()
