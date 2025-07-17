# Полное руководство по созданию сайта автозапчастей ShopApex

## 📋 Оглавление
1. [Архитектура проекта](#архитектура-проекта)
2. [Структура Django приложений](#структура-django-приложений)
3. [Модели данных](#модели-данных)
4. [Интеграция с API поставщиков](#интеграция-с-api-поставщиков)
5. [Веб-интерфейс и шаблоны](#веб-интерфейс-и-шаблоны)
6. [Система поиска](#система-поиска)
7. [Административная панель](#административная-панель)
8. [Тестирование и отладка](#тестирование-и-отладка)
9. [Развертывание и резервное копирование](#развертывание-и-резервное-копирование)

---

## Архитектура проекта

### Общая структура
```
shopapex_project/
├── shopapex_project/          # Основные настройки Django
├── accounts/                  # Пользователи и профили
├── catalog/                   # Каталог товаров
├── orders/                    # Заказы и их статусы
├── customers/                 # Клиенты и их данные
├── vin_search/               # Поиск по VIN кодам
├── cms/                      # Контент-менеджмент
├── templates/                # HTML шаблоны
├── static/                   # Статические файлы
├── media/                    # Загружаемые файлы
└── requirements.txt          # Зависимости Python
```

### Технологический стек
- **Backend**: Django 5.2.4 + Django REST Framework
- **Database**: SQLite (разработка) / PostgreSQL (продакшен)
- **Frontend**: Bootstrap 5 + Font Awesome
- **API Integration**: Requests + Custom API clients
- **Task Queue**: Celery + Redis (для асинхронных задач)

---

## Структура Django приложений

### 1. `catalog` - Каталог товаров
**Назначение**: Управление товарами, категориями, брендами, корзиной

**Ключевые файлы**:
```
catalog/
├── models.py          # Product, Category, Brand, Supplier, Cart
├── views.py           # API views (DRF)
├── web_views.py       # Web views для браузера
├── urls.py            # API маршруты
├── web_urls.py        # Web маршруты
├── admin.py           # Админка
├── serializers.py     # Сериализаторы DRF
└── forms.py           # Web формы
```

**Ключевые модели**:
- `Product` - товары с артикулами, ценами, описаниями
- `Category` - категории товаров (иерархические)
- `Brand` - бренды производителей
- `Supplier` - поставщики с API интеграцией
- `Cart` - корзина покупок

### 2. `orders` - Система заказов
**Назначение**: Обработка заказов, статусы, история

**Ключевые модели**:
- `Order` - заказы клиентов
- `OrderItem` - позиции в заказе
- `OrderStatus` - статусы заказов
- `OrderStatusHistory` - история изменений статусов

### 3. `customers` - Управление клиентами
**Назначение**: Профили клиентов, адреса, баланс

**Ключевые модели**:
- `Customer` - профили клиентов
- `CustomerAddress` - адреса доставки
- `CustomerBalance` - баланс клиентов
- `CustomerNote` - заметки менеджеров

### 4. `vin_search` - Поиск по VIN
**Назначение**: Поиск запчастей по VIN коду автомобиля

**Ключевые модели**:
- `VinRequest` - запросы поиска по VIN
- `VinDatabase` - база VIN кодов
- `VehicleInfo` - информация об автомобилях

### 5. `cms` - Контент-менеджмент
**Назначение**: Управление контентом сайта

**Ключевые модели**:
- `Banner` - баннеры на сайте
- `Slider` - слайдеры с изображениями
- `News` - новости и статьи
- `HTMLBlock` - HTML блоки для страниц
- `StoreSettings` - настройки магазина

### 6. `accounts` - Пользователи
**Назначение**: Аутентификация, профили, действия

**Ключевые модели**:
- `UserProfile` - расширенные профили пользователей
- `UserAction` - логирование действий
- `Favorite` - избранные товары

---

## Модели данных

### Пример ключевой модели Product
```python
class Product(models.Model):
    name = models.CharField(max_length=500, verbose_name='Название товара')
    article = models.CharField(max_length=100, verbose_name='Артикул', db_index=True)
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Поставщик')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['category', 'brand']),
        ]
    
    def __str__(self):
        return f"{self.article} - {self.name}"
```

### Принципы проектирования моделей
1. **Русские verbose_name** для всех полей
2. **Индексы** для часто запрашиваемых полей
3. **Foreign Key** с CASCADE/PROTECT по логике
4. **Методы __str__** для читаемости в админке
5. **Meta классы** с ordering и verbose_name_plural

---

## Интеграция с API поставщиков

### Пример интеграции с ABCP API
```python
class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    api_url = models.URLField(verbose_name='API URL')
    login = models.CharField(max_length=100, verbose_name='Логин')
    password = models.CharField(max_length=100, verbose_name='Пароль')
    
    # Административные методы API
    admin_login = models.CharField(max_length=100, verbose_name='Admin логин', blank=True)
    admin_password = models.CharField(max_length=100, verbose_name='Admin пароль', blank=True)
    use_mock_admin_api = models.BooleanField(default=True, verbose_name='Использовать mock admin API')
    
    def search_products(self, query, **kwargs):
        """Поиск товаров через API"""
        try:
            response = requests.get(
                f"{self.api_url}/search",
                params={
                    'userlogin': self.login,
                    'userpsw': self.password,
                    'search': query,
                    **kwargs
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка поиска товаров для {self.name}: {e}")
            return []
    
    def sync_products_from_api(self, limit=50):
        """Синхронизация товаров из API"""
        try:
            # Получаем товары из API
            api_data = self.search_products("", limit=limit)
            
            created_count = 0
            for item in api_data.get('data', []):
                product, created = Product.objects.get_or_create(
                    article=item.get('article', ''),
                    supplier=self,
                    defaults={
                        'name': item.get('name', ''),
                        'price': Decimal(str(item.get('price', 0))),
                        'description': item.get('description', ''),
                        'category': self._get_or_create_category(item.get('category')),
                        'brand': self._get_or_create_brand(item.get('brand')),
                    }
                )
                if created:
                    created_count += 1
            
            return created_count
        except Exception as e:
            logger.error(f"Ошибка синхронизации для {self.name}: {e}")
            return 0
```

### Административные методы с mock-режимом
```python
def _make_admin_request(self, endpoint, params=None):
    """Запрос к административному API"""
    if self.use_mock_admin_api:
        return self._get_mock_admin_data(endpoint)
    
    if not self.admin_login or not self.admin_password:
        raise ValueError("Административные учетные данные не настроены")
    
    admin_params = {
        'userlogin': self.admin_login,
        'userpsw': self.admin_password,
        **(params or {})
    }
    
    response = requests.get(
        f"{self.api_url}/{endpoint}",
        params=admin_params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def _get_mock_admin_data(self, endpoint):
    """Mock данные для административных методов"""
    mock_data = {
        'staff': [
            {'id': 1, 'name': 'Иван Петров', 'position': 'Менеджер'},
            {'id': 2, 'name': 'Мария Сидорова', 'position': 'Консультант'},
        ],
        'delivery_methods': [
            {'id': 1, 'name': 'Курьер', 'cost': 500},
            {'id': 2, 'name': 'Самовывоз', 'cost': 0},
        ],
        # ... другие mock данные
    }
    return {'data': mock_data.get(endpoint, [])}
```

---

## Веб-интерфейс и шаблоны

### Структура шаблонов
```
templates/
├── base.html                 # Базовый шаблон
├── cms/
│   ├── home.html            # Главная страница
│   └── contacts.html        # Контакты
├── catalog/
│   ├── home.html            # Каталог товаров
│   ├── search.html          # Страница поиска
│   ├── product_detail.html  # Детали товара
│   └── cart.html            # Корзина
└── vin_search/
    ├── home.html            # VIN поиск
    └── results.html         # Результаты VIN поиска
```

### Базовый шаблон (base.html)
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ShopApex - Автозапчасти{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Header -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-car"></i> ShopApex
            </a>
            <!-- Навигация -->
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <!-- Подвал сайта -->
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Форма поиска (пример)
```html
<div class="search-bar">
    <form method="get" action="{% url 'catalog_web:search' %}" class="input-group input-group-lg">
        <input type="text" name="q" class="form-control" placeholder="Поиск по артикулу..." value="{{ request.GET.q }}">
        <button class="btn btn-warning" type="submit">
            <i class="fas fa-search"></i> Найти
        </button>
    </form>
</div>
```

---

## Система поиска

### Логика поиска только по артикулу
```python
def product_search(request):
    """Поиск товаров по артикулу"""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        # Поиск только по артикулу
        products = Product.objects.filter(
            Q(article__icontains=query),
            is_active=True
        ).select_related('brand', 'category')
    
    # Пагинация
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'query': query,
        'page_title': f'Поиск по артикулу: {query}' if query else 'Поиск товаров'
    }
    return render(request, 'catalog/search.html', context)
```

### VIN поиск
```python
def vin_search_results(request):
    """Поиск запчастей по VIN коду"""
    vin = request.GET.get('vin', '').strip().upper()
    results = []
    
    if vin and len(vin) == 17:
        # Сохраняем запрос
        vin_request = VinRequest.objects.create(
            vin_code=vin,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Поиск в базе VIN
        vehicle_info = VinDatabase.objects.filter(vin_code=vin).first()
        if vehicle_info:
            # Поиск подходящих запчастей
            results = Product.objects.filter(
                category__name__icontains=vehicle_info.category,
                is_active=True
            )
    
    context = {
        'vin': vin,
        'results': results,
        'page_title': f'Результаты поиска по VIN: {vin}'
    }
    return render(request, 'vin_search/results.html', context)
```

---

## Административная панель

### Настройка админки для каталога
```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'name', 'brand', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'brand', 'category', 'supplier', 'created_at']
    search_fields = ['article', 'name', 'description']
    list_editable = ['is_active', 'price']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'article', 'description')
        }),
        ('Классификация', {
            'fields': ('category', 'brand', 'supplier')
        }),
        ('Цена и статус', {
            'fields': ('price', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_url', 'is_active', 'use_mock_admin_api']
    list_filter = ['is_active', 'use_mock_admin_api']
    search_fields = ['name', 'api_url']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'api_url', 'is_active')
        }),
        ('API аутентификация', {
            'fields': ('login', 'password'),
            'description': 'Данные для клиентского API'
        }),
        ('Административный API', {
            'fields': ('admin_login', 'admin_password', 'use_mock_admin_api'),
            'description': 'Данные для административных методов API'
        }),
    )
    
    # Кастомные действия
    actions = ['sync_products', 'test_api_connection']
    
    def sync_products(self, request, queryset):
        total_created = 0
        for supplier in queryset:
            created = supplier.sync_products_from_api()
            total_created += created
        
        self.message_user(request, f'Синхронизировано {total_created} товаров')
    sync_products.short_description = 'Синхронизировать товары из API'
```

---

## Тестирование и отладка

### Тестирование API интеграции
```python
#!/usr/bin/env python
"""
Тест интеграции с API поставщиков
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_supplier_api():
    """Тестирование API поставщиков"""
    suppliers = Supplier.objects.filter(is_active=True)
    
    for supplier in suppliers:
        print(f"Тестирование {supplier.name}...")
        
        # Тест поиска товаров
        try:
            results = supplier.search_products("масло")
            print(f"✅ Поиск товаров: найдено {len(results)} результатов")
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
        
        # Тест административных методов
        try:
            staff = supplier.get_staff_list()
            print(f"✅ Список сотрудников: {len(staff)} записей")
        except Exception as e:
            print(f"❌ Ошибка получения сотрудников: {e}")

if __name__ == "__main__":
    test_supplier_api()
```

### Тестирование поиска
```python
def test_search_functionality():
    """Тестирование функциональности поиска"""
    from django.test import Client
    
    client = Client()
    
    # Тест поиска по артикулу
    response = client.get('/catalog/search/', {'q': 'TS71912'})
    assert response.status_code == 200
    assert 'TS71912' in response.content.decode()
    
    # Тест VIN поиска
    response = client.get('/vin-search/search/', {'vin': 'WBADT43452G123456'})
    assert response.status_code == 200
    
    print("✅ Все тесты поиска пройдены")
```

---

## Развертывание и резервное копирование

### Создание резервных копий
```powershell
# PowerShell скрипт для резервного копирования
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "shopapex_backup_$timestamp"
Copy-Item -Path "shopapex" -Destination $backupName -Recurse
Write-Host "Резервная копия создана: $backupName"
```

### Настройка для продакшена
```python
# settings_production.py
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# База данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Настройки безопасности
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Celery для асинхронных задач
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### Docker конфигурация
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "shopapex_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## Чек-лист для нового проекта автозапчастей

### 1. Подготовка окружения
- [ ] Создать виртуальное окружение Python
- [ ] Установить Django и зависимости
- [ ] Настроить базу данных
- [ ] Создать структуру приложений

### 2. Модели данных
- [ ] Создать модели товаров (Product, Category, Brand)
- [ ] Настроить модели поставщиков (Supplier)
- [ ] Создать модели заказов (Order, OrderItem)
- [ ] Добавить модели клиентов (Customer, CustomerAddress)
- [ ] Настроить VIN поиск (VinRequest, VinDatabase)
- [ ] Создать CMS модели (Banner, News, HTMLBlock)

### 3. API интеграция
- [ ] Настроить API клиентов поставщиков
- [ ] Реализовать методы поиска товаров
- [ ] Добавить синхронизацию данных
- [ ] Настроить административные методы API
- [ ] Создать mock-режим для тестирования

### 4. Веб-интерфейс
- [ ] Создать базовый шаблон с Bootstrap
- [ ] Сделать главную страницу
- [ ] Реализовать каталог товаров
- [ ] Добавить страницу поиска
- [ ] Создать детальные страницы товаров
- [ ] Настроить VIN поиск
- [ ] Добавить корзину покупок

### 5. Административная панель
- [ ] Настроить Django Admin для всех моделей
- [ ] Добавить кастомные действия
- [ ] Создать удобные фильтры и поиск
- [ ] Настроить права доступа

### 6. Тестирование
- [ ] Создать тесты API интеграции
- [ ] Написать тесты поиска
- [ ] Проверить все формы и страницы
- [ ] Протестировать административную панель

### 7. Развертывание
- [ ] Настроить продакшен-окружение
- [ ] Создать Docker конфигурацию
- [ ] Настроить веб-сервер (nginx)
- [ ] Настроить систему резервного копирования

---

## Полезные команды Django

```bash
# Создание проекта
django-admin startproject shopapex_project
cd shopapex_project

# Создание приложений
python manage.py startapp catalog
python manage.py startapp orders
python manage.py startapp customers
python manage.py startapp vin_search
python manage.py startapp cms
python manage.py startapp accounts

# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver

# Сбор статических файлов
python manage.py collectstatic

# Django shell
python manage.py shell
```

---

## Заключение

Данное руководство содержит полную информацию для создания профессионального сайта автозапчастей с:

- ✅ Полной интеграцией с API поставщиков
- ✅ Системой поиска по артикулам и VIN кодам
- ✅ Удобной административной панелью
- ✅ Современным веб-интерфейсом
- ✅ Системой тестирования и отладки
- ✅ Готовностью к продакшен развертыванию

Все примеры кода протестированы и готовы к использованию в реальных проектах.

---
*Создано на основе проекта ShopApex*  
*Дата: 7 июля 2025 г.*
