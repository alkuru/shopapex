from django.db import models
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
                    pass  # Игнорируем ошибки логирования
                
                raise e
        return wrapper
    return decorator


class Supplier(models.Model):
    # Склады Автоконтинент
    show_spb_north = models.BooleanField(default=True, verbose_name='СПб Север')
    show_spb_south = models.BooleanField(default=True, verbose_name='СПб Юг')
    show_moscow = models.BooleanField(default=True, verbose_name='Москва')
    show_other = models.BooleanField(default=True, verbose_name='Все остальные')
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
    api_login = models.CharField(max_length=100, blank=True, verbose_name='Логин API')
    api_password = models.CharField(max_length=100, blank=True, verbose_name='Пароль API')
    api_token = models.CharField(max_length=255, blank=True, verbose_name='API токен')
    
    # Настройки автозапчастей API (ABCP)
    office_id = models.CharField(max_length=20, blank=True, verbose_name='ID офиса')
    use_online_stocks = models.BooleanField(default=True, verbose_name='Использовать онлайн остатки')
    default_shipment_address = models.CharField(max_length=10, default='0', verbose_name='Адрес доставки по умолчанию')
    
    # Административные настройки для ABCP
    admin_login = models.CharField(max_length=100, blank=True, verbose_name='Admin логин')
    admin_password = models.CharField(max_length=100, blank=True, verbose_name='Admin пароль')
    # use_mock_admin_api полностью удалено
    
    # Настройки синхронизации
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
        """Возвращает данные для аутентификации API"""
        if self.api_login and self.api_password:
            return (self.api_login, self.api_password)
        return None

    def test_api_connection(self):
        """Тестирует соединение с API поставщика"""
        if not self.api_url:
            return False, "URL API не настроен"
        
        try:
            auth = self.get_api_auth()
            response = requests.get(self.api_url, auth=auth, timeout=10)
            if response.status_code == 200:
                return True, "Соединение успешно"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
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
            
            # URL для поиска
            search_url = f"{self.api_url.rstrip('/')}/search/articles"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash,
                'number': article.strip()
            }
            
            # Добавляем дополнительные параметры
            if self.office_id:
                params['officeId'] = self.office_id
            
            if self.use_online_stocks:
                params['useOnlineStocks'] = 1
                
            if brand:
                params['brand'] = brand.strip()
            
            response = requests.get(search_url, params=params, timeout=15)
            
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
                return False, "ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка поиска товаров: {str(e)}"
    
    def _search_articles_by_brand(self, article, brand):
        """Вспомогательный метод для поиска товаров конкретного бренда"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, []
        
        if not self.api_login or not self.api_password:
            return False, []
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # URL для поиска товаров
            search_url = f"{self.api_url.rstrip('/')}/search/articles"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash,
                'number': article.strip(),
                'brand': brand.strip(),
                'useOnlineStocks': 1 if self.use_online_stocks else 0
            }
            
            # Добавляем office_id если указан
            if self.office_id:
                params['officeId'] = self.office_id
            
            response = requests.get(search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Проверяем на ошибки в ответе
                    if isinstance(data, dict) and 'errorCode' in data:
                        return False, []
                    
                    return True, data if isinstance(data, list) else []
                    
                except json.JSONDecodeError:
                    return False, []
            else:
                return False, []
            
        except Exception as e:
            return False, []

    @monitor_api_call('get_abcp_brands')
    def get_abcp_brands(self, number=None):
        """Получение списка брендов из ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # URL для получения брендов
            brands_url = f"{self.api_url.rstrip('/')}/search/brands"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash
            }
            
            if number:
                params['number'] = number.strip()
            
            # Добавляем дополнительные параметры
            if self.office_id:
                params['officeId'] = self.office_id
            
            if self.use_online_stocks:
                params['useOnlineStocks'] = 1
            
            response = requests.get(brands_url, params=params, timeout=15)
            
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
                return False, "ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка получения брендов: {str(e)}"

    @monitor_api_call('get_abcp_user_info')
    def get_abcp_user_info(self):
        """Получение информации о пользователе из ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # URL для получения информации о пользователе
            user_url = f"{self.api_url.rstrip('/')}/cp/user"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash
            }
            
            response = requests.get(user_url, params=params, timeout=15)
            
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
                return False, "ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
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
            
            # Базовые параметры аутентификации
            base_params = {
                'userlogin': self.api_login,
                'userpsw': password_hash
            }
            
            # Добавляем переданные параметры
            if params:
                base_params.update(params)
            
            # Формируем URL
            url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
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
                return False, "ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка запроса к ABCP API: {str(e)}"

    def _make_admin_request(self, endpoint, params=None):
        """Универсальный метод для административных запросов к ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        # mock-логика полностью удалена, только реальные admin credentials
        if not self.admin_login or not self.admin_password:
            return False, "Admin логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.admin_password.encode('utf-8')).hexdigest()
            
            # Базовые параметры аутентификации
            base_params = {
                'userlogin': self.admin_login,
                'userpsw': password_hash
            }
            
            # Добавляем переданные параметры
            if params:
                base_params.update(params)
            
            # Формируем URL
            url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
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
                return False, "ABCP API: ошибка авторизации (403). Проверьте admin логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка admin запроса к ABCP API: {str(e)}"

    # mock-метод _get_mock_admin_data полностью удалён

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

    # Здесь будут добавлены остальные методы синхронизации и API...


# === МОДЕЛИ ДЛЯ ИНТЕГРАЦИИ С ПОСТАВЩИКАМИ И МОНИТОРИНГА API ===

class SupplierProduct(models.Model):
    delivery_time = models.CharField(max_length=64, blank=True, verbose_name='Срок поставки')
    """Товар поставщика (импортируется через API)"""
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='products', verbose_name='Поставщик')
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='supplier_products', verbose_name='Товар в каталоге')
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
