#!/usr/bin/env python
"""
Создание тестовой страницы для отладки поиска
"""
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.urls import reverse

def create_debug_page():
    """Создание отладочной страницы"""
    
    # Получаем правильные URL'ы
    try:
        search_url = reverse('catalog_web:search')
        print(f"URL для поиска: {search_url}")
    except Exception as e:
        print(f"Ошибка получения URL поиска: {e}")
        search_url = "/catalog/search/"
    
    try:
        vin_search_url = reverse('vin_search_web:search')
        print(f"URL для VIN поиска: {vin_search_url}")
    except Exception as e:
        print(f"Ошибка получения VIN URL: {e}")
        vin_search_url = "/vin-search/search/"
    
    debug_html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отладка поиска - ShopApex</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Отладка поиска ShopApex</h1>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <h3>Поиск товаров</h3>
                <form method="get" action="{search_url}">
                    <div class="input-group mb-3">
                        <input type="text" name="q" class="form-control" placeholder="Поиск товаров..." value="">
                        <button class="btn btn-primary" type="submit">
                            <i class="fas fa-search"></i> Найти
                        </button>
                    </div>
                </form>
                <small class="text-muted">Action: {search_url}</small>
            </div>
            
            <div class="col-md-6">
                <h3>Поиск по VIN</h3>
                <form method="get" action="{vin_search_url}">
                    <div class="input-group mb-3">
                        <input type="text" name="vin" class="form-control" placeholder="VIN код..." value="">
                        <button class="btn btn-success" type="submit">
                            <i class="fas fa-car"></i> Найти
                        </button>
                    </div>
                </form>
                <small class="text-muted">Action: {vin_search_url}</small>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <h3>Прямые ссылки для тестирования</h3>
                <ul class="list-group">
                    <li class="list-group-item">
                        <a href="{search_url}?q=масло" target="_blank">Поиск "масло"</a>
                    </li>
                    <li class="list-group-item">
                        <a href="{search_url}?q=тормозные" target="_blank">Поиск "тормозные"</a>
                    </li>
                    <li class="list-group-item">
                        <a href="{search_url}?q=brembo" target="_blank">Поиск "brembo"</a>
                    </li>
                    <li class="list-group-item">
                        <a href="/catalog/" target="_blank">Страница каталога</a>
                    </li>
                    <li class="list-group-item">
                        <a href="/" target="_blank">Главная страница</a>
                    </li>
                </ul>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <h3>Информация для отладки</h3>
                <div class="alert alert-info">
                    <strong>JavaScript отладка:</strong><br>
                    Откройте консоль браузера (F12) и проверьте ошибки JavaScript при отправке формы.
                </div>
                <div class="alert alert-warning">
                    <strong>Network отладка:</strong><br>
                    Используйте вкладку Network в инструментах разработчика для отслеживания запросов.
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Отладочный JavaScript
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Отладочная страница загружена');
            console.log('URL поиска: {search_url}');
            console.log('URL VIN поиска: {vin_search_url}');
            
            // Отслеживание отправки форм
            document.querySelectorAll('form').forEach(function(form) {{
                form.addEventListener('submit', function(e) {{
                    console.log('Отправка формы:', form.action);
                    console.log('Метод:', form.method);
                    console.log('Данные:', new FormData(form));
                }});
            }});
        }});
    </script>
</body>
</html>
    """
    
    with open('debug_search.html', 'w', encoding='utf-8') as f:
        f.write(debug_html)
    
    print(f"Отладочная страница создана: debug_search.html")
    print(f"Откройте http://127.0.0.1:8000/../debug_search.html или используйте файл напрямую")

if __name__ == "__main__":
    create_debug_page()
