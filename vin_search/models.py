from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product


class VinRequest(models.Model):
    """Запросы поиска по VIN"""
    REQUEST_TYPES = [
        ('vin', 'VIN код'),
        ('frame', 'FRAME номер'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Обработан'),
        ('cancelled', 'Отменен'),
    ]

    request_number = models.CharField(max_length=20, unique=True, verbose_name='Номер запроса')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES, verbose_name='Тип запроса')
    vin_code = models.CharField(max_length=17, blank=True, verbose_name='VIN код')
    frame_number = models.CharField(max_length=20, blank=True, verbose_name='FRAME номер')
    
    # Информация о клиенте
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Клиент')
    customer_name = models.CharField(max_length=200, blank=True, verbose_name='Имя клиента')
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон клиента')
    customer_email = models.EmailField(blank=True, verbose_name='Email клиента')
    
    # Статус и обработка
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='processed_vin_requests', verbose_name='Обработал')
    admin_comment = models.TextField(blank=True, verbose_name='Комментарий администратора')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата обработки')

    class Meta:
        verbose_name = 'VIN запрос'
        verbose_name_plural = 'VIN запросы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Запрос #{self.request_number} - {self.vin_code or self.frame_number}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            # Генерация номера запроса
            last_request = VinRequest.objects.order_by('-id').first()
            if last_request:
                last_number = int(last_request.request_number.split('-')[-1])
                self.request_number = f"VIN-{last_number + 1:06d}"
            else:
                self.request_number = "VIN-000001"
        super().save(*args, **kwargs)


class VehicleInfo(models.Model):
    """Информация об автомобиле по VIN"""
    vin_request = models.OneToOneField(VinRequest, on_delete=models.CASCADE, related_name='vehicle_info', verbose_name='VIN запрос')
    
    # Основная информация об автомобиле
    make = models.CharField(max_length=100, verbose_name='Марка')
    model = models.CharField(max_length=100, verbose_name='Модель')
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    engine_type = models.CharField(max_length=100, blank=True, verbose_name='Тип двигателя')
    engine_volume = models.CharField(max_length=20, blank=True, verbose_name='Объем двигателя')
    transmission = models.CharField(max_length=50, blank=True, verbose_name='Коробка передач')
    body_type = models.CharField(max_length=50, blank=True, verbose_name='Тип кузова')
    drive_type = models.CharField(max_length=20, blank=True, verbose_name='Привод')
    
    # Дополнительная информация
    color = models.CharField(max_length=50, blank=True, verbose_name='Цвет')
    country_of_origin = models.CharField(max_length=100, blank=True, verbose_name='Страна происхождения')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Информация об автомобиле'
        verbose_name_plural = 'Информация об автомобилях'

    def __str__(self):
        return f"{self.make} {self.model} {self.year}"


class VinSearchResult(models.Model):
    """Результаты поиска запчастей по VIN"""
    vin_request = models.ForeignKey(VinRequest, on_delete=models.CASCADE, related_name='search_results', verbose_name='VIN запрос')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    is_recommended = models.BooleanField(default=False, verbose_name='Рекомендуемый')
    compatibility_note = models.TextField(blank=True, verbose_name='Примечание о совместимости')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Результат поиска по VIN'
        verbose_name_plural = 'Результаты поиска по VIN'
        unique_together = ['vin_request', 'product']

    def __str__(self):
        return f"{self.vin_request.request_number} - {self.product.name}"


class VinDatabase(models.Model):
    """База VIN кодов и соответствующих запчастей"""
    vin_pattern = models.CharField(max_length=17, verbose_name='VIN паттерн')
    make = models.CharField(max_length=100, verbose_name='Марка')
    model = models.CharField(max_length=100, verbose_name='Модель')
    year_from = models.PositiveIntegerField(verbose_name='Год от')
    year_to = models.PositiveIntegerField(verbose_name='Год до')
    engine_type = models.CharField(max_length=100, blank=True, verbose_name='Тип двигателя')
    products = models.ManyToManyField(Product, blank=True, verbose_name='Подходящие товары')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Запись VIN базы'
        verbose_name_plural = 'VIN база данных'
        ordering = ['make', 'model', 'year_from']

    def __str__(self):
        return f"{self.make} {self.model} ({self.year_from}-{self.year_to})"
