from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import requests
import json
import hashlib
from django.utils import timezone
import time
from functools import wraps

def monitor_api_call(method_name):
    """Декоратор для мониторинга API вызовов"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            request_data = {
                'args': args,
                'kwargs': {k: v for k, v in kwargs.items() if k not in ['password', 'userpsw']}
            }
            
            try:
                success, result = func(self, *args, **kwargs)
                response_time = time.time() - start_time
                
                # Создаем лог только если модель существует
                try:
                    APIMonitorLog.objects.create(
                        supplier=self,
                        method=method_name,
                        status='success' if success else 'error',
                        response_time=response_time,
                        request_data=request_data,
                        response_data={'success': success, 'data_length': len(str(result))},
                        error_message='' if success else str(result)
                    )
                except:
                    pass  # Игнорируем ошибки логирования
                
                return success, result
                
            except Exception as e:
                response_time = time.time() - start_time
                try:
                    APIMonitorLog.objects.create(
                        supplier=self,
                        method=method_name,
                        status='error',
                        response_time=response_time,
                        request_data=request_data,
                        response_data={},
                        error_message=str(e)
                    )
                except:
                    pass
                
                return False, str(e)
        
        return wrapper
    return decorator


class ProductCategory(models.Model):
    """Категории товаров (Кузовной каталог, Тормозные жидкости и т.д.)"""
    name = models.CharField(max_length=200, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Изображение')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'pk': self.pk})


class Brand(models.Model):
    """Бренды товаров"""
    name = models.CharField(max_length=100, verbose_name='Название бренда')
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name='Логотип')
    description = models.TextField(blank=True, verbose_name='Описание бренда')
    website = models.URLField(blank=True, verbose_name='Официальный сайт')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товары"""
    name = models.CharField(max_length=300, verbose_name='Название товара')
    article = models.CharField(max_length=100, unique=True, verbose_name='Артикул')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, verbose_name='Категория')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Цена со скидкой')
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_featured = models.BooleanField(default=False, verbose_name='Популярный товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Связь с основным поставщиком
    primary_supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, blank=True, null=True, 
                                       related_name='primary_products', verbose_name='Основной поставщик')
    
    # SEO поля
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='SEO заголовок')
    meta_description = models.TextField(blank=True, verbose_name='SEO описание')
    meta_keywords = models.CharField(max_length=300, blank=True, verbose_name='SEO ключевые слова')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article} - {self.name}"

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.pk})

    @property
    def final_price(self):
        """Возвращает итоговую цену с учетом скидки"""
        return self.discount_price if self.discount_price else self.price

    @property
    def in_stock(self):
        """Проверяет наличие товара на складе"""
        return self.stock_quantity > 0


class ProductImage(models.Model):
    """Изображения товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    is_main = models.BooleanField(default=False, verbose_name='Главное изображение')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order']

    def __str__(self):
        return f"Изображение {self.product.name}"


class ProductAnalog(models.Model):
    """Аналоги товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='analogs', verbose_name='Товар')
    analog_product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Аналог')

    class Meta:
        verbose_name = 'Аналог товара'
        verbose_name_plural = 'Аналоги товаров'
        unique_together = ['product', 'analog_product']

    def __str__(self):
        return f"Аналог {self.product.name} -> {self.analog_product.name}"


class Cart(models.Model):
    """Корзина покупок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_amount(self):
        """Общая сумма корзины"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Товары в корзине"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.product.final_price * self.quantity


class Supplier(models.Model):
    """Поставщики товаров"""
    SYNC_FREQUENCY_CHOICES = [
        ('hourly', 'Каждый час'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('manual', 'Только вручную'),
    ]
    
    DATA_FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('csv', 'CSV'),
    ]
    
    API_TYPE_CHOICES = [
        ('custom', 'Пользовательский API'),
        ('autoparts', 'API автозапчастей'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название поставщика')
    description = models.TextField(blank=True, verbose_name='Описание')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='Контактное лицо')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    website = models.URLField(blank=True, verbose_name='Сайт')
    
    # API настройки
    api_type = models.CharField(max_length=20, choices=API_TYPE_CHOICES, default='custom', verbose_name='Тип API')
    api_url = models.URLField(blank=True, verbose_name='URL API')
    api_login = models.CharField(max_length=100, blank=True, verbose_name='Логин API (клиентский)')
    api_password = models.CharField(max_length=100, blank=True, verbose_name='Пароль API (клиентский)')
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
    
    # Дополнительные параметры согласно документации ABCP API
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
    
    api_key = models.CharField(max_length=500, blank=True, verbose_name='API ключ')
    api_secret = models.CharField(max_length=500, blank=True, verbose_name='API секрет')
    data_format = models.CharField(max_length=10, choices=DATA_FORMAT_CHOICES, default='json', verbose_name='Формат данных')
    sync_frequency = models.CharField(max_length=20, choices=SYNC_FREQUENCY_CHOICES, default='manual', verbose_name='Частота синхронизации')
    
    # Настройки товаров
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Наценка (%)')
    auto_activate_products = models.BooleanField(default=False, verbose_name='Автоматически активировать товары')
    category_mapping = models.JSONField(default=dict, blank=True, verbose_name='Маппинг категорий')
    
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    last_sync_at = models.DateTimeField(blank=True, null=True, verbose_name='Последняя синхронизация')

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_api_auth(self):
        """Возвращает данные авторизации для API"""
        if self.api_login and self.api_password:
            return (self.api_login, self.api_password)
        return None

    def test_api_connection(self):
        """Тестирует соединение с API поставщика"""
        if not self.api_url:
            return False, "URL API не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            if self.api_type == 'autoparts':
                # Тестируем ABCP API - используем поиск брендов по простому артикулу
                success, brands_data = self.get_abcp_brands(number="TEST123")
                
                if success:
                    return True, f"ABCP API соединение успешно"
                else:
                    # Если ошибка не связана с авторизацией, считаем подключение рабочим
                    if "ошибка 4:" in brands_data or "Not enough parameters" in brands_data:
                        return True, f"ABCP API соединение успешно (ошибка параметров ожидаема)"
                    return False, brands_data
            else:
                # Стандартное тестирование
                headers = {}
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                response = requests.get(self.api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return True, "Соединение успешно"
                else:
                    return False, f"Ошибка HTTP: {response.status_code}"
                    
        except requests.exceptions.RequestException as e:
            return False, f"Ошибка соединения: {str(e)}"

    @monitor_api_call('search_products_by_article')
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
                    # brands_data имеет структуру {ключ: {brand: название, ...}}
                    all_results = []
                    
                    for key, brand_info in brands_data.items():
                        brand_name = brand_info.get('brand', '')
                        if brand_name:
                            # Ищем товары по найденному бренду
                            success, result = self._search_articles_by_brand(article, brand_name)
                            if success and isinstance(result, list):
                                all_results.extend(result)
                            elif success and result:  # Если результат не список, но есть данные
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
            
            # Добавляем дополнительные параметры согласно документации ABCP API
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

    @monitor_api_call('get_abcp_brands')
    def get_abcp_brands(self, number=None):
        """Получает список брендов из ABCP API (с опциональным поиском по артикулу)"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # Формируем URL для получения брендов
            brands_url = f"{self.api_url.rstrip('/')}/search/brands"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash
            }
            
            # Если указан артикул, добавляем его в параметры
            if number:
                params['number'] = number.strip()
            
            response = requests.get(brands_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Проверяем на ошибки в ответе
                    if 'errorCode' in data:
                        error_code = data.get('errorCode')
                        error_message = data.get('errorMessage', 'Неизвестная ошибка')
                        return False, f"ABCP API ошибка {error_code}: {error_message}"
                    
                    return True, data
                    
                except json.JSONDecodeError:
                    return False, "ABCP API: ошибка парсинга JSON ответа"
            elif response.status_code == 403:
                return False, f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка получения брендов: {str(e)}"

    @monitor_api_call('get_abcp_user_info')
    def get_abcp_user_info(self):
        """Получает информацию о пользователе из ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # Формируем URL для получения информации о пользователе
            user_info_url = f"{self.api_url.rstrip('/')}/user/info/"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash,
                'format': 'json'
            }
            
            response = requests.get(user_info_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Проверяем на ошибки в ответе
                    if 'errorCode' in data:
                        error_code = data.get('errorCode')
                        error_message = data.get('errorMessage', 'Неизвестная ошибка')
                        return False, f"ABCP API ошибка {error_code}: {error_message}"
                    
                    return True, data
                    
                except json.JSONDecodeError:
                    return False, "ABCP API: ошибка парсинга JSON ответа"
            elif response.status_code == 403:
                return False, f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка получения информации о пользователе: {str(e)}"

    def _make_abcp_request(self, endpoint, params=None):
        """Универсальный метод для выполнения запросов к ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # Формируем URL
            url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Базовые параметры авторизации
            base_params = {
                'userlogin': self.api_login,
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
                        return False, f"ABCP API ошибка {error_code}: {error_message}"
                    
                    return True, data
                    
                except json.JSONDecodeError:
                    return False, "ABCP API: ошибка парсинга JSON ответа"
            elif response.status_code == 403:
                return False, f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка запроса к ABCP API: {str(e)}"

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
            
            # Добавляем офис если указан
            if self.office_id:
                base_params['officeId'] = self.office_id
            
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

    def _get_mock_admin_data(self, endpoint, params=None):
        """Возвращает mock данные для административных endpoints для тестирования"""
        from django.utils import timezone
        
        mock_data = {
            'cp/managers': {
                'managers': [
                    {
                        'id': 1,
                        'name': 'Менеджер по продажам',
                        'email': 'manager@vinttop.ru',
                        'phone': '+7(999)123-45-67',
                        'role': 'manager',
                        'is_active': True
                    },
                    {
                        'id': 2, 
                        'name': 'Администратор',
                        'email': 'admin@vinttop.ru',
                        'phone': '+7(999)123-45-68',
                        'role': 'admin',
                        'is_active': True
                    }
                ]
            },
            'cp/statuses': {
                'statuses': [
                    {'id': 1, 'name': 'Новый', 'color': '#007bff', 'is_active': True},
                    {'id': 2, 'name': 'В обработке', 'color': '#ffc107', 'is_active': True},
                    {'id': 3, 'name': 'Отправлен', 'color': '#28a745', 'is_active': True},
                    {'id': 4, 'name': 'Доставлен', 'color': '#17a2b8', 'is_active': True},
                    {'id': 5, 'name': 'Отменен', 'color': '#dc3545', 'is_active': True}
                ]
            },
            'cp/users': {
                'users': [
                    {
                        'id': 1,
                        'name': 'Тестовый клиент 1',
                        'email': 'client1@example.com',
                        'phone': '+7(999)111-11-11',
                        'group_id': 1,
                        'manager_id': 1,
                        'balance': 5000.00,
                        'is_active': True,
                        'created_at': timezone.now().isoformat()
                    },
                    {
                        'id': 2,
                        'name': 'Тестовый клиент 2', 
                        'email': 'client2@example.com',
                        'phone': '+7(999)222-22-22',
                        'group_id': 1,
                        'manager_id': 1,
                        'balance': 3000.00,
                        'is_active': True,
                        'created_at': timezone.now().isoformat()
                    }
                ]
            },
            'cp/orders': {
                'orders': [
                    {
                        'id': 1,
                        'number': 'ORD-001',
                        'client_id': 1,
                        'status_id': 2,
                        'total_amount': 15000.00,
                        'created_at': timezone.now().isoformat(),
                        'items': [
                            {
                                'id': 1,
                                'article': '0986424815',
                                'name': 'Комплект тормозных колодок',
                                'brand': 'BOSCH',
                                'quantity': 1,
                                'price': 15000.00
                            }
                        ]
                    }
                ]
            },
            'cp/route': {
                'delivery_methods': [
                    {
                        'id': 1,
                        'name': 'Самовывоз',
                        'description': 'Забрать товар самостоятельно',
                        'price': 0,
                        'days_min': 1,
                        'days_max': 2,
                        'is_active': True
                    },
                    {
                        'id': 2,
                        'name': 'Курьерская доставка',
                        'description': 'Доставка курьером по городу',
                        'price': 500,
                        'days_min': 1,
                        'days_max': 3,
                        'is_active': True
                    }
                ]
            }
        }
        
        if endpoint in mock_data:
            return True, mock_data[endpoint]
        else:
            return False, f"Mock данные для {endpoint} не найдены"
    
    def sync_products(self):
        """Синхронизирует товары с API поставщика"""
        if not self.api_url:
            return False, "URL API не настроен"
        
        try:
            # Создаем лог синхронизации
            sync_log = SupplierSyncLog.objects.create(
                supplier=self,
                status='in_progress',
                message='Начата синхронизация'
            )
            
            updated_count = 0
            created_count = 0
            error_count = 0
            
            if self.api_type == 'autoparts':
                # Для API автозапчастей нужно сначала получить список артикулов
                # В данном случае будем обновлять существующие товары
                existing_products = self.products.all()
                
                for supplier_product in existing_products:
                    try:
                        success, result = self.search_products_by_article(supplier_product.supplier_article)
                        
                        if success and 'products' in result:
                            products = result['products']
                            
                            # Находим наш товар в результатах
                            matching_product = None
                            for product in products:
                                if (product.get('article') == supplier_product.supplier_article and 
                                    product.get('brand') == supplier_product.data.get('brand')):
                                    matching_product = product
                                    break
                            
                            if matching_product:
                                # Обновляем товар
                                supplier_product.name = matching_product.get('name', supplier_product.name)
                                supplier_product.price = matching_product.get('price', supplier_product.price)
                                supplier_product.stock_quantity = max(0, matching_product.get('stock', 0))
                                supplier_product.data = matching_product
                                supplier_product.save()
                                updated_count += 1
                                
                    except Exception as e:
                        error_count += 1
                        continue
                        
            else:
                # Стандартная синхронизация для пользовательского API
                headers = {}
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                response = requests.get(self.api_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                if self.data_format == 'json':
                    data = response.json()
                else:
                    return False, f"Формат данных {self.data_format} пока не поддерживается"
                
                products_data = data.get('products', []) if isinstance(data, dict) else data
                
                for product_data in products_data:
                    try:
                        article = product_data.get('article') or product_data.get('sku')
                        if not article:
                            error_count += 1
                            continue
                        
                        supplier_product, created = SupplierProduct.objects.get_or_create(
                            supplier=self,
                            supplier_article=article,
                            defaults={
                                'name': product_data.get('name', ''),
                                'price': product_data.get('price', 0),
                                'stock_quantity': product_data.get('stock', 0),
                                'data': product_data
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            supplier_product.name = product_data.get('name', supplier_product.name)
                            supplier_product.price = product_data.get('price', supplier_product.price)
                            supplier_product.stock_quantity = product_data.get('stock', supplier_product.stock_quantity)
                            supplier_product.data = product_data
                            supplier_product.save()
                            updated_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        continue
            
            # Обновляем лог
            sync_log.status = 'completed'
            sync_log.message = f'Синхронизация завершена. Создано: {created_count}, Обновлено: {updated_count}, Ошибок: {error_count}'
            sync_log.products_created = created_count
            sync_log.products_updated = updated_count
            sync_log.errors_count = error_count
            sync_log.save()
            
            # Обновляем время последней синхронизации
            self.last_sync_at = timezone.now()
            self.save()
            
            return True, sync_log.message
            
        except Exception as e:
            # Создаем лог ошибки
            SupplierSyncLog.objects.create(
                supplier=self,
                status='error',
                message=f'Ошибка синхронизации: {str(e)}'
            )
            return False, f"Ошибка синхронизации: {str(e)}"

    # === ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ API АВТОЗАПЧАСТЕЙ ===
    
    def get_staff_list(self):
        """Получает список сотрудников через административный API"""
        return self._make_admin_request('cp/managers')
    
    def get_delivery_methods(self):
        """Получает список способов доставки через административный API"""
        return self._make_admin_request('cp/route')
    
    def get_order_statuses(self):
        """Получает список статусов заказов через административный API"""
        return self._make_admin_request('cp/statuses')
    
    def get_client_groups(self):
        """Получает список групп клиентов через административный API"""
        return self._make_admin_request('cp/users/groups')
    
    def get_clients_list(self, group_id=None, manager_id=None, limit=100, offset=0):
        """Получает список клиентов с возможностью фильтрации через административный API"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if group_id:
            params['group_id'] = group_id
        if manager_id:
            params['manager_id'] = manager_id
            
        return self._make_admin_request('cp/users', params)
    
    def get_client_detail(self, client_id):
        """Получает детальную информацию о клиенте"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/client/{client_id}"
            auth = self.get_api_auth()
            
            response = requests.get(url, auth=auth, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка получения информации о клиенте: {str(e)}"
    
    def create_client(self, client_data):
        """Создает нового клиента"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/client"
            auth = self.get_api_auth()
            
            response = requests.post(url, auth=auth, json=client_data, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка создания клиента: {str(e)}"
    
    def update_client(self, client_id, client_data):
        """Обновляет данные клиента"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/client/{client_id}"
            auth = self.get_api_auth()
            
            response = requests.put(url, auth=auth, json=client_data, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка обновления клиента: {str(e)}"
    
    def get_client_balance(self, client_id):
        """Получает баланс клиента"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/client/{client_id}/balance"
            auth = self.get_api_auth()
            
            response = requests.get(url, auth=auth, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка получения баланса клиента: {str(e)}"
    
    def add_client_balance(self, client_id, amount, description=""):
        """Пополняет баланс клиента"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/client/{client_id}/balance"
            auth = self.get_api_auth()
            
            data = {
                'amount': amount,
                'description': description
            }
            
            response = requests.post(url, auth=auth, json=data, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка пополнения баланса: {str(e)}"
    
    def get_orders_list(self, client_id=None, status_id=None, limit=100, offset=0):
        """Получает список заказов с возможностью фильтрации через административный API"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if client_id:
            params['client_id'] = client_id
        if status_id:
            params['status_id'] = status_id
            
        return self._make_admin_request('cp/orders', params)
    
    def get_order_detail(self, order_id):
        """Получает детальную информацию о заказе"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/order/{order_id}"
            auth = self.get_api_auth()
            
            response = requests.get(url, auth=auth, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка получения информации о заказе: {str(e)}"
    
    def create_order(self, order_data):
        """Создает новый заказ"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/order"
            auth = self.get_api_auth()
            
            response = requests.post(url, auth=auth, json=order_data, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка создания заказа: {str(e)}"
    
    def update_order_status(self, order_id, status_id, comment=""):
        """Обновляет статус заказа"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/order/{order_id}/status"
            auth = self.get_api_auth()
            
            data = {
                'status_id': status_id,
                'comment': comment
            }
            
            response = requests.put(url, auth=auth, json=data, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка обновления статуса заказа: {str(e)}"
    
    def get_order_history(self, order_id):
        """Получает историю изменений заказа"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/order/{order_id}/history"
            auth = self.get_api_auth()
            
            response = requests.get(url, auth=auth, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка получения истории заказа: {str(e)}"
    
    def search_parts_by_vin(self, vin_code, part_name=None):
        """Поиск запчастей по VIN коду"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        try:
            url = f"{self.api_url.rstrip('/')}/panel/parts/vin/{vin_code}"
            auth = self.get_api_auth()
            
            params = {}
            if part_name:
                params['part_name'] = part_name
            
            response = requests.get(url, auth=auth, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return True, data
            
        except Exception as e:
            return False, f"Ошибка поиска по VIN: {str(e)}"
    
    # === МЕТОДЫ СИНХРОНИЗАЦИИ СУЩНОСТЕЙ ===
    
    def sync_staff(self):
        """Синхронизирует сотрудников с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        try:
            success, data = self.get_staff_list()
            if not success:
                return False, data
            
            staff_list = data.get('staff', [])
            updated_count = 0
            created_count = 0
            
            for staff_data in staff_list:
                external_id = str(staff_data.get('id'))
                
                staff, created = SupplierStaff.objects.update_or_create(
                    supplier=self,
                    external_id=external_id,
                    defaults={
                        'name': staff_data.get('name', ''),
                        'email': staff_data.get('email', ''),
                        'phone': staff_data.get('phone', ''),
                        'role': staff_data.get('role', ''),
                        'is_active': staff_data.get('is_active', True),
                        'data': staff_data
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return True, f"Синхронизировано сотрудников: {created_count} создано, {updated_count} обновлено"
            
        except Exception as e:
            return False, f"Ошибка синхронизации сотрудников: {str(e)}"
    
    def sync_delivery_methods(self):
        """Синхронизирует способы доставки с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        try:
            success, data = self.get_delivery_methods()
            if not success:
                return False, data
            
            delivery_list = data.get('delivery_methods', [])
            updated_count = 0
            created_count = 0
            
            for delivery_data in delivery_list:
                external_id = str(delivery_data.get('id'))
                
                delivery, created = SupplierDeliveryMethod.objects.update_or_create(
                    supplier=self,
                    external_id=external_id,
                    defaults={
                        'name': delivery_data.get('name', ''),
                        'description': delivery_data.get('description', ''),
                        'price': delivery_data.get('price', 0),
                        'days_min': delivery_data.get('days_min', 1),
                        'days_max': delivery_data.get('days_max', 7),
                        'is_active': delivery_data.get('is_active', True),
                        'data': delivery_data
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return True, f"Синхронизировано способов доставки: {created_count} создано, {updated_count} обновлено"
            
        except Exception as e:
            return False, f"Ошибка синхронизации способов доставки: {str(e)}"
    
    def sync_order_statuses(self):
        """Синхронизирует статусы заказов с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        try:
            success, data = self.get_order_statuses()
            if not success:
                return False, data
            
            statuses_list = data.get('statuses', [])
            updated_count = 0
            created_count = 0
            
            for status_data in statuses_list:
                external_id = str(status_data.get('id'))
                
                status, created = SupplierOrderStatus.objects.update_or_create(
                    supplier=self,
                    external_id=external_id,
                    defaults={
                        'name': status_data.get('name', ''),
                        'description': status_data.get('description', ''),
                        'color': status_data.get('color', '#6c757d'),
                        'is_final': status_data.get('is_final', False),
                        'notify_client': status_data.get('notify_client', True),
                        'data': status_data
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return True, f"Синхронизировано статусов: {created_count} создано, {updated_count} обновлено"
            
        except Exception as e:
            return False, f"Ошибка синхронизации статусов: {str(e)}"
    
    def sync_client_groups(self):
        """Синхронизирует группы клиентов с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        try:
            success, data = self.get_client_groups()
            if not success:
                return False, data
            
            groups_list = data.get('groups', [])
            updated_count = 0
            created_count = 0
            
            for group_data in groups_list:
                external_id = str(group_data.get('id'))
                
                group, created = SupplierClientGroup.objects.update_or_create(
                    supplier=self,
                    external_id=external_id,
                    defaults={
                        'name': group_data.get('name', ''),
                        'description': group_data.get('description', ''),
                        'discount_percentage': group_data.get('discount_percentage', 0),
                        'data': group_data
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return True, f"Синхронизировано групп клиентов: {created_count} создано, {updated_count} обновлено"
            
        except Exception as e:
            return False, f"Ошибка синхронизации групп клиентов: {str(e)}"
    
    def sync_clients(self, limit=100):
        """Синхронизирует клиентов с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        try:
            success, data = self.get_clients_list(limit=limit)
            if not success:
                return False, data
            
            clients_list = data.get('clients', [])
            updated_count = 0
            created_count = 0
            
            for client_data in clients_list:
                external_id = str(client_data.get('id'))
                
                # Находим группу и менеджера если указаны
                group = None
                if client_data.get('group_id'):
                    try:
                        group = self.client_groups.get(external_id=str(client_data['group_id']))
                    except SupplierClientGroup.DoesNotExist:
                        pass
                
                manager = None
                if client_data.get('manager_id'):
                    try:
                        manager = self.staff.get(external_id=str(client_data['manager_id']))
                    except SupplierStaff.DoesNotExist:
                        pass
                
                client, created = SupplierClient.objects.update_or_create(
                    supplier=self,
                    external_id=external_id,
                    defaults={
                        'name': client_data.get('name', ''),
                        'email': client_data.get('email', ''),
                        'phone': client_data.get('phone', ''),
                        'address': client_data.get('address', ''),
                        'group': group,
                        'manager': manager,
                        'balance': client_data.get('balance', 0),
                        'is_active': client_data.get('is_active', True),
                        'data': client_data
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return True, f"Синхронизировано клиентов: {created_count} создано, {updated_count} обновлено"
            
        except Exception as e:
            return False, f"Ошибка синхронизации клиентов: {str(e)}"
    
    def sync_orders(self, limit=100):
        """Синхронизирует заказы с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        try:
            success, data = self.get_orders_list(limit=limit)
            if not success:
                return False, data
            
            orders_list = data.get('orders', [])
            updated_count = 0
            created_count = 0
            
            for order_data in orders_list:
                external_id = str(order_data.get('id'))
                
                # Находим связанные объекты
                client = None
                if order_data.get('client_id'):
                    try:
                        client = self.clients.get(external_id=str(order_data['client_id']))
                    except SupplierClient.DoesNotExist:
                        pass
                
                status = None
                if order_data.get('status_id'):
                    try:
                        status = self.order_statuses.get(external_id=str(order_data['status_id']))
                    except SupplierOrderStatus.DoesNotExist:
                        pass
                
                delivery_method = None
                if order_data.get('delivery_id'):
                    try:
                        delivery_method = self.delivery_methods.get(external_id=str(order_data['delivery_id']))
                    except SupplierDeliveryMethod.DoesNotExist:
                        pass
                
                order, created = SupplierOrder.objects.update_or_create(
                    supplier=self,
                    external_id=external_id,
                    defaults={
                        'number': order_data.get('number', ''),
                        'client': client,
                        'status': status,
                        'delivery_method': delivery_method,
                        'total_amount': order_data.get('total_amount', 0),
                        'delivery_cost': order_data.get('delivery_cost', 0),
                        'comment': order_data.get('comment', ''),
                        'data': order_data
                    }
                )
                
                # Синхронизируем позиции заказа
                if 'items' in order_data:
                    # Удаляем старые позиции
                    order.items.all().delete()
                    
                    for item_data in order_data['items']:
                        # Находим товар по артикулу
                        product = None
                        article = item_data.get('article', '')
                        if article:
                            try:
                                product = self.products.get(supplier_article=article)
                            except SupplierProduct.DoesNotExist:
                                pass
                        
                        SupplierOrderItem.objects.create(
                            order=order,
                            product=product,
                            article=article,
                            name=item_data.get('name', ''),
                            brand=item_data.get('brand', ''),
                            quantity=item_data.get('quantity', 1),
                            price=item_data.get('price', 0),
                            data=item_data
                        )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return True, f"Синхронизировано заказов: {created_count} создано, {updated_count} обновлено"
            
        except Exception as e:
            return False, f"Ошибка синхронизации заказов: {str(e)}"
    
    def sync_all_entities(self):
        """Синхронизирует все сущности с API"""
        if self.api_type != 'autoparts':
            return False, "Метод доступен только для API автозапчастей"
        
        results = []
        
        # Синхронизируем в правильном порядке (учитывая зависимости)
        sync_methods = [
            ('Сотрудники', self.sync_staff),
            ('Способы доставки', self.sync_delivery_methods),
            ('Статусы заказов', self.sync_order_statuses),
            ('Группы клиентов', self.sync_client_groups),
            ('Клиенты', self.sync_clients),
            ('Товары', self.sync_products),
            ('Заказы', self.sync_orders),
        ]
        
        for entity_name, method in sync_methods:
            try:
                success, message = method()
                results.append(f"{entity_name}: {message}")
            except Exception as e:
                results.append(f"{entity_name}: Ошибка - {str(e)}")
        
        return True, "\n".join(results)

    # === МЕТОДЫ КОРЗИНЫ СОГЛАСНО ДОКУМЕНТАЦИИ ABCP API ===
    
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

    # === РАСШИРЕННЫЕ МЕТОДЫ ПОИСКА ===
    
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

    @monitor_api_call('get_product_analogs')
    def get_product_analogs(self, article, brand=None, limit=20):
        """Получение аналогов товара по артикулу через ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # Получаем список брендов по артикулу (это и есть аналоги)
            brands_url = f"{self.api_url.rstrip('/')}/search/brands"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash,
                'number': article.strip(),
                'useOnlineStocks': 1 if self.use_online_stocks else 0
            }
            
            # Добавляем office_id если указан
                if self.office_id:
                    params['officeId'] = self.office_id
                
                response = requests.get(brands_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    try:
                        brands_data = response.json()
                                            # Проверяем на ошибки в ответе
                        if isinstance(brands_data, dict) and 'errorCode' in brands_data:
                        
                        # Проверяем на ошибки в ответе
                        
                            error_code = brands_data.get('errorCode')
                            error_message = brands_data.get('errorMessage', 'Неизвестная ошибка')
                            return False, f"ABCP API ошибка {error_code}: {error_message}"
                        
                        # Если указан конкретный бренд, фильтруем
                        if brand:
                            brands_data = [b for b in brands_data if isinstance(b, dict) and b.get('brand', '').lower() == brand.lower()]
                            if isinstance(brands_data, dict):
                                brands_list = []
                                for key, value in brands_data.items():
                                    if isinstance(value, dict) and ('brand' in value or 'number' in value):
                                        brands_list.append(value)
                                brands_data = brands_list
                            # Ограничиваем количество результатов
                            if limit and len(brands_data) > limit:
                                brands_data = brands_data[:limit]
                            
                            # Для каждого бренда получаем детальную информацию
                            analogs = []
                            for brand_info in brands_data:
                            # Проверяем что это действительно словарь
                                if not isinstance(brand_info, dict):
                                    continue
                                brand_name = brand_info.get('brand', '')
                                article_code = brand_info.get('number', article)
                                
                                
                                
                                # Получаем детальную информацию о товарах этого бренда
                                success, articles_data = self._search_articles_by_brand(article_code, brand_name)
                                
                                if success and articles_data:
                                    for product in articles_data:
                                 # Проверяем что product - словарь перед вызовом .get()
                                        if not isinstance(product, dict):
                                           continue
                                            
                                        analog = {
                                            'article': product.get('articleCode', article_code),
                                            'article_fix': product.get('articleCodeFix', article_code),
                                            'brand': product.get('brand', brand_name),
                                            'name': product.get('description', ''),
                                            'price': product.get('price', 0),
                                            'availability': product.get('availability', 0),
                                            'delivery_period': product.get('deliveryPeriod', 0),
                                            'weight': product.get('weight', '0'),
                                            'article_id': product.get('articleId', ''),
                                            'is_original': brand_name.lower() == brand.lower() if brand else False
                                        }
                                        analogs.append(analog)
                            
                            return True, {
                                'original_article': article,
                                'original_brand': brand or '',
                                'total_found': len(analogs),
                                'analogs': analogs
                            }
                            
                        except json.JSONDecodeError:
                            return False, "ABCP API: ошибка парсинга JSON ответа"
                    elif response.status_code == 403:
                        return False, f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
                    else:
                        return False, f"ABCP API: ошибка HTTP {response.status_code}"
                    
            except Exception as e:
                return False, f"Ошибка поиска аналогов: {str(e)}"
    # === МОДЕЛИ ДЛЯ ИНТЕГРАЦИИ С ПОСТАВЩИКАМИ И МОНИТОРИНГА API ===

    class SupplierProduct(models.Model):
        """Товар поставщика (импортируется через API)"""
        supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='products', verbose_name='Поставщик')
        product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='supplier_products', verbose_name='Товар в каталоге')
        article = models.CharField(max_length=64, db_index=True, verbose_name='Артикул')
        brand = models.CharField(max_length=64, db_index=True, verbose_name='Бренд')
        name = models.CharField(max_length=255, verbose_name='Название')
        price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
        availability = models.IntegerField(default=0, verbose_name='Доступно')
        is_active = models.BooleanField(default=True, verbose_name='Активен')
        updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
        created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

        class Meta:
            verbose_name = 'Товар поставщика'
            verbose_name_plural = 'Товары поставщиков'
            indexes = [
                models.Index(fields=['article', 'brand']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.article} {self.brand} ({self.supplier.name})"


class SupplierSyncLog(models.Model):
    """Лог синхронизации товаров поставщика"""
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='sync_logs', verbose_name='Поставщик')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Время начала')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')
    status = models.CharField(max_length=32, choices=[('success', 'Успешно'), ('error', 'Ошибка'), ('in_progress', 'В процессе')], default='in_progress', verbose_name='Статус')
    products_created = models.PositiveIntegerField(default=0, verbose_name='Создано товаров')
    products_updated = models.PositiveIntegerField(default=0, verbose_name='Обновлено товаров')
    errors_count = models.PositiveIntegerField(default=0, verbose_name='Ошибок')
    message = models.TextField(blank=True, verbose_name='Сообщение/лог')

    class Meta:
        verbose_name = 'Лог синхронизации поставщика'
        verbose_name_plural = 'Логи синхронизации поставщиков'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.supplier.name} ({self.started_at:%Y-%m-%d %H:%M}) [{self.status}]"


class APIMonitorLog(models.Model):
    """Лог мониторинга состояния API поставщика"""
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='api_monitor_logs', verbose_name='Поставщик')
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='Время проверки')
    response_time = models.FloatField(verbose_name='Время ответа (сек)')
    status = models.CharField(max_length=16, choices=[('success', 'Успешно'), ('error', 'Ошибка')], verbose_name='Статус')
    method = models.CharField(max_length=64, verbose_name='Метод API')
    request_data = models.JSONField(default=dict, blank=True, verbose_name='Данные запроса')
    response_data = models.JSONField(default=dict, blank=True, verbose_name='Данные ответа')
    error_message = models.TextField(blank=True, verbose_name='Ошибка')

    class Meta:
        verbose_name = 'Лог мониторинга API'
        verbose_name_plural = 'Логи мониторинга API'
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.supplier.name} [{self.checked_at:%Y-%m-%d %H:%M}] - {self.status}"


class APIHealthCheck(models.Model):
    """Периодическая проверка доступности API"""
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='api_health_checks', verbose_name='Поставщик')
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='Время проверки')
    is_available = models.BooleanField(default=True, verbose_name='API доступен')
    response_time = models.FloatField(null=True, blank=True, verbose_name='Время ответа (сек)')
    status_code = models.IntegerField(null=True, blank=True, verbose_name='HTTP статус')
    error_message = models.TextField(blank=True, verbose_name='Ошибка')

    class Meta:
        verbose_name = 'Проверка доступности API'
        verbose_name_plural = 'Проверки доступности API'
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.supplier.name} [{self.checked_at:%Y-%m-%d %H:%M}] - {'OK' if self.is_available else 'FAIL'}"


class SupplierStaff(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='staff', verbose_name='Поставщик')
    name = models.CharField(max_length=128, verbose_name='Имя')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=32, blank=True, verbose_name='Телефон')
    role = models.CharField(max_length=64, blank=True, verbose_name='Роль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные сотрудника')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    external_id = models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Внешний ID')

    class Meta:
        verbose_name = 'Сотрудник поставщика'
        verbose_name_plural = 'Сотрудники поставщика'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class SupplierDeliveryMethod(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='delivery_methods', verbose_name='Поставщик')
    name = models.CharField(max_length=128, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость')
    days_min = models.PositiveIntegerField(default=1, verbose_name='Мин. дней')
    days_max = models.PositiveIntegerField(default=7, verbose_name='Макс. дней')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные способа доставки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    external_id = models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Внешний ID')

    class Meta:
        verbose_name = 'Способ доставки поставщика'
        verbose_name_plural = 'Способы доставки поставщика'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class SupplierOrderStatus(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='order_statuses', verbose_name='Поставщик')
    name = models.CharField(max_length=64, verbose_name='Статус')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=16, default='#6c757d', verbose_name='Цвет')
    is_final = models.BooleanField(default=False, verbose_name='Финальный статус')
    notify_client = models.BooleanField(default=True, verbose_name='Уведомлять клиента')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные статуса')
    external_id = models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Внешний ID')

    class Meta:
        verbose_name = 'Статус заказа поставщика'
        verbose_name_plural = 'Статусы заказов поставщика'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class SupplierClientGroup(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='client_groups', verbose_name='Поставщик')
    name = models.CharField(max_length=128, verbose_name='Название группы')
    description = models.TextField(blank=True, verbose_name='Описание')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Скидка (%)')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные группы')
    external_id = models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Внешний ID')

    class Meta:
        verbose_name = 'Группа клиентов поставщика'
        verbose_name_plural = 'Группы клиентов поставщика'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class SupplierClient(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='clients', verbose_name='Поставщик')
    group = models.ForeignKey('SupplierClientGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients', verbose_name='Группа')
    manager = models.ForeignKey('SupplierStaff', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients', verbose_name='Менеджер')
    name = models.CharField(max_length=128, verbose_name='Имя клиента')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=32, blank=True, verbose_name='Телефон')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Баланс')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные клиента')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    external_id = models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Внешний ID')

    class Meta:
        verbose_name = 'Клиент поставщика'
        verbose_name_plural = 'Клиенты поставщика'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class SupplierOrder(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='orders', verbose_name='Поставщик')
    client = models.ForeignKey('SupplierClient', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Клиент')
    status = models.ForeignKey('SupplierOrderStatus', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Статус')
    delivery_method = models.ForeignKey('SupplierDeliveryMethod', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Способ доставки')
    number = models.CharField(max_length=64, blank=True, verbose_name='Номер заказа')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма заказа')
    delivery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Стоимость доставки')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные заказа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    external_id = models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Внешний ID')

    class Meta:
        verbose_name = 'Заказ поставщика'
        verbose_name_plural = 'Заказы поставщика'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ {self.number or self.id} ({self.supplier.name})"


class SupplierOrderItem(models.Model):
    order = models.ForeignKey('SupplierOrder', on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey('SupplierProduct', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items', verbose_name='Товар поставщика')
    article = models.CharField(max_length=64, blank=True, verbose_name='Артикул')
    name = models.CharField(max_length=255, blank=True, verbose_name='Название')
    brand = models.CharField(max_length=64, blank=True, verbose_name='Бренд')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена за единицу')
    data = models.JSONField(default=dict, blank=True, verbose_name='Данные позиции')

    class Meta:
        verbose_name = 'Позиция заказа поставщика'
        verbose_name_plural = 'Позиции заказов поставщика'

    def __str__(self):
        return f"{self.name or self.article} x {self.quantity}"


class SupplierOrderHistory(models.Model):
    order = models.ForeignKey('SupplierOrder', on_delete=models.CASCADE, related_name='history', verbose_name='Заказ')
    status = models.ForeignKey('SupplierOrderStatus', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статус')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'История заказа поставщика'
        verbose_name_plural = 'История заказов поставщика'
        ordering = ['-changed_at']

    def __str__(self):
        return f"История заказа {self.order_id} ({self.status})"


class SupplierBalanceTransaction(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='balance_transactions', verbose_name='Поставщик')
    client = models.ForeignKey('SupplierClient', on_delete=models.SET_NULL, null=True, blank=True, related_name='balance_transactions', verbose_name='Клиент')
    staff = models.ForeignKey('SupplierStaff', on_delete=models.SET_NULL, null=True, blank=True, related_name='balance_transactions', verbose_name='Сотрудник')
    order = models.ForeignKey('SupplierOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='balance_transactions', verbose_name='Заказ')
    transaction_type = models.CharField(max_length=32, choices=[('in', 'Пополнение'), ('out', 'Списание')], verbose_name='Тип транзакции')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Транзакция баланса поставщика'
        verbose_name_plural = 'Транзакции баланса поставщика'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} ({self.supplier.name})"