#!/usr/bin/env python
"""
Скрипт для тестирования поиска на сайте
"""
import requests
from urllib.parse import urljoin

def test_search_functionality():
    """Тестирует функциональность поиска на всех страницах сайта"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 ТЕСТИРОВАНИЕ ПОИСКА НА САЙТЕ")
    print("=" * 50)
    
    # Тестовые поисковые запросы
    test_queries = [
        "колодки",
        "ремень", 
        "масла",
        "тормозные",
        "BP0526",
        "MITSUBISHI"
    ]
    
    # Страницы для тестирования
    test_pages = [
        ("Главная страница", "/"),
        ("Каталог товаров", "/catalog/"),
        ("Поиск каталога", "/catalog/search/"),
    ]
    
    print(f"📋 Проверяем доступность страниц:")
    for page_name, url in test_pages:
        try:
            response = requests.get(urljoin(base_url, url), timeout=5)
            status = "✅ Доступна" if response.status_code == 200 else f"❌ Ошибка {response.status_code}"
            print(f"   {page_name}: {status}")
        except Exception as e:
            print(f"   {page_name}: ❌ Ошибка подключения - {e}")
    
    print(f"\n🔎 Тестируем поиск по запросам:")
    
    for query in test_queries:
        print(f"\n📝 Запрос: '{query}'")
        
        # Тестируем поиск через каталог
        search_url = f"{base_url}/catalog/search/?q={query}"
        
        try:
            response = requests.get(search_url, timeout=5)
            
            if response.status_code == 200:
                # Простая проверка - есть ли в ответе наш запрос
                content = response.text.lower()
                
                # Ищем признаки успешного поиска
                if 'результат' in content or 'найден' in content or query.lower() in content:
                    print(f"   ✅ Поиск работает: {search_url}")
                    
                    # Подсчитываем результаты (примерно)
                    if 'card' in content:
                        card_count = content.count('card-title')
                        print(f"   📊 Примерно найдено карточек: {card_count}")
                    
                else:
                    print(f"   ⚠️  Результаты неясны: {search_url}")
                    
            else:
                print(f"   ❌ Ошибка {response.status_code}: {search_url}")
                
        except Exception as e:
            print(f"   ❌ Ошибка запроса: {e}")
    
    print(f"\n🔗 ПОЛЕЗНЫЕ ССЫЛКИ ДЛЯ ТЕСТИРОВАНИЯ:")
    print("-" * 40)
    
    for query in test_queries[:3]:  # Первые 3 запроса
        search_url = f"{base_url}/catalog/search/?q={query}"
        print(f"🔍 Поиск '{query}': {search_url}")
    
    print(f"\n📄 СТРАНИЦЫ САЙТА:")
    print("-" * 20)
    print(f"🏠 Главная: {base_url}/")
    print(f"📚 Каталог: {base_url}/catalog/")
    print(f"🔍 Поиск: {base_url}/catalog/search/")
    print(f"🚗 VIN поиск: {base_url}/vin-search/")
    print(f"📞 Контакты: {base_url}/contacts/")
    print(f"⚙️  Админка: {base_url}/admin/")
    
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестирования поиска на сайте")
    print("=" * 50)
    
    try:
        test_search_functionality()
        
        print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"📝 Рекомендации:")
        print(f"   • Откройте главную страницу: http://127.0.0.1:8000/")
        print(f"   • Протестируйте поиск вручную")
        print(f"   • Проверьте работу форм")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
