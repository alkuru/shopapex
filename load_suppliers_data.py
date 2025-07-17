#!/usr/bin/env python
"""
Скрипт для загрузки тестовых данных поставщиков в ShopApex
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, SupplierProduct, ProductCategory, Brand, SupplierSyncLog
from django.utils import timezone
import json


def create_suppliers():
    """Создание тестовых поставщиков"""
    
    # Поставщик 1: Автозапчасти "Премиум"
    supplier1, created = Supplier.objects.get_or_create(
        name='Автозапчасти "Премиум"',
        defaults={
            'description': 'Крупный поставщик оригинальных автозапчастей с широким ассортиментом',
            'contact_person': 'Иванов Иван Иванович',
            'email': 'info@premium-auto.ru',
            'phone': '+7 (495) 123-45-67',
            'website': 'https://premium-auto.ru',
            'api_url': 'https://api.premium-auto.ru/v1/products',
            'api_key': 'test_api_key_premium_12345',
            'data_format': 'json',
            'sync_frequency': 'daily',
            'markup_percentage': 15.0,
            'auto_activate_products': True,
            'is_active': True
        }
    )
    
    # Поставщик 2: MotorParts Supply
    supplier2, created = Supplier.objects.get_or_create(
        name='MotorParts Supply',
        defaults={
            'description': 'Международный поставщик запчастей для европейских автомобилей',
            'contact_person': 'Smith John',
            'email': 'sales@motorparts-supply.com',
            'phone': '+1 (555) 987-65-43',
            'website': 'https://motorparts-supply.com',
            'api_url': 'https://api.motorparts-supply.com/parts',
            'api_key': 'mp_api_key_67890',
            'data_format': 'json',
            'sync_frequency': 'hourly',
            'markup_percentage': 12.5,
            'auto_activate_products': False,
            'is_active': True
        }
    )
    
    # Поставщик 3: РосАвто
    supplier3, created = Supplier.objects.get_or_create(
        name='РосАвто',
        defaults={
            'description': 'Российский поставщик запчастей для отечественных автомобилей',
            'contact_person': 'Петров Петр Петрович',
            'email': 'zakaz@rosavto.ru',
            'phone': '+7 (812) 456-78-90',
            'website': 'https://rosavto.ru',
            'api_url': 'https://api.rosavto.ru/catalog',
            'api_key': 'rosavto_secret_key_111',
            'data_format': 'json',
            'sync_frequency': 'weekly',
            'markup_percentage': 20.0,
            'auto_activate_products': True,
            'is_active': True
        }
    )
    
    print(f"Создано поставщиков: {Supplier.objects.count()}")
    return [supplier1, supplier2, supplier3]


def create_supplier_products(suppliers):
    """Создание тестовых товаров поставщиков"""
    
    # Получаем категории и бренды
    categories = list(ProductCategory.objects.filter(is_active=True))
    brands = list(Brand.objects.filter(is_active=True))
    
    if not categories:
        print("Нет активных категорий. Создайте категории перед загрузкой товаров поставщиков.")
        return
    
    if not brands:
        print("Нет активных брендов. Создайте бренды перед загрузкой товаров поставщиков.")
        return
    
    # Товары для первого поставщика
    supplier1_products = [
        {
            'supplier_article': 'BP-001',
            'name': 'Тормозные колодки передние Toyota Camry',
            'price': 2500.00,
            'stock_quantity': 25,
            'data': {
                'brand': 'Toyota',
                'model': 'Camry',
                'year': '2018-2023',
                'description': 'Оригинальные тормозные колодки Toyota',
                'weight': '1.2 кг',
                'warranty': '12 месяцев'
            }
        },
        {
            'supplier_article': 'FT-045',
            'name': 'Фильтр топливный Hyundai Solaris',
            'price': 850.00,
            'stock_quantity': 50,
            'data': {
                'brand': 'Hyundai',
                'model': 'Solaris',
                'year': '2017-2022',
                'description': 'Топливный фильтр высокого качества',
                'weight': '0.3 кг',
                'warranty': '6 месяцев'
            }
        },
        {
            'supplier_article': 'SP-198',
            'name': 'Свечи зажигания NGK (комплект 4 шт.)',
            'price': 1200.00,
            'stock_quantity': 100,
            'data': {
                'brand': 'NGK',
                'description': 'Комплект свечей зажигания NGK',
                'quantity_in_pack': 4,
                'weight': '0.5 кг',
                'warranty': '24 месяца'
            }
        }
    ]
    
    # Товары для второго поставщика
    supplier2_products = [
        {
            'supplier_article': 'BMW-789',
            'name': 'Амортизатор передний BMW X5',
            'price': 8500.00,
            'stock_quantity': 12,
            'data': {
                'brand': 'BMW',
                'model': 'X5',
                'year': '2019-2023',
                'description': 'Оригинальный амортизатор BMW',
                'weight': '3.5 кг',
                'warranty': '36 месяцев'
            }
        },
        {
            'supplier_article': 'MB-456',
            'name': 'Ремень ГРМ Mercedes-Benz E-Class',
            'price': 3200.00,
            'stock_quantity': 20,
            'data': {
                'brand': 'Mercedes-Benz',
                'model': 'E-Class',
                'year': '2016-2021',
                'description': 'Ремень ГРМ Gates для Mercedes',
                'weight': '0.8 кг',
                'warranty': '18 месяцев'
            }
        }
    ]
    
    # Товары для третьего поставщика
    supplier3_products = [
        {
            'supplier_article': 'LADA-111',
            'name': 'Радиатор охлаждения Lada Granta',
            'price': 4500.00,
            'stock_quantity': 8,
            'data': {
                'brand': 'Lada',
                'model': 'Granta',
                'year': '2018-2023',
                'description': 'Радиатор охлаждения двигателя',
                'weight': '5.2 кг',
                'warranty': '12 месяцев'
            }
        },
        {
            'supplier_article': 'UAZ-333',
            'name': 'Комплект сцепления УАЗ Патриот',
            'price': 12000.00,
            'stock_quantity': 5,
            'data': {
                'brand': 'УАЗ',
                'model': 'Патриот',
                'year': '2015-2023',
                'description': 'Полный комплект сцепления',
                'weight': '8.5 кг',
                'warranty': '24 месяца'
            }
        }
    ]
    
    # Создаем товары для каждого поставщика
    all_products = [
        (suppliers[0], supplier1_products),
        (suppliers[1], supplier2_products),
        (suppliers[2], supplier3_products)
    ]
    
    total_created = 0
    
    for supplier, products in all_products:
        for product_data in products:
            supplier_product, created = SupplierProduct.objects.get_or_create(
                supplier=supplier,
                supplier_article=product_data['supplier_article'],
                defaults={
                    'name': product_data['name'],
                    'price': product_data['price'],
                    'stock_quantity': product_data['stock_quantity'],
                    'data': product_data['data'],
                    'is_active': True
                }
            )
            
            if created:
                total_created += 1
                print(f"Создан товар поставщика: {supplier.name} - {product_data['name']}")
    
    print(f"Всего создано товаров поставщиков: {total_created}")


def create_sync_logs(suppliers):
    """Создание тестовых логов синхронизации"""
    
    # Создаем успешные логи
    for supplier in suppliers[:2]:  # Для первых двух поставщиков
        SupplierSyncLog.objects.create(
            supplier=supplier,
            status='completed',
            message=f'Синхронизация завершена успешно. Обновлено товаров: {supplier.products.count()}',
            products_created=0,
            products_updated=supplier.products.count(),
            errors_count=0
        )
    
    # Создаем лог с ошибкой для третьего поставщика
    if len(suppliers) > 2:
        SupplierSyncLog.objects.create(
            supplier=suppliers[2],
            status='error',
            message='Ошибка подключения к API: Timeout error',
            products_created=0,
            products_updated=0,
            errors_count=1
        )
    
    print(f"Создано логов синхронизации: {SupplierSyncLog.objects.count()}")


def main():
    """Основная функция загрузки данных"""
    print("Загрузка тестовых данных поставщиков...")
    
    try:
        # Создаем поставщиков
        suppliers = create_suppliers()
        
        # Создаем товары поставщиков
        create_supplier_products(suppliers)
        
        # Создаем логи синхронизации
        create_sync_logs(suppliers)
        
        print("\n" + "="*50)
        print("ЗАГРУЗКА ЗАВЕРШЕНА!")
        print("="*50)
        print(f"Поставщиков: {Supplier.objects.count()}")
        print(f"Товаров поставщиков: {SupplierProduct.objects.count()}")
        print(f"Логов синхронизации: {SupplierSyncLog.objects.count()}")
        print("\nТеперь вы можете:")
        print("1. Зайти в админку: http://127.0.0.1:8000/admin/")
        print("2. Проверить API поставщиков: http://127.0.0.1:8000/api/catalog/suppliers/")
        print("3. Протестировать синхронизацию товаров")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
