from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class OrderStatus(models.TextChoices):
    """Статусы заказов"""
    PENDING = 'pending', 'В обработке'
    CONFIRMED = 'confirmed', 'Подтверждён'
    IN_PROGRESS = 'in_progress', 'В работе'
    SHIPPED = 'shipped', 'Отправлен'
    DELIVERED = 'delivered', 'Доставлен'
    CANCELLED = 'cancelled', 'Отменён'
    RETURNED = 'returned', 'Возвращён'


class DeliveryMethod(models.TextChoices):
    """Способы доставки"""
    PICKUP = 'pickup', 'Самовывоз'
    COURIER = 'courier', 'Курьер'
    POST = 'post', 'Почта России'
    TRANSPORT = 'transport', 'Транспортная компания'


class PaymentMethod(models.TextChoices):
    """Способы оплаты"""
    CASH = 'cash', 'Наличными при получении'
    CARD = 'card', 'Банковской картой'
    BANK_TRANSFER = 'bank_transfer', 'Банковский перевод'
    ONLINE = 'online', 'Онлайн оплата'


class Order(models.Model):
    """Модель заказа"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заказа')
    status = models.CharField(
        max_length=20, 
        choices=OrderStatus.choices, 
        default=OrderStatus.PENDING,
        verbose_name='Статус заказа'
    )
    
    # Информация о доставке
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.PICKUP,
        verbose_name='Способ доставки'
    )
    delivery_address = models.TextField(blank=True, verbose_name='Адрес доставки')
    delivery_company = models.CharField(max_length=100, blank=True, verbose_name='Компания доставки')
    
    # Информация об оплате
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='Способ оплаты'
    )
    payment_status = models.BooleanField(default=False, verbose_name='Оплачен')
    
    # Стоимость
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Сумма без скидки'
    )
    discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Скидка'
    )
    delivery_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Стоимость доставки'
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Итоговая сумма'
    )
    
    # Комментарии
    user_comment = models.TextField(blank=True, verbose_name='Комментарий пользователя')
    admin_comment = models.TextField(blank=True, verbose_name='Комментарий администратора')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата подтверждения')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата доставки')
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отмены')
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ {self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Автоматическая генерация номера заказа
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[1])
                self.order_number = f"ORD-{last_number + 1:06d}"
            else:
                self.order_number = "ORD-000001"
        
        # Автоматический расчёт итоговой суммы
        self.total = self.subtotal - self.discount + self.delivery_cost
        
        super().save(*args, **kwargs)
    
    @property
    def items_count(self):
        """Количество товаров в заказе"""
        return self.items.count()
    
    @property
    def status_display(self):
        """Отображение статуса для фронтенда"""
        status_map = {
            OrderStatus.PENDING: 'В обработке',
            OrderStatus.CONFIRMED: 'Подтверждён',
            OrderStatus.IN_PROGRESS: 'В работе',
            OrderStatus.SHIPPED: 'Отправлен',
            OrderStatus.DELIVERED: 'Доставлен',
            OrderStatus.CANCELLED: 'Отменён',
            OrderStatus.RETURNED: 'Возвращён',
        }
        return status_map.get(self.status, self.status)


class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    
    # Информация о товаре
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель', default='')
    article = models.CharField(max_length=100, verbose_name='Артикул', default='')
    name = models.CharField(max_length=500, verbose_name='Наименование', default='')
    
    # Цена и количество
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Цена за единицу'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Стоимость',
        default=Decimal('0.00')
    )
    
    # Статус товара
    item_status = models.CharField(
        max_length=50,
        default='В обработке',
        verbose_name='Статус товара'
    )
    item_comment = models.TextField(blank=True, verbose_name='Комментарий к товару')
    
    # Дополнительная информация
    supplier = models.CharField(max_length=100, blank=True, verbose_name='Поставщик')
    warehouse = models.CharField(max_length=100, blank=True, verbose_name='Склад')
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказах'
    
    def __str__(self):
        return f"{self.manufacturer} {self.article} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Автоматический расчёт стоимости
        self.cost = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderDocument(models.Model):
    """Документы к заказу (счета, накладные и т.д.)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='documents', verbose_name='Заказ')
    document_type = models.CharField(max_length=50, verbose_name='Тип документа')
    file = models.FileField(upload_to='orders/documents/', verbose_name='Файл')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    
    class Meta:
        verbose_name = 'Документ заказа'
        verbose_name_plural = 'Документы заказов'
    
    def __str__(self):
        return f"{self.document_type} - {self.order.order_number}"


class OrderHistory(models.Model):
    """История изменений заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history', verbose_name='Заказ')
    status_from = models.CharField(max_length=20, blank=True, verbose_name='Статус с')
    status_to = models.CharField(max_length=20, verbose_name='Статус на')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Кем изменено'
    )
    
    class Meta:
        verbose_name = 'История заказа'
        verbose_name_plural = 'История заказов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status_to} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
