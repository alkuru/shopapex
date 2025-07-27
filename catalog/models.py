from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Настройки отображения складов для фильтрации в каталоге
class WarehouseSettings(models.Model):
    show_spb_north = models.BooleanField(default=True, verbose_name='СПб Север')
    show_spb_south = models.BooleanField(default=True, verbose_name='СПб Юг')
    show_moscow = models.BooleanField(default=True, verbose_name='Москва')
    show_other = models.BooleanField(default=True, verbose_name='Все другие')
    show_avtosp = models.BooleanField(default=True, verbose_name='Авто-Сп')

    class Meta:
        verbose_name = 'Настройки складов'
        verbose_name_plural = 'Настройки складов'

    def __str__(self):
        return 'Настройки складов'



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
    RATING_CHOICES = [
        (5, '5★ Премиум'),
        (4, '4★ Хорошее'),
        (3, '3★ Средний'),
        (2, '2★ Низкий'),
        (1, '1★ Плохой'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название бренда')
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name='Логотип')
    description = models.TextField(blank=True, verbose_name='Описание бренда')
    website = models.URLField(blank=True, verbose_name='Официальный сайт')
    online_catalog = models.URLField(blank=True, verbose_name='Онлайн каталог')
    country_iso = models.CharField(max_length=2, blank=True, verbose_name='ISO-код страны (например, pl, de, cn)')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, blank=True, null=True, verbose_name='Рейтинг бренда')
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
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Закупочная цена')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Цена со скидкой')
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    delivery_time = models.CharField(max_length=100, blank=True, verbose_name='Срок поставки')
    warehouse = models.CharField(max_length=100, blank=True, verbose_name='Склад')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_featured = models.BooleanField(default=False, verbose_name='Популярный товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Связь с основным поставщиком (временно отключено для исправления ошибки)
    # primary_supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, blank=True, null=True, 
    #                                    related_name='primary_products', verbose_name='Основной поставщик')
    
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


class OemNumber(models.Model):
    """Оригинальные номера запчастей (OEM)"""
    number = models.CharField(max_length=100, verbose_name='OEM номер')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'OEM номер'
        verbose_name_plural = 'OEM номера'
        unique_together = ['number', 'manufacturer']
        ordering = ['manufacturer', 'number']

    def __str__(self):
        return f"{self.manufacturer} {self.number}"


class ProductOem(models.Model):
    """Связь товаров с OEM номерами"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='oem_numbers', verbose_name='Товар')
    oem_number = models.ForeignKey(OemNumber, on_delete=models.CASCADE, related_name='products', verbose_name='OEM номер')
    is_main = models.BooleanField(default=False, verbose_name='Основной номер')

    class Meta:
        verbose_name = 'OEM номер товара'
        verbose_name_plural = 'OEM номера товаров'
        unique_together = ['product', 'oem_number']

    def __str__(self):
        return f"{self.product.article} -> {self.oem_number}"


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


# Импортируем модели поставщиков из отдельного файла
from .supplier_models import *

# Импорт моделей умного поиска для регистрации в ORM
from .smart_search_models import SearchCache, SearchHistory, SavedProduct, OrderedProduct


class AutoKontinentProduct(models.Model):
    """Товары из прайса АвтоКонтинента"""
    brand = models.CharField(max_length=100, verbose_name='Бренд')
    article = models.CharField(max_length=100, verbose_name='Код товара')
    name = models.CharField(max_length=300, verbose_name='Наименование товара')
    stock_spb = models.PositiveIntegerField(default=0, verbose_name='Кол-во СПб')
    stock_msk = models.PositiveIntegerField(default=0, verbose_name='Кол-во МСК')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    multiplicity = models.PositiveIntegerField(default=1, verbose_name='Кратность')
    unit = models.CharField(max_length=20, verbose_name='Ед. изм.')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Товар АвтоКонтинента'
        verbose_name_plural = 'Товары АвтоКонтинента'
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['brand']),
        ]
        unique_together = ['brand', 'article']

    def __str__(self):
        return f"{self.brand} {self.article} {self.name}"