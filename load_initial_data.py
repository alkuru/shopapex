#!/usr/bin/env python
"""
Скрипт для создания начальных данных в базе ShopApex
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.contrib.auth.models import User
from catalog.models import ProductCategory, Brand, Product
from orders.models import OrderStatus
from cms.models import StoreSettings
from decimal import Decimal


def create_initial_data():
    """Создание начальных данных"""
    
    print("🚀 Создание начальных данных для ShopApex...")
    
    # 1. Настройки магазина
    print("📋 Создание настроек магазина...")
    store_settings, created = StoreSettings.objects.get_or_create(
        defaults={
            'store_name': 'ShopApex',
            'slogan': 'Надежные автозапчасти для вашего автомобиля',
            'meta_keywords': 'автозапчасти, запчасти, автомобиль, масла, аккумуляторы',
            'meta_description': 'ShopApex - интернет-магазин автозапчастей. Широкий ассортимент качественных запчастей для любого автомобиля.',
            'phone': '+7 (999) 123-45-67',
            'email': 'info@shopapex.ru',
            'address': 'г. Москва, ул. Примерная, д. 123',
            'footer_copyright': '© 2025 ShopApex. Все права защищены.',
        }
    )
    print(f"✅ Настройки магазина {'созданы' if created else 'уже существуют'}")
    
    # 2. Статусы заказов
    print("📦 Создание статусов заказов...")
    statuses_data = [
        {'name': 'Новый', 'color': '#ff9800', 'send_email': True, 'send_sms': True},
        {'name': 'Принят', 'color': '#2196f3', 'send_email': True, 'send_sms': True},
        {'name': 'В работе', 'color': '#9c27b0', 'send_email': True, 'send_sms': False},
        {'name': 'Готов к выдаче', 'color': '#4caf50', 'send_email': True, 'send_sms': True, 'show_in_balance': True},
        {'name': 'Выдан', 'color': '#4caf50', 'send_email': True, 'send_sms': True},
        {'name': 'Отменен', 'color': '#f44336', 'send_email': True, 'send_sms': False},
    ]
    
    for status_data in statuses_data:
        status, created = OrderStatus.objects.get_or_create(
            name=status_data['name'],
            defaults=status_data
        )
        print(f"  ✅ Статус '{status.name}' {'создан' if created else 'уже существует'}")
    
    # 3. Категории товаров
    print("📂 Создание категорий товаров...")
    categories_data = [
        {'name': 'Кузовной каталог', 'description': 'Детали кузова, бамперы, крылья, двери', 'order': 1},
        {'name': 'Тормозные жидкости', 'description': 'DOT 3, DOT 4, DOT 5.1', 'order': 2},
        {'name': 'Масла моторные', 'description': 'Синтетические, полусинтетические, минеральные масла', 'order': 3},
        {'name': 'Масла трансмиссионные', 'description': 'Масла для МКПП, АКПП, дифференциалов', 'order': 4},
        {'name': 'Аккумуляторы', 'description': 'АКБ для легковых и грузовых автомобилей', 'order': 5},
        {'name': 'Зарядные устройства', 'description': 'Зарядники для аккумуляторов', 'order': 6},
        {'name': 'Шины', 'description': 'Летние, зимние, всесезонные шины', 'order': 7},
        {'name': 'Диски', 'description': 'Литые, штампованные диски', 'order': 8},
        {'name': 'Автохимия', 'description': 'Присадки, очистители, автокосметика', 'order': 9},
        {'name': 'Антифризы', 'description': 'Охлаждающие жидкости различных типов', 'order': 10},
        {'name': 'Присадки', 'description': 'Присадки для двигателя, топлива, трансмиссии', 'order': 11},
        {'name': 'Прочая электроника', 'description': 'Автоэлектроника и аксессуары', 'order': 12},
    ]
    
    for cat_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        print(f"  ✅ Категория '{category.name}' {'создана' if created else 'уже существует'}")
    
    # 4. Бренды
    print("🏷️ Создание брендов...")
    brands_data = [
        {'name': 'Mobil 1', 'description': 'Премиальные синтетические масла'},
        {'name': 'Castrol', 'description': 'Высококачественные моторные масла'},
        {'name': 'Shell', 'description': 'Инновационные смазочные материалы'},
        {'name': 'Bosch', 'description': 'Автомобильные компоненты и системы'},
        {'name': 'Mann Filter', 'description': 'Фильтры для автомобилей'},
        {'name': 'Brembo', 'description': 'Тормозные системы'},
        {'name': 'Continental', 'description': 'Шины и автокомпоненты'},
        {'name': 'Michelin', 'description': 'Премиальные шины'},
        {'name': 'Varta', 'description': 'Автомобильные аккумуляторы'},
        {'name': 'Liqui Moly', 'description': 'Масла и автохимия'},
    ]
    
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults=brand_data
        )
        print(f"  ✅ Бренд '{brand.name}' {'создан' if created else 'уже существует'}")
    
    # 5. Примеры товаров
    print("🛍️ Создание примеров товаров...")
    
    # Получаем созданные категории и бренды
    oil_category = ProductCategory.objects.get(name='Масла моторные')
    brake_fluid_category = ProductCategory.objects.get(name='Тормозные жидкости')
    battery_category = ProductCategory.objects.get(name='Аккумуляторы')
    
    mobil_brand = Brand.objects.get(name='Mobil 1')
    castrol_brand = Brand.objects.get(name='Castrol')
    bosch_brand = Brand.objects.get(name='Bosch')
    varta_brand = Brand.objects.get(name='Varta')
    
    products_data = [
        {
            'name': 'Mobil 1 ESP Formula 5W-30',
            'article': 'MOB-ESP-5W30-4L',
            'category': oil_category,
            'brand': mobil_brand,
            'description': 'Полностью синтетическое моторное масло для современных дизельных и бензиновых двигателей',
            'price': Decimal('3500.00'),
            'stock_quantity': 25,
            'is_featured': True,
        },
        {
            'name': 'Castrol GTX 10W-40',
            'article': 'CAS-GTX-10W40-4L',
            'category': oil_category,
            'brand': castrol_brand,
            'description': 'Полусинтетическое моторное масло для бензиновых и дизельных двигателей',
            'price': Decimal('2200.00'),
            'stock_quantity': 30,
        },
        {
            'name': 'Bosch DOT 4 Brake Fluid',
            'article': 'BSH-DOT4-1L',
            'category': brake_fluid_category,
            'brand': bosch_brand,
            'description': 'Тормозная жидкость DOT 4 для гидравлических тормозных систем',
            'price': Decimal('450.00'),
            'stock_quantity': 50,
        },
        {
            'name': 'Varta Blue Dynamic E11',
            'article': 'VAR-BD-E11-74AH',
            'category': battery_category,
            'brand': varta_brand,
            'description': 'Аккумулятор 74Ah 680A для легковых автомобилей',
            'price': Decimal('8500.00'),
            'discount_price': Decimal('7800.00'),
            'stock_quantity': 15,
            'is_featured': True,
        },
        {
            'name': 'Mobil 1 0W-20',
            'article': 'MOB-1-0W20-4L',
            'category': oil_category,
            'brand': mobil_brand,
            'description': 'Полностью синтетическое масло для современных бензиновых двигателей',
            'price': Decimal('4200.00'),
            'stock_quantity': 20,
        },
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            article=product_data['article'],
            defaults=product_data
        )
        print(f"  ✅ Товар '{product.name}' {'создан' if created else 'уже существует'}")
    
    print("\n🎉 Начальные данные успешно созданы!")
    print(f"📊 Создано:")
    print(f"   - Категорий: {ProductCategory.objects.count()}")
    print(f"   - Брендов: {Brand.objects.count()}")
    print(f"   - Товаров: {Product.objects.count()}")
    print(f"   - Статусов заказов: {OrderStatus.objects.count()}")
    print("\n🌐 Теперь вы можете:")
    print("   - Открыть главную страницу: http://127.0.0.1:8000/")
    print("   - Войти в админку: http://127.0.0.1:8000/admin/")
    print("   - Использовать API: http://127.0.0.1:8000/api/")


if __name__ == '__main__':
    create_initial_data()
