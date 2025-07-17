#!/usr/bin/env python
"""
Скрипт для загрузки тестовых данных в ShopApex
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import ProductCategory, Brand, Product
from cms.models import News, Banner, HTMLBlock
from vin_search.models import VehicleInfo, VinRequest
from django.contrib.auth.models import User

def create_test_data():
    """Создание тестовых данных"""
    print("🚀 Создание тестовых данных для ShopApex...")
    
    # Создание брендов
    print("📦 Создание брендов...")
    brands_data = [
        {'name': 'Bosch', 'description': 'Немецкое качество автозапчастей'},
        {'name': 'Continental', 'description': 'Европейский производитель'},
        {'name': 'Febi', 'description': 'Качественные запчасти от Febi'},
        {'name': 'Sachs', 'description': 'Амортизаторы и сцепления'},
        {'name': 'Mann Filter', 'description': 'Фильтры для автомобилей'},
    ]
    
    brands = {}
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults=brand_data
        )
        brands[brand.name] = brand
        if created:
            print(f"  ✅ Создан бренд: {brand.name}")
    
    # Создание категорий
    print("📁 Создание категорий...")
    categories_data = [
        {'name': 'Двигатель', 'description': 'Запчасти для двигателя'},
        {'name': 'Трансмиссия', 'description': 'Коробка передач и сцепление'},
        {'name': 'Подвеска', 'description': 'Амортизаторы, пружины, стойки'},
        {'name': 'Тормозная система', 'description': 'Тормозные колодки, диски'},
        {'name': 'Электрика', 'description': 'Электрические компоненты'},
        {'name': 'Фильтры', 'description': 'Воздушные, масляные, топливные фильтры'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[category.name] = category
        if created:
            print(f"  ✅ Создана категория: {category.name}")
    
    # Создание товаров
    print("🛍️ Создание товаров...")
    products_data = [
        {
            'name': 'Масляный фильтр Bosch F026407006',
            'article': 'F026407006',
            'description': 'Высококачественный масляный фильтр для легковых автомобилей',
            'price': 350.00,
            'category': 'Фильтры',
            'brand': 'Bosch',
            'is_featured': True,
        },
        {
            'name': 'Тормозные колодки Febi 16728',
            'article': '16728',
            'description': 'Передние тормозные колодки, совместимы с большинством автомобилей',
            'price': 1200.00,
            'category': 'Тормозная система',
            'brand': 'Febi',
            'is_featured': True,
        },
        {
            'name': 'Амортизатор Sachs 314 404',
            'article': '314404',
            'description': 'Передний амортизатор газомасляный',
            'price': 2800.00,
            'category': 'Подвеска',
            'brand': 'Sachs',
            'is_featured': True,
        },
        {
            'name': 'Воздушный фильтр Mann C 30 005',
            'article': 'C30005',
            'description': 'Воздушный фильтр двигателя, высокая степень очистки',
            'price': 450.00,
            'category': 'Фильтры',
            'brand': 'Mann Filter',
        },
        {
            'name': 'Ремень ГРМ Continental CT1028',
            'article': 'CT1028',
            'description': 'Зубчатый ремень ГРМ, усиленная конструкция',
            'price': 890.00,
            'category': 'Двигатель',
            'brand': 'Continental',
        },
        {
            'name': 'Свечи зажигания Bosch FR7DC',
            'article': 'FR7DC',
            'description': 'Комплект свечей зажигания (4 шт.)',
            'price': 320.00,
            'category': 'Электрика',
            'brand': 'Bosch',
        },
    ]
    
    for product_data in products_data:
        category = categories[product_data.pop('category')]
        brand = brands[product_data.pop('brand')]
        
        product, created = Product.objects.get_or_create(
            article=product_data['article'],
            defaults={
                **product_data,
                'category': category,
                'brand': brand,
                'stock_quantity': 10,  # Добавляем количество на складе
            }
        )
        if created:
            print(f"  ✅ Создан товар: {product.name}")
    
    # Создание новостей
    print("📰 Создание новостей...")
    
    # Используем админа как автора новостей
    admin_user = User.objects.get(username='admin')
    
    news_data = [
        {
            'title': 'Новые поступления автозапчастей Bosch',
            'slug': 'novye-postupleniya-avtozapchastej-bosch',
            'content': 'В наш магазин поступили новые оригинальные запчасти от Bosch. Большой выбор фильтров, свечей зажигания и других компонентов.',
            'is_published': True,
            'author': admin_user,
        },
        {
            'title': 'Скидки на тормозные колодки',
            'slug': 'skidki-na-tormoznye-kolodki',
            'content': 'Специальное предложение на тормозные колодки от ведущих производителей. Скидка до 15% на весь ассортимент.',
            'is_published': True,
            'author': admin_user,
        },
    ]
    
    for news_item in news_data:
        news, created = News.objects.get_or_create(
            slug=news_item['slug'],
            defaults=news_item
        )
        if created:
            print(f"  ✅ Создана новость: {news.title}")
    
    # Создание HTML блоков
    print("📄 Создание HTML блоков...")
    html_blocks_data = [
        {
            'title': 'Контактная информация',
            'position': 'contacts',
            'html_content': '''
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-map-marker-alt text-primary"></i> Адрес</h6>
                    <p>г. Москва, ул. Автозаводская, д. 123<br>
                    ТЦ "Автозапчасти", павильон 45</p>
                    
                    <h6><i class="fas fa-phone text-primary"></i> Телефоны</h6>
                    <p>
                        +7 (495) 123-45-67<br>
                        +7 (499) 987-65-43
                    </p>
                    
                    <h6><i class="fas fa-envelope text-primary"></i> Email</h6>
                    <p>info@shopapex.ru<br>
                    sales@shopapex.ru</p>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-clock text-primary"></i> Режим работы</h6>
                    <p>
                        Пн-Пт: 9:00 - 19:00<br>
                        Сб: 10:00 - 16:00<br>
                        Вс: выходной
                    </p>
                    
                    <h6><i class="fas fa-car text-primary"></i> Услуги</h6>
                    <p>• Подбор запчастей по VIN<br>
                    • Доставка по Москве<br>
                    • Установка в автосервисе<br>
                    • Гарантия на все товары</p>
                </div>
            </div>
            ''',
            'is_active': True,
        }
    ]
    
    for block_data in html_blocks_data:
        block, created = HTMLBlock.objects.get_or_create(
            position=block_data['position'],
            defaults=block_data
        )
        if created:
            print(f"  ✅ Создан HTML блок: {block.title}")
    
    # Создание тестовых VIN записей
    print("🚗 Создание тестовых VIN записей...")
    
    # Создаем тестового пользователя для VIN запросов
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь'
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"  ✅ Создан тестовый пользователь: {test_user.username}")
    
    # Создаем VIN запрос
    vin_request, created = VinRequest.objects.get_or_create(
        vin_code='WVWZZZ1JZXW123456',
        defaults={
            'request_number': 'VIN001',
            'request_type': 'vin',
            'customer': test_user,
            'customer_name': test_user.get_full_name(),
            'status': 'completed',
            'admin_comment': 'Тестовый VIN запрос'
        }
    )
    if created:
        print(f"  ✅ Создан VIN запрос: {vin_request.vin_code}")
        
        # Создаем информацию об автомобиле
        vehicle_info, created = VehicleInfo.objects.get_or_create(
            vin_request=vin_request,
            defaults={
                'make': 'Volkswagen',
                'model': 'Golf',
                'year': 2015,
                'engine_volume': '1.6 TDI',
                'transmission': 'Manual',
                'drive_type': 'FWD'
            }
        )
        if created:
            print(f"  ✅ Создана информация об автомобиле: {vehicle_info.make} {vehicle_info.model}")
    
    print("✅ Тестовые данные успешно созданы!")
    print("\n🎯 Что создано:")
    print(f"  • Брендов: {Brand.objects.count()}")
    print(f"  • Категорий: {ProductCategory.objects.count()}")
    print(f"  • Товаров: {Product.objects.count()}")
    print(f"  • Новостей: {News.objects.count()}")
    print(f"  • HTML блоков: {HTMLBlock.objects.count()}")
    print(f"  • VIN запросов: {VinRequest.objects.count()}")
    print("\n🚀 Теперь можно тестировать сайт с реальными данными!")

if __name__ == '__main__':
    create_test_data()
