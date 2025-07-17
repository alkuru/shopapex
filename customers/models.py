from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """Расширенная информация о клиентах"""
    DELIVERY_TYPES = [
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьер'),
        ('post', 'Почта России'),
        ('transport', 'Транспортная компания'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    preferred_delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, 
                                               default='pickup', verbose_name='Предпочитаемый тип доставки')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='managed_customers', verbose_name='Менеджер')
    delivery_address = models.TextField(blank=True, verbose_name='Адрес доставки')
    admin_comment = models.TextField(blank=True, verbose_name='Комментарий администратора')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    last_order_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата последнего заказа')
    total_orders_count = models.PositiveIntegerField(default=0, verbose_name='Количество заказов')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общая сумма покупок')
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True, verbose_name='Email уведомления')
    sms_notifications = models.BooleanField(default=True, verbose_name='SMS уведомления')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.phone})"

    @property
    def full_name(self):
        """Полное имя клиента"""
        return self.user.get_full_name() or self.user.username

    def update_order_stats(self):
        """Обновление статистики заказов"""
        from orders.models import Order
        orders = Order.objects.filter(user=self.user)
        self.total_orders_count = orders.count()
        if orders.exists():
            self.last_order_date = orders.latest('created_at').created_at
            self.total_spent = sum(order.total_amount for order in orders)
        self.save()


class CustomerAddress(models.Model):
    """Адреса клиентов"""
    ADDRESS_TYPES = [
        ('home', 'Домашний'),
        ('work', 'Рабочий'),
        ('other', 'Другой'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses', verbose_name='Клиент')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, verbose_name='Тип адреса')
    title = models.CharField(max_length=100, verbose_name='Название адреса')
    address = models.TextField(verbose_name='Адрес')
    is_default = models.BooleanField(default=False, verbose_name='Адрес по умолчанию')

    class Meta:
        verbose_name = 'Адрес клиента'
        verbose_name_plural = 'Адреса клиентов'

    def __str__(self):
        return f"{self.customer.full_name} - {self.title}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Убираем флаг default с других адресов этого клиента
            CustomerAddress.objects.filter(customer=self.customer, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class CustomerBalance(models.Model):
    """Баланс клиента"""
    TRANSACTION_TYPES = [
        ('deposit', 'Пополнение'),
        ('withdrawal', 'Списание'),
        ('bonus', 'Бонус'),
        ('refund', 'Возврат'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='balance_transactions', verbose_name='Клиент')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Тип операции')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    description = models.CharField(max_length=200, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата операции')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Связанный заказ')

    class Meta:
        verbose_name = 'Операция по балансу'
        verbose_name_plural = 'Операции по балансу'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.full_name} - {self.get_transaction_type_display()} {self.amount}"


class CustomerNote(models.Model):
    """Заметки о клиентах"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes', verbose_name='Клиент')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    note = models.TextField(verbose_name='Заметка')
    is_important = models.BooleanField(default=False, verbose_name='Важная заметка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Заметка о клиенте'
        verbose_name_plural = 'Заметки о клиентах'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заметка о {self.customer.full_name} от {self.author.username}"
