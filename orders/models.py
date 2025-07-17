from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product


class OrderStatus(models.Model):
    """Статусы заказов"""
    name = models.CharField(max_length=100, verbose_name='Название статуса')
    color = models.CharField(max_length=7, default='#000000', verbose_name='Цвет (HEX)')
    send_sms = models.BooleanField(default=False, verbose_name='Отправлять SMS')
    send_email = models.BooleanField(default=False, verbose_name='Отправлять Email')
    show_in_balance = models.BooleanField(default=False, verbose_name='Показывать в балансе клиента')
    action_description = models.CharField(max_length=200, blank=True, verbose_name='Описание действия')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(models.Model):
    """Заказы"""
    DELIVERY_TYPES = [
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьер'),
        ('post', 'Почта России'),
        ('transport', 'Транспортная компания'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('transfer', 'Банковский перевод'),
        ('online', 'Онлайн оплата'),
    ]

    order_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заказа')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Клиент')
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, verbose_name='Статус')
    
    # Контактная информация
    customer_name = models.CharField(max_length=200, verbose_name='Имя клиента')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон клиента')
    customer_email = models.EmailField(blank=True, verbose_name='Email клиента')
    
    # Доставка
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, verbose_name='Тип доставки')
    delivery_address = models.TextField(blank=True, verbose_name='Адрес доставки')
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость доставки')
    
    # Оплата
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='Способ оплаты')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')
    
    # Суммы
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая сумма')
    
    # Комментарии
    customer_comment = models.TextField(blank=True, verbose_name='Комментарий клиента')
    admin_comment = models.TextField(blank=True, verbose_name='Комментарий администратора')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата выполнения')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Генерация номера заказа
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                self.order_number = f"ORD-{last_number + 1:06d}"
            else:
                self.order_number = "ORD-000001"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Товары в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.price * self.quantity


class OrderStatusHistory(models.Model):
    """История изменения статусов заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name='Заказ')
    old_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, related_name='old_status_history', 
                                   blank=True, null=True, verbose_name='Предыдущий статус')
    new_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, related_name='new_status_history', 
                                   verbose_name='Новый статус')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Изменил')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'История статуса заказа'
        verbose_name_plural = 'История статусов заказов'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ {self.order.order_number}: {self.old_status} -> {self.new_status}"
