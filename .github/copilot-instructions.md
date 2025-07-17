<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# ShopApex - Инструкции для GitHub Copilot

## Контекст проекта
Это Django проект интернет-магазина автозапчастей с полным функционалом e-commerce, включая:
- Каталог товаров с категориями и брендами
- Систему заказов с отслеживанием статусов
- Управление клиентами и их профилями
- Поиск по VIN кодам автомобилей
- CMS для управления контентом сайта
- Административную панель для всех операций

## Архитектурные принципы

### Django приложения:
- `catalog` - каталог товаров, категории, бренды, корзина
- `orders` - заказы, статусы, история изменений
- `customers` - клиенты, адреса, баланс, заметки
- `vin_search` - поиск по VIN, база VIN кодов, запросы
- `cms` - контент-менеджмент, настройки, баннеры, новости
- `accounts` - пользователи, профили, действия, избранное

### Соглашения по коду:
- Используйте русские verbose_name в моделях
- Все модели должны иметь `__str__` методы
- API views используют Django REST Framework
- Административная панель настроена для всех моделей
- Используйте select_related/prefetch_related для оптимизации запросов

### Стиль и форматирование:
- Следуйте PEP 8 для Python кода
- Используйте docstrings для классов и методов
- Bootstrap 5 для фронтенда
- Font Awesome для иконок
- Адаптивный дизайн для мобильных устройств

### Базы данных:
- SQLite для разработки, PostgreSQL для продакшена
- Используйте миграции Django для изменений схемы
- Индексы для часто запрашиваемых полей
- Foreign Key ограничения с CASCADE/PROTECT по логике

### API и сериализация:
- Django REST Framework для API
- Вложенные сериализаторы для связанных объектов
- Фильтрация через django-filter
- Пагинация для списков
- Права доступа для защищенных эндпоинтов

### Безопасность:
- CSRF токены для форм
- Аутентификация для админских операций
- Валидация данных на уровне модели и формы
- Безопасные настройки для продакшена

### Задачи и уведомления:
- Celery для асинхронных задач
- Redis как брокер сообщений
- Email/SMS уведомления при изменении статусов
- Логирование действий пользователей

## Примеры использования

### Создание новой модели:
```python
class ExampleModel(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Пример'
        verbose_name_plural = 'Примеры'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
```

### API ViewSet:
```python
class ExampleViewSet(viewsets.ModelViewSet):
    queryset = ExampleModel.objects.filter(is_active=True)
    serializer_class = ExampleSerializer
    
    def get_queryset(self):
        return super().get_queryset().select_related('related_field')
```

### Админка:
```python
@admin.register(ExampleModel)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']
```

## Важные особенности проекта

### VIN поиск:
- Поддержка VIN кодов и FRAME номеров
- Автоматический подбор запчастей по базе данных
- История запросов с возможностью обработки

### Система заказов:
- Гибкие статусы с настройкой уведомлений
- История изменений статусов
- Различные способы доставки и оплаты

### CMS функционал:
- Управление баннерами с датами показа
- Слайдеры с настройками автопрокрутки
- Новости с SEO оптимизацией
- HTML блоки для кастомного контента

### Клиентская база:
- Расширенные профили клиентов
- Множественные адреса доставки
- Система баланса с транзакциями
- Заметки менеджеров о клиентах

Всегда учитывайте эти особенности при разработке новых функций или модификации существующих.
