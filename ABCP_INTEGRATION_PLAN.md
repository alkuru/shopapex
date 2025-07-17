# План доработки интеграции ABCP API

## Критически важные изменения (2-4 часа работы)

### 1. Добавить поля для API-администратора

#### models.py - добавить в класс Supplier:
```python
# После строки api_password добавить:
admin_login = models.CharField(max_length=100, blank=True, verbose_name='Логин API-администратора')
admin_password = models.CharField(max_length=100, blank=True, verbose_name='Пароль API-администратора')
```

#### Создать миграцию:
```bash
python manage.py makemigrations catalog --name add_admin_credentials
python manage.py migrate
```

### 2. Обновить админку

#### admin.py - изменить fieldsets для SupplierAdmin:
```python
('API настройки', {
    'fields': (
        'api_type', 'api_url',
        ('api_login', 'api_password'),           # Клиентский доступ  
        ('admin_login', 'admin_password'),       # Административный доступ
        'api_key', 'api_secret', 'data_format', 'sync_frequency'
    ),
    'description': 'Клиентский доступ - для поиска товаров. Административный доступ - для управления заказами и клиентами.'
})
```

### 3. Создать метод для админских запросов

#### models.py - добавить в класс Supplier:
```python
def _make_admin_request(self, endpoint, params=None):
    """Универсальный метод для административных запросов к ABCP API"""
    if self.api_type != 'autoparts' or not self.api_url:
        return False, "API автозапчастей не настроен"
    
    if not self.admin_login or not self.admin_password:
        return False, "Логин или пароль API-администратора не настроены"
    
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

### 4. Обновить методы синхронизации

#### Заменить в методах sync_* вызовы _make_abcp_request на _make_admin_request:

```python
# В методах sync_staff, sync_delivery_methods, sync_order_statuses и т.д.
# Заменить:
success, data = self._make_abcp_request(endpoint, params)
# На:
success, data = self._make_admin_request(endpoint, params)
```

### 5. Добавить метод тестирования админского доступа

```python
def test_admin_api_connection(self):
    """Тестирует соединение с Admin API поставщика"""
    if not self.admin_login or not self.admin_password:
        return False, "Логин или пароль API-администратора не настроены"
    
    try:
        # Тестируем получение списка сотрудников
        success, data = self._make_admin_request('cp/managers')
        
        if success:
            return True, f"Admin API соединение успешно"
        else:
            return False, data
            
    except Exception as e:
        return False, f"Ошибка соединения с Admin API: {str(e)}"
```

### 6. Добавить кнопку тестирования в админку

#### admin.py - добавить в action_buttons для SupplierAdmin:
```python
if obj.admin_login and obj.admin_password:
    buttons.append(
        f'<a href="/admin/catalog/supplier/{obj.pk}/test-admin-api/" '
        f'class="button" style="margin-right: 5px; background-color: #007cba;">Тест Admin API</a>'
    )
```

#### Добавить URL и view:
```python
# В get_urls():
path('<int:supplier_id>/test-admin-api/', self.test_admin_api_view, name='supplier_test_admin_api'),

# Добавить метод:
def test_admin_api_view(self, request, supplier_id):
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
        success, message = supplier.test_admin_api_connection()
        
        if success:
            messages.success(request, f"Admin API тест успешен: {message}")
        else:
            messages.error(request, f"Admin API тест неудачен: {message}")
            
    except Supplier.DoesNotExist:
        messages.error(request, "Поставщик не найден")
    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
    
    return redirect(f'/admin/catalog/supplier/{supplier_id}/change/')
```

## После критических изменений

### Тестирование
1. Добавить в админку поставщика admin_login и admin_password
2. Протестировать кнопку "Тест Admin API"
3. Протестировать синхронизацию сущностей
4. Убедиться, что административные методы работают

### Дальнейшие доработки (по желанию)
1. Добавить недостающие административные методы из документации
2. Реализовать финансовые операции
3. Добавить расширенную работу с заказами
4. Реализовать управление пользователями

## Результат
После этих изменений интеграция с ABCP API будет полностью функциональной для всех основных операций.
