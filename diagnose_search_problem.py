#!/usr/bin/env python
"""
Проверка конкретной проблемы с поиском с главной страницы
"""
import os
import django
import time

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def manual_test_instructions():
    """Инструкции для ручного тестирования"""
    print("=== Инструкции для ручного тестирования поиска ===\n")
    
    print("1. Откройте браузер и перейдите на http://127.0.0.1:8000")
    print("2. Найдите форму поиска в разделе 'Автозапчасти для любого автомобиля'")
    print("3. Введите любой поисковый запрос (например, 'масло')")
    print("4. Нажмите кнопку 'Найти'")
    print("5. Проверьте, происходит ли переход на страницу поиска")
    print("\nЕсли поиск НЕ работает:")
    print("- Откройте консоль браузера (F12)")
    print("- Перейдите на вкладку Console")
    print("- Попробуйте отправить форму еще раз")
    print("- Найдите ошибки JavaScript (красные сообщения)")
    print("- Перейдите на вкладку Network")
    print("- Проверьте, отправляются ли HTTP запросы при отправке формы")
    
    print("\n=== Альтернативные тесты ===\n")
    print("1. Перейдите на http://127.0.0.1:8000/catalog/")
    print("2. Попробуйте поиск с этой страницы")
    print("3. Сравните поведение")
    
    print("\n=== Прямое тестирование ===\n")
    print("Откройте эти ссылки в браузере:")
    print("- http://127.0.0.1:8000/catalog/search/?q=масло")
    print("- http://127.0.0.1:8000/catalog/search/?q=тормозные")
    print("- http://127.0.0.1:8000/catalog/search/?q=brembo")
    
    print("\nЕсли прямые ссылки работают, но форма с главной страницы не работает,")
    print("то проблема в JavaScript или HTML форме.")


def check_url_patterns():
    """Проверка паттернов URL"""
    print("\n=== Проверка URL паттернов ===\n")
    
    from django.urls import reverse, NoReverseMatch
    
    # Список URL для проверки
    urls_to_check = [
        ('catalog_web:search', 'Поиск в каталоге'),
        ('catalog_web:home', 'Главная каталога'),
        ('vin_search_web:search', 'VIN поиск'),
        ('vin_search_web:home', 'Главная VIN поиска'),
        ('cms_web:contacts', 'Контакты'),
        ('cms:home', 'Главная CMS'),
    ]
    
    for url_name, description in urls_to_check:
        try:
            url = reverse(url_name)
            print(f"✅ {description}: {url}")
        except NoReverseMatch as e:
            print(f"❌ {description}: Ошибка - {e}")
        except Exception as e:
            print(f"⚠️  {description}: Исключение - {e}")


def check_templates():
    """Проверка доступности шаблонов"""
    print("\n=== Проверка шаблонов ===\n")
    
    import os
    from django.conf import settings
    
    templates_to_check = [
        'cms/home.html',
        'catalog/search.html',
        'catalog/home.html',
        'base.html',
    ]
    
    for template_path in templates_to_check:
        full_path = None
        found = False
        
        # Проверяем во всех директориях шаблонов
        for template_dir in settings.TEMPLATES[0]['DIRS']:
            full_path = os.path.join(template_dir, template_path)
            if os.path.exists(full_path):
                print(f"✅ {template_path}: найден в {full_path}")
                found = True
                break
        
        if not found:
            print(f"❌ {template_path}: НЕ НАЙДЕН")


if __name__ == "__main__":
    print("ShopApex - Диагностика проблем поиска\n")
    
    check_url_patterns()
    check_templates()
    manual_test_instructions()
    
    print("\n=== Рекомендации ===\n")
    print("1. Если все URL работают правильно, но поиск с главной не работает:")
    print("   - Проверьте JavaScript в браузере")
    print("   - Проверьте HTML форму на главной странице")
    print("   - Сравните с формой на странице каталога")
    
    print("\n2. Если есть ошибки в URL:")
    print("   - Проверьте настройки URL в файлах urls.py")
    print("   - Проверьте namespace конфликты")
    
    print("\n3. Если есть проблемы с шаблонами:")
    print("   - Проверьте пути к шаблонам в settings.py")
    print("   - Убедитесь, что все шаблоны существуют")
