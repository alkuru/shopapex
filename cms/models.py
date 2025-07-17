from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class StoreSettings(models.Model):
    """Основные настройки магазина"""
    store_name = models.CharField(max_length=200, verbose_name='Название магазина')
    slogan = models.CharField(max_length=300, blank=True, verbose_name='Слоган')
    meta_keywords = models.TextField(blank=True, verbose_name='Meta keywords')
    meta_description = models.TextField(blank=True, verbose_name='Meta description')
    footer_copyright = models.TextField(blank=True, verbose_name='Копирайт в футере')
    vk_group = models.URLField(blank=True, verbose_name='Группа ВКонтакте')
    telegram_group = models.URLField(blank=True, verbose_name='Группа Telegram')
    
    # Контактная информация
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.TextField(blank=True, verbose_name='Адрес')
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Настройки магазина'
        verbose_name_plural = 'Настройки магазина'

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        # Разрешаем только одну запись настроек
        if not self.pk and StoreSettings.objects.exists():
            raise ValueError('Может существовать только одна запись настроек магазина')
        return super().save(*args, **kwargs)


class HomePage(models.Model):
    """Контент главной страницы"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(blank=True, verbose_name='Содержание')
    image = models.ImageField(upload_to='homepage/', blank=True, null=True, verbose_name='Изображение')
    video_url = models.URLField(blank=True, verbose_name='Ссылка на видео')
    external_link = models.URLField(blank=True, verbose_name='Внешняя ссылка')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Блок главной страницы'
        verbose_name_plural = 'Блоки главной страницы'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Banner(models.Model):
    """Баннеры"""
    BANNER_TYPES = [
        ('main', 'Главный баннер'),
        ('sidebar', 'Боковой баннер'),
        ('footer', 'Баннер в футере'),
        ('category', 'Баннер категории'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название баннера')
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, verbose_name='Тип баннера')
    image = models.ImageField(upload_to='banners/', verbose_name='Изображение')
    text = models.TextField(blank=True, verbose_name='Текст баннера')
    link_url = models.URLField(blank=True, verbose_name='Ссылка')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    start_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала показа')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания показа')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    @property
    def is_active_now(self):
        """Проверка активности баннера по датам"""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class HTMLBlock(models.Model):
    """HTML блоки"""
    BLOCK_POSITIONS = [
        ('header', 'Шапка сайта'),
        ('sidebar', 'Боковая панель'),
        ('footer', 'Футер'),
        ('home_top', 'Главная - верх'),
        ('home_bottom', 'Главная - низ'),
        ('catalog_top', 'Каталог - верх'),
        ('product_bottom', 'Страница товара - низ'),
        ('contacts', 'Страница контактов'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название блока')
    position = models.CharField(max_length=20, choices=BLOCK_POSITIONS, verbose_name='Позиция')
    html_content = models.TextField(verbose_name='HTML содержимое')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'HTML блок'
        verbose_name_plural = 'HTML блоки'
        ordering = ['position', 'order']

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"


class Slider(models.Model):
    """Слайдеры"""
    title = models.CharField(max_length=200, verbose_name='Название слайдера')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    autoplay = models.BooleanField(default=True, verbose_name='Автопрокрутка')
    autoplay_speed = models.PositiveIntegerField(default=5000, verbose_name='Скорость автопрокрутки (мс)')
    loop = models.BooleanField(default=True, verbose_name='Зацикливание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Слайдер'
        verbose_name_plural = 'Слайдеры'

    def __str__(self):
        return self.title


class SliderItem(models.Model):
    """Элементы слайдера"""
    slider = models.ForeignKey(Slider, on_delete=models.CASCADE, related_name='items', verbose_name='Слайдер')
    title = models.CharField(max_length=200, verbose_name='Заголовок слайда')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='slider/', verbose_name='Изображение')
    link_url = models.URLField(blank=True, verbose_name='Ссылка')
    link_text = models.CharField(max_length=100, blank=True, verbose_name='Текст ссылки')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Элемент слайдера'
        verbose_name_plural = 'Элементы слайдера'
        ordering = ['order']

    def __str__(self):
        return f"{self.slider.title} - {self.title}"


class News(models.Model):
    """Новости"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='URL слаг')
    content = models.TextField(verbose_name='Содержание')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='Краткое описание')
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name='Изображение')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class CatalogBlock(models.Model):
    """Блоки каталогов на главной странице"""
    title = models.CharField(max_length=200, verbose_name='Название блока')
    description = models.TextField(blank=True, verbose_name='Описание')
    categories = models.ManyToManyField('catalog.ProductCategory', blank=True, verbose_name='Категории')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    show_products = models.BooleanField(default=True, verbose_name='Показывать товары')
    products_count = models.PositiveIntegerField(default=8, verbose_name='Количество товаров')
    sort_by = models.CharField(max_length=20, default='created_at', verbose_name='Сортировка товаров')

    class Meta:
        verbose_name = 'Блок каталога'
        verbose_name_plural = 'Блоки каталогов'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
