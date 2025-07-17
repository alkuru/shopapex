#!/usr/bin/env python
"""
Проверка доступности различных ресурсов vinttop.ru
"""
import requests
from requests.auth import HTTPBasicAuth

def check_vinttop_resources():
    """Проверяет доступность различных ресурсов vinttop"""
    
    login = "autovag@bk.ru"
    password = "0754"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    }
    
    # Ресурсы для проверки
    resources = [
        {
            'name': 'Основной сайт vinttop.ru',
            'url': 'https://vinttop.ru',
            'auth': False
        },
        {
            'name': 'Основной сайт HTTP',
            'url': 'http://vinttop.ru', 
            'auth': False
        },
        {
            'name': 'API сервер (наши данные)',
            'url': 'http://178.208.92.49',
            'auth': True
        },
        {
            'name': 'API сервер без авторизации',
            'url': 'http://178.208.92.49',
            'auth': False
        },
        {
            'name': 'Возможный API на основном сайте',
            'url': 'https://vinttop.ru/api',
            'auth': True
        }
    ]
    
    print("🌐 ПРОВЕРКА ДОСТУПНОСТИ РЕСУРСОВ VINTTOP")
    print("=" * 60)
    
    for resource in resources:
        print(f"\n🔍 {resource['name']}")
        print(f"    URL: {resource['url']}")
        print(f"    Авторизация: {'Да' if resource['auth'] else 'Нет'}")
        
        try:
            if resource['auth']:
                response = requests.get(
                    resource['url'],
                    headers=headers,
                    auth=HTTPBasicAuth(login, password),
                    timeout=10,
                    verify=False  # Игнорируем SSL ошибки
                )
            else:
                response = requests.get(
                    resource['url'],
                    headers=headers,
                    timeout=10,
                    verify=False
                )
            
            print(f"    ✅ Статус: {response.status_code}")
            print(f"    ✅ Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"    ✅ Размер: {len(response.text)} символов")
            
            # Анализируем содержимое
            content = response.text.lower()
            
            if response.status_code == 200:
                if 'vinttop' in content:
                    print(f"    ✅ Содержит 'vinttop' - это их ресурс")
                if 'api' in content:
                    print(f"    ✅ Упоминается 'api'")
                if 'json' in content:
                    print(f"    ✅ Упоминается 'json'")
                if 'webservice' in content or 'web service' in content:
                    print(f"    ✅ Упоминается 'webservice'")
                    
                # Показываем первые строки
                lines = response.text.split('\n')[:3]
                print(f"    📄 Первые строки:")
                for i, line in enumerate(lines, 1):
                    clean_line = line.strip()[:80]
                    if clean_line:
                        print(f"       {i}. {clean_line}")
                        
            elif response.status_code == 503:
                print(f"    ⚠️  Сервис временно недоступен")
            elif response.status_code == 401:
                print(f"    🔐 Требуется авторизация")
            elif response.status_code == 403:
                print(f"    🚫 Доступ запрещен")
            elif response.status_code == 404:
                print(f"    ❌ Не найден")
            else:
                print(f"    ⚠️  Неожиданный статус")
                
        except requests.exceptions.Timeout:
            print(f"    ⏰ Тайм-аут подключения")
        except requests.exceptions.ConnectionError:
            print(f"    ❌ Ошибка подключения")
        except requests.exceptions.SSLError:
            print(f"    🔒 Ошибка SSL")
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
    
    print(f"\n📋 РЕКОМЕНДАЦИИ:")
    print(f"1. Свяжитесь с vinttop.ru для уточнения:")
    print(f"   - Правильный URL API")
    print(f"   - Метод авторизации")
    print(f"   - Доступность сервиса")
    print(f"2. Возможно, нужно добавить ваш IP в белый список")
    print(f"3. API может быть временно недоступен")
    print(f"4. Проверьте документацию по их API")

if __name__ == "__main__":
    check_vinttop_resources()
