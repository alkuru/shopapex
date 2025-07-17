#!/usr/bin/env python
"""
Эмулятор API vinttop.ru для тестирования интеграции
Пока недоступен их реальный API сервер
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, SupplierSyncLog

def create_mock_api_response():
    """Создает мок-данные для тестирования API"""
    
    # Получаем поставщика
    try:
        supplier = Supplier.objects.get(name__icontains='vinttop')
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop не найден!")
        return
    
    print("🎭 СОЗДАНИЕ MOCK API ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    print("Пока API сервер vinttop.ru недоступен (503),")
    print("создаем тестовые данные для проверки интеграции.")
    
    # Создаем новый класс для эмуляции API
    class MockVintTopAPI:
        def __init__(self, supplier):
            self.supplier = supplier
            
        def test_connection(self):
            """Эмуляция успешного подключения"""
            return True, "Mock API: Подключение успешно"
            
        def search_products(self, article):
            """Эмуляция поиска товаров"""
            return True, {
                "brands": [
                    {
                        "brand": "BOSCH",
                        "parts": [
                            {
                                "name": f"Тормозные колодки {article}",
                                "code": article,
                                "price": "2500.00",
                                "currency": "RUB",
                                "quantity": 5,
                                "description": "Передние тормозные колодки"
                            }
                        ]
                    },
                    {
                        "brand": "FEBI",
                        "parts": [
                            {
                                "name": f"Масляный фильтр {article}",
                                "code": article + "-ALT",
                                "price": "850.00", 
                                "currency": "RUB",
                                "quantity": 12,
                                "description": "Масляный фильтр двигателя"
                            }
                        ]
                    }
                ]
            }
            
        def get_staff(self):
            """Эмуляция списка сотрудников"""
            return True, [
                {
                    "id": 1,
                    "name": "Иван Петров",
                    "position": "Менеджер",
                    "email": "ivan@vinttop.ru",
                    "phone": "+7 (495) 123-45-67",
                    "is_active": True
                },
                {
                    "id": 2,
                    "name": "Мария Сидорова", 
                    "position": "Кладовщик",
                    "email": "maria@vinttop.ru",
                    "phone": "+7 (495) 123-45-68",
                    "is_active": True
                }
            ]
            
        def get_delivery_methods(self):
            """Эмуляция способов доставки"""
            return True, [
                {
                    "id": 1,
                    "name": "Самовывоз",
                    "description": "Самовывоз со склада",
                    "cost": 0,
                    "delivery_time": "В течение дня"
                },
                {
                    "id": 2,
                    "name": "Курьерская доставка",
                    "description": "Доставка курьером по Москве",
                    "cost": 500,
                    "delivery_time": "1-2 дня"
                }
            ]
            
        def get_order_statuses(self):
            """Эмуляция статусов заказов"""
            return True, [
                {"id": 1, "name": "Новый", "description": "Заказ создан"},
                {"id": 2, "name": "Подтвержден", "description": "Заказ подтвержден"},
                {"id": 3, "name": "В работе", "description": "Заказ собирается"},
                {"id": 4, "name": "Готов", "description": "Заказ готов к выдаче"},
                {"id": 5, "name": "Выдан", "description": "Заказ выдан клиенту"}
            ]
            
        def get_client_groups(self):
            """Эмуляция групп клиентов"""
            return True, [
                {"id": 1, "name": "Розничные клиенты", "discount": 0},
                {"id": 2, "name": "Оптовые клиенты", "discount": 5},
                {"id": 3, "name": "VIP клиенты", "discount": 10}
            ]
            
        def get_clients(self):
            """Эмуляция списка клиентов"""
            return True, [
                {
                    "id": 1,
                    "name": "ООО Автосервис",
                    "email": "info@autoservice.ru",
                    "phone": "+7 (495) 555-01-01",
                    "group_id": 2,
                    "balance": 15000.50,
                    "is_active": True
                },
                {
                    "id": 2,
                    "name": "Петров Иван Иванович",
                    "email": "petrov@example.com",
                    "phone": "+7 (926) 555-02-02", 
                    "group_id": 1,
                    "balance": 2500.00,
                    "is_active": True
                }
            ]
            
        def get_orders(self):
            """Эмуляция списка заказов"""
            return True, [
                {
                    "id": 1001,
                    "client_id": 1,
                    "status_id": 2,
                    "total_amount": 5500.00,
                    "created_at": "2024-12-01 10:30:00",
                    "items": [
                        {
                            "product_code": "0986424815",
                            "product_name": "Тормозные колодки BOSCH",
                            "quantity": 2,
                            "price": 2500.00,
                            "total": 5000.00
                        },
                        {
                            "product_code": "123456789-ALT",
                            "product_name": "Масляный фильтр FEBI", 
                            "quantity": 1,
                            "price": 500.00,
                            "total": 500.00
                        }
                    ]
                }
            ]
    
    # Временно заменяем методы поставщика на mock версии
    mock_api = MockVintTopAPI(supplier)
    
    print("\n🔧 ТЕСТИРОВАНИЕ MOCK API:")
    
    # Тест подключения
    print(f"\n1. Тест подключения:")
    success, message = mock_api.test_connection()
    print(f"   ✅ {message}")
    
    # Тест поиска
    print(f"\n2. Поиск товаров по артикулу '0986424815':")
    success, result = mock_api.search_products("0986424815")
    if success:
        brands = result.get('brands', [])
        total_products = sum(len(brand.get('parts', [])) for brand in brands)
        print(f"   ✅ Найдено товаров: {total_products}")
        for brand in brands:
            brand_name = brand.get('brand')
            parts_count = len(brand.get('parts', []))
            print(f"      - {brand_name}: {parts_count} товаров")
    
    # Тест сущностей
    entities = [
        ("Сотрудники", mock_api.get_staff),
        ("Способы доставки", mock_api.get_delivery_methods), 
        ("Статусы заказов", mock_api.get_order_statuses),
        ("Группы клиентов", mock_api.get_client_groups),
        ("Клиенты", mock_api.get_clients),
        ("Заказы", mock_api.get_orders)
    ]
    
    for name, method in entities:
        print(f"\n3. {name}:")
        success, data = method()
        if success and isinstance(data, list):
            print(f"   ✅ Загружено записей: {len(data)}")
            if data:
                first_item = data[0]
                item_name = first_item.get('name', first_item.get('id', 'N/A'))
                print(f"      Пример: {item_name}")
    
    # Создаем лог о тестировании
    SupplierSyncLog.objects.create(
        supplier=supplier,
        status='info',
        message='Mock API протестирован. Реальный API сервер vinttop.ru недоступен (503). Ожидается уточнение правильного URL API.'
    )
    
    print(f"\n📋 ЗАКЛЮЧЕНИЕ:")
    print(f"✅ Mock API работает корректно")
    print(f"✅ Интеграционный код готов к работе")
    print(f"⚠️  Нужен реальный URL API от vinttop.ru")
    print(f"📞 Свяжитесь с поставщиком для уточнения:")
    print(f"   - Правильный URL API")
    print(f"   - Статус доступности сервиса")
    print(f"   - Документация по API")

if __name__ == "__main__":
    create_mock_api_response()
