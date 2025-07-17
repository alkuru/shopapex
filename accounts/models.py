from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Расширение профиля пользователя"""
    USER_TYPES = [
        ('customer', 'Клиент'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer', verbose_name='Тип пользователя')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True, verbose_name='Email уведомления')
    sms_notifications = models.BooleanField(default=False, verbose_name='SMS уведомления')
    
    # Дополнительная информация
    company = models.CharField(max_length=200, blank=True, verbose_name='Компания')
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username}"

    @property
    def full_name(self):
        """Полное имя пользователя"""
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматическое создание профиля при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Автоматическое сохранение профиля при сохранении пользователя"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


class UserSession(models.Model):
    """Сессии пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    session_key = models.CharField(max_length=40, verbose_name='Ключ сессии')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес')
    user_agent = models.TextField(verbose_name='User Agent')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')

    class Meta:
        verbose_name = 'Сессия пользователя'
        verbose_name_plural = 'Сессии пользователей'
        ordering = ['-last_activity']

    def __str__(self):
        return f"Сессия {self.user.username} ({self.ip_address})"


class UserAction(models.Model):
    """Действия пользователей (логирование)"""
    ACTION_TYPES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('order_create', 'Создание заказа'),
        ('order_update', 'Обновление заказа'),
        ('product_view', 'Просмотр товара'),
        ('cart_add', 'Добавление в корзину'),
        ('cart_remove', 'Удаление из корзины'),
        ('search', 'Поиск'),
        ('vin_search', 'Поиск по VIN'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name='Тип действия')
    description = models.CharField(max_length=200, verbose_name='Описание')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP адрес')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    additional_data = models.JSONField(blank=True, null=True, verbose_name='Дополнительные данные')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата действия')

    class Meta:
        verbose_name = 'Действие пользователя'
        verbose_name_plural = 'Действия пользователей'
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.username if self.user else 'Анонимный'
        return f"{user_name} - {self.get_action_type_display()}"


class UserFavorite(models.Model):
    """Избранные товары пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
