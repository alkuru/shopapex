# ПЛАН КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ ABCP API ИНТЕГРАЦИИ

## 📋 Задачи для немедленного выполнения

### 1. Добавление полей для административного API

#### 🔧 Изменения в модели Supplier

```python
# Добавить в catalog/models.py в класс Supplier перед api_key:

admin_login = models.CharField(
    max_length=100, 
    blank=True, 
    verbose_name='Логин API-администратора',
    help_text='Логин для административных методов ABCP API (cp/*)'
)
admin_password = models.CharField(
    max_length=100, 
    blank=True, 
    verbose_name='Пароль API-администратора',
    help_text='Пароль для административных методов ABCP API'
)
use_mock_admin_api = models.BooleanField(
    default=True, 
    verbose_name='Использовать mock данные для админ API',
    help_text='Если True, административные методы возвращают тестовые данные'
)

# Также добавить новые поля согласно документации:
office_id = models.CharField(
    max_length=50, 
    blank=True, 
    verbose_name='ID офиса поставщика',
    help_text='Идентификатор офиса для методов API'
)
use_online_stocks = models.BooleanField(
    default=False, 
    verbose_name='Использовать онлайн склады',
    help_text='Включает поиск по онлайн складам'
)
default_shipment_address = models.CharField(
    max_length=50, 
    default='0',
    verbose_name='Адрес доставки по умолчанию',
    help_text='0 = самовывоз, другие значения = ID адреса доставки'
)
```

### 2. Обновление административной панели

#### 🔧 Изменения в catalog/admin.py

```python
# Обновить fieldsets в SupplierAdmin:

fieldsets = [
    ('Основная информация', {
        'fields': ('name', 'description', 'is_active')
    }),
    ('Контактная информация', {
        'fields': ('contact_person', 'email', 'phone', 'website'),
        'classes': ('collapse',)
    }),
    ('API настройки', {
        'fields': (
            'api_type', 'api_url',
            ('api_login', 'api_password'),           # Клиентский доступ
            ('admin_login', 'admin_password'),       # Административный доступ
            'use_mock_admin_api',
            ('office_id', 'use_online_stocks', 'default_shipment_address'),
            ('api_key', 'api_secret'),
            ('data_format', 'sync_frequency')
        ),
        'description': 'API клиентский доступ - для поиска товаров. API административный доступ - для cp/* методов.'
    }),
    # ... остальные fieldsets
]
```

### 3. Создание миграции

```bash
# Выполнить в терминале:
cd /path/to/shopapex
python manage.py makemigrations catalog --name add_admin_api_fields
python manage.py migrate
```

### 4. Исправление метода _make_admin_request

#### 🔧 Полное обновление метода в catalog/models.py

```python
def _make_admin_request(self, endpoint, params=None):
    """Универсальный метод для административных запросов к ABCP API"""
    if self.api_type != 'autoparts' or not self.api_url:
        return False, "API автозапчастей не настроен"
    
    # Если нет admin credentials или включен mock режим, возвращаем mock данные
    if (not self.admin_login or not self.admin_password or 
        self.use_mock_admin_api):
        return self._get_mock_admin_data(endpoint, params)
    
    try:
        # Создаем md5-хэш пароля администратора
        password_hash = hashlib.md5(self.admin_password.encode('utf-8')).hexdigest()
        
        # Формируем URL
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Базовые параметры авторизации для админа
        base_params = {
            'userlogin': self.admin_login,
            'userpsw': password_hash,
            'format': 'json'
        }
        
        # Добавляем дополнительные параметры
        if params:
            base_params.update(params)
        
        # Добавляем офис если указан
        if self.office_id:
            base_params['officeId'] = self.office_id
        
        response = requests.get(url, params=base_params, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Проверяем на ошибки в ответе
                if isinstance(data, dict) and 'errorCode' in data:
                    error_code = data.get('errorCode')
                    error_message = data.get('errorMessage', 'Неизвестная ошибка')
                    return False, f"ABCP Admin API ошибка {error_code}: {error_message}"
                
                return True, data
                
            except json.JSONDecodeError:
                return False, "ABCP Admin API: ошибка парсинга JSON ответа"
        elif response.status_code == 403:
            return False, f"ABCP Admin API: ошибка авторизации (403). Проверьте логин и пароль администратора."
        else:
            return False, f"ABCP Admin API: ошибка HTTP {response.status_code}"
        
    except Exception as e:
        return False, f"Ошибка запроса к ABCP Admin API: {str(e)}"
```

### 5. Обновление методов поиска для новых параметров

#### 🔧 Обновление search_products_by_article

```python
def search_products_by_article(self, article, brand=None):
    """Поиск товаров по артикулу через ABCP API"""
    if self.api_type != 'autoparts' or not self.api_url:
        return False, "API автозапчастей не настроен"
    
    if not self.api_login or not self.api_password:
        return False, "Логин или пароль не настроены"
    
    try:
        # Создаем md5-хэш пароля
        password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
        
        # Если поиск без конкретного бренда, используем поиск брендов по артикулу
        if not brand:
            # Сначала ищем бренды по артикулу
            success, brands_data = self.get_abcp_brands(number=article.strip())
            
            if success and isinstance(brands_data, dict):
                all_results = []
                
                for key, brand_info in brands_data.items():
                    brand_name = brand_info.get('brand', '')
                    if brand_name:
                        # Ищем товары по найденному бренду
                        success, result = self._search_articles_by_brand(article, brand_name)
                        if success and isinstance(result, list):
                            all_results.extend(result)
                        elif success and result:
                            all_results.append(result)
                
                return True, all_results if all_results else []
            else:
                return False, f"Бренды по артикулу {article} не найдены"
        
        # Если указан конкретный бренд, ищем товары
        return self._search_articles_by_brand(article, brand)
        
    except Exception as e:
        return False, f"Ошибка поиска: {str(e)}"

def _search_articles_by_brand(self, article, brand):
    """Внутренний метод поиска товаров по артикулу и бренду"""
    try:
        # Создаем md5-хэш пароля
        password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
        
        # Формируем URL для поиска по артикулу
        search_url = f"{self.api_url.rstrip('/')}/search/articles"
        
        params = {
            'userlogin': self.api_login,
            'userpsw': password_hash,
            'number': article.strip(),
            'brand': brand.strip()
        }
        
        # Добавляем дополнительные параметры согласно документации
        if self.office_id:
            params['officeId'] = self.office_id
        
        if self.use_online_stocks:
            params['useOnlineStocks'] = 1
        
        # Добавляем адрес доставки если не самовывоз
        if self.default_shipment_address != '0':
            params['shipmentAddress'] = self.default_shipment_address
        
        response = requests.get(search_url, params=params, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Проверяем на ошибки в ответе
                if 'errorCode' in data:
                    error_code = data.get('errorCode')
                    error_message = data.get('errorMessage', 'Неизвестная ошибка')
                    return False, f"ABCP API ошибка {error_code}: {error_message}"
                
                # Если ответ успешный, возвращаем данные
                return True, data
                
            except json.JSONDecodeError:
                return False, "ABCP API: ошибка парсинга JSON ответа"
        elif response.status_code == 403:
            return False, f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
        else:
            return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Ошибка поиска по бренду: {str(e)}"
```

### 6. Добавление новых методов API

#### 🔧 Методы корзины

```python
# Добавить в класс Supplier:

def add_to_basket(self, supplier_code, item_key, quantity=1, comment=""):
    """Добавляет товар в корзину через ABCP API"""
    params = {
        'supplierCode': supplier_code,
        'itemKey': item_key,
        'quantity': quantity,
        'comment': comment
    }
    
    if self.default_shipment_address != '0':
        params['shipmentAddress'] = self.default_shipment_address
    
    return self._make_abcp_request('basket/add', params)

def get_basket_content(self, shipment_address=None):
    """Получает содержимое корзины"""
    params = {}
    
    address = shipment_address or self.default_shipment_address
    if address != '0':
        params['shipmentAddress'] = address
    
    return self._make_abcp_request('basket/content', params)

def clear_basket(self):
    """Очищает корзину"""
    return self._make_abcp_request('basket/clear')

def get_shipment_addresses(self):
    """Получает доступные адреса доставки"""
    return self._make_abcp_request('basket/shipmentAddresses')

def create_order_from_basket(self, payment_method, shipment_method, 
                           shipment_date, comment=""):
    """Создает заказ из корзины"""
    params = {
        'paymentMethod': payment_method,
        'shipmentMethod': shipment_method,
        'shipmentAddress': self.default_shipment_address,
        'shipmentDate': shipment_date,
        'comment': comment
    }
    
    return self._make_abcp_request('basket/order', params)

def search_batch(self, search_items):
    """Пакетный поиск товаров (до 100 позиций)"""
    if len(search_items) > 100:
        return False, "Максимум 100 позиций за один запрос"
    
    # Формируем параметры для POST запроса
    params = {
        'userlogin': self.api_login,
        'userpsw': hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
    }
    
    # Добавляем дополнительные параметры
    if self.office_id:
        params['officeId'] = self.office_id
    
    if self.use_online_stocks:
        params['useOnlineStocks'] = 1
    
    # Добавляем товары для поиска
    for i, item in enumerate(search_items):
        params[f'search[{i}][number]'] = item.get('number', '')
        params[f'search[{i}][brand]'] = item.get('brand', '')
    
    try:
        url = f"{self.api_url.rstrip('/')}/search/batch"
        response = requests.post(url, data=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errorCode' in data:
                error_code = data.get('errorCode')
                error_message = data.get('errorMessage', 'Неизвестная ошибка')
                return False, f"ABCP API ошибка {error_code}: {error_message}"
            
            return True, data
        else:
            return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Ошибка пакетного поиска: {str(e)}"

def get_search_history(self):
    """Получает историю поиска пользователя"""
    return self._make_abcp_request('search/history')

def get_search_tips(self, number_part):
    """Получает подсказки по поиску"""
    params = {'number': number_part}
    return self._make_abcp_request('search/tips', params)
```

### 7. Обновление кнопок в админке

#### 🔧 Добавление новых действий в admin.py

```python
# Добавить в SupplierAdmin новые actions:

def test_admin_api_connection(self, request, queryset):
    """Тестирует соединение с административным API"""
    results = []
    for supplier in queryset:
        if supplier.api_type == 'autoparts':
            success, message = supplier.get_staff_list()
            status = "✅ Успешно" if success else "❌ Ошибка"
            results.append(f"{supplier.name}: {status} - {message}")
        else:
            results.append(f"{supplier.name}: Не API автозапчастей")
    
    self.message_user(request, "\n".join(results))

test_admin_api_connection.short_description = "Тест административного API"

def sync_basket_methods(self, request, queryset):
    """Тестирует методы корзины"""
    results = []
    for supplier in queryset:
        if supplier.api_type == 'autoparts':
            # Тестируем получение содержимого корзины
            success, message = supplier.get_basket_content()
            status = "✅ Успешно" if success else "❌ Ошибка" 
            results.append(f"{supplier.name} корзина: {status}")
        else:
            results.append(f"{supplier.name}: Не API автозапчастей")
    
    self.message_user(request, "\n".join(results))

sync_basket_methods.short_description = "Тест методов корзины"

# Обновить список actions:
actions = [
    'test_api_connection',
    'test_admin_api_connection',    # Новое действие
    'sync_products',
    'sync_basket_methods',          # Новое действие
    'sync_all_entities',
    'view_supplier_products'
]
```

## 📋 Порядок выполнения

### Шаг 1 (5 минут)
1. Добавить новые поля в модель Supplier
2. Создать и применить миграцию

### Шаг 2 (10 минут)  
3. Обновить административную панель
4. Обновить метод _make_admin_request

### Шаг 3 (15 минут)
5. Добавить методы корзины и расширенного поиска
6. Обновить методы поиска для новых параметров

### Шаг 4 (10 минут)
7. Добавить новые действия в админку
8. Протестировать все изменения

## 🧪 Тестирование

После внесения изменений протестировать:

1. **Административные методы**: 
   - Зайти в админку поставщика
   - Нажать "Тест административного API"
   - Проверить работу синхронизации

2. **Методы корзины**:
   - Нажать "Тест методов корзины" 
   - Проверить получение содержимого

3. **Поиск с новыми параметрами**:
   - Заполнить office_id и useOnlineStocks
   - Протестировать поиск товаров

## ✅ Результат

После выполнения всех шагов интеграция с ABCP API будет:
- ✅ Полностью соответствовать официальной документации
- ✅ Поддерживать все обязательные параметры  
- ✅ Работать с административными методами
- ✅ Иметь функционал корзины
- ✅ Поддерживать расширенный поиск
- ✅ Готова к продуктивному использованию
