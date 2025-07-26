from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    """Расширение профиля пользователя"""
    USER_TYPES = [
        ('client', 'Клиент'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    # Дополнительная информация
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сессия пользователя'
        verbose_name_plural = 'Сессии пользователей'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"


class UserAction(models.Model):
    """Действия пользователей (логирование)"""
    ACTION_TYPES = [
        ('login', 'Вход'),
        ('logout', 'Выход'),
        ('register', 'Регистрация'),
        ('search', 'Поиск'),
        ('view_product', 'Просмотр товара'),
        ('add_to_cart', 'Добавление в корзину'),
        ('purchase', 'Покупка'),
        ('add_to_garage', 'Добавление в гараж'),
        ('remove_from_garage', 'Удаление из гаража'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions', null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    additional_data = models.JSONField(blank=True, null=True, verbose_name='Дополнительные данные')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Действие пользователя'
        verbose_name_plural = 'Действия пользователей'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.get_action_type_display()}"


class UserFavorite(models.Model):
    """Избранные товары пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class UserGarage(models.Model):
    """Модель для хранения автомобилей пользователя в гараже"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='garage_vehicles')
    vin = models.CharField(max_length=17, verbose_name='VIN номер')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'vin']
        verbose_name = 'Автомобиль в гараже'
        verbose_name_plural = 'Автомобили в гараже'

    def __str__(self):
        return f"{self.user.username} - {self.vin}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if len(self.vin) != 17:
            raise ValidationError('VIN номер должен содержать 17 символов')
