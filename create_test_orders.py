#!/usr/bin/env python
"""
Скрипт для создания тестовых заказов
"""
import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.contrib.auth.models import User
from orders.models import Order, OrderItem, OrderStatus, DeliveryMethod, PaymentMethod


def create_test_orders():
    """Создание тестовых заказов"""
    
    # Получаем или создаем тестового пользователя
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тест',
            'last_name': 'Пользователь'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Создан тестовый пользователь: {user.username}")
    
    # Удаляем существующие заказы пользователя
    Order.objects.filter(user=user).delete()
    print("Удалены существующие заказы")
    
    # Создаем заказы с разными статусами
    orders_data = [
        {
            'status': OrderStatus.DELIVERED,
            'delivery_method': DeliveryMethod.COURIER,
            'delivery_company': 'Автоваг (СПб)',
            'delivery_address': 'г Санкт-Петербург, ул 2-я Никитинская, д 53',
            'payment_method': PaymentMethod.CASH,
            'payment_status': True,
            'created_at': timezone.now() - timedelta(days=3),
            'delivered_at': timezone.now() - timedelta(days=1),
            'items': [
                {
                    'manufacturer': 'AMD',
                    'article': 'AMD.FL716',
                    'name': 'Фильтр масляный 15208-9F60A/AMD.FL716 AMD',
                    'price': Decimal('153.40'),
                    'quantity': 20,
                    'item_status': 'Доставлен',
                    'supplier': 'AMD',
                    'warehouse': 'Основной склад'
                }
            ]
        },
        {
            'status': OrderStatus.DELIVERED,
            'delivery_method': DeliveryMethod.COURIER,
            'delivery_company': 'Автоваг (СПб)',
            'delivery_address': 'г Санкт-Петербург, ул 2-я Никитинская, д 53',
            'payment_method': PaymentMethod.CARD,
            'payment_status': True,
            'created_at': timezone.now() - timedelta(days=15),
            'delivered_at': timezone.now() - timedelta(days=12),
            'items': [
                {
                    'manufacturer': 'VERNET',
                    'article': 'TH6245.82J',
                    'name': 'Термостат',
                    'price': Decimal('847.20'),
                    'quantity': 1,
                    'item_status': 'Доставлен',
                    'supplier': 'VERNET',
                    'warehouse': 'Основной склад'
                }
            ]
        },
        {
            'status': OrderStatus.SHIPPED,
            'delivery_method': DeliveryMethod.TRANSPORT,
            'delivery_company': 'ТК Деловые линии',
            'delivery_address': 'г Москва, ул Примерная, д 123',
            'payment_method': PaymentMethod.BANK_TRANSFER,
            'payment_status': True,
            'created_at': timezone.now() - timedelta(days=5),
            'shipped_at': timezone.now() - timedelta(days=2),
            'items': [
                {
                    'manufacturer': 'MANN-FILTER',
                    'article': 'C15300',
                    'name': 'Фильтр воздушный двигателя',
                    'price': Decimal('1250.00'),
                    'quantity': 2,
                    'item_status': 'Отправлен',
                    'supplier': 'MANN-FILTER',
                    'warehouse': 'Основной склад'
                },
                {
                    'manufacturer': 'BOSCH',
                    'article': '0986AF3025',
                    'name': 'Свеча зажигания',
                    'price': Decimal('450.00'),
                    'quantity': 4,
                    'item_status': 'Отправлен',
                    'supplier': 'BOSCH',
                    'warehouse': 'Основной склад'
                }
            ]
        },
        {
            'status': OrderStatus.CONFIRMED,
            'delivery_method': DeliveryMethod.PICKUP,
            'delivery_company': 'Самовывоз',
            'delivery_address': '',
            'payment_method': PaymentMethod.CASH,
            'payment_status': False,
            'created_at': timezone.now() - timedelta(days=1),
            'confirmed_at': timezone.now() - timedelta(hours=12),
            'items': [
                {
                    'manufacturer': 'FILTRON',
                    'article': 'AP005/3',
                    'name': 'Фильтр салона',
                    'price': Decimal('320.00'),
                    'quantity': 1,
                    'item_status': 'Подтверждён',
                    'supplier': 'FILTRON',
                    'warehouse': 'Основной склад'
                }
            ]
        },
        {
            'status': OrderStatus.PENDING,
            'delivery_method': DeliveryMethod.POST,
            'delivery_company': 'Почта России',
            'delivery_address': 'г Екатеринбург, ул Ленина, д 1',
            'payment_method': PaymentMethod.ONLINE,
            'payment_status': False,
            'created_at': timezone.now() - timedelta(hours=2),
            'items': [
                {
                    'manufacturer': 'KNECHT/MAHLE',
                    'article': 'OC47',
                    'name': 'Фильтр масляный',
                    'price': Decimal('280.00'),
                    'quantity': 3,
                    'item_status': 'В обработке',
                    'supplier': 'KNECHT/MAHLE',
                    'warehouse': 'Основной склад'
                }
            ]
        },
        {
            'status': OrderStatus.CANCELLED,
            'delivery_method': DeliveryMethod.COURIER,
            'delivery_company': 'Курьерская служба',
            'delivery_address': 'г Казань, ул Баумана, д 10',
            'payment_method': PaymentMethod.CARD,
            'payment_status': False,
            'created_at': timezone.now() - timedelta(days=7),
            'cancelled_at': timezone.now() - timedelta(days=6),
            'user_comment': 'Отменил заказ по личным причинам',
            'items': [
                {
                    'manufacturer': 'DONALDSON',
                    'article': 'P551123',
                    'name': 'Фильтр топливный',
                    'price': Decimal('890.00'),
                    'quantity': 1,
                    'item_status': 'Отменён',
                    'supplier': 'DONALDSON',
                    'warehouse': 'Основной склад'
                }
            ]
        }
    ]
    
    created_orders = []
    
    for order_data in orders_data:
        # Создаем заказ
        order = Order.objects.create(
            user=user,
            status=order_data['status'],
            delivery_method=order_data['delivery_method'],
            delivery_company=order_data['delivery_company'],
            delivery_address=order_data['delivery_address'],
            payment_method=order_data['payment_method'],
            payment_status=order_data['payment_status'],
            user_comment=order_data.get('user_comment', ''),
            created_at=order_data['created_at'],
            confirmed_at=order_data.get('confirmed_at'),
            shipped_at=order_data.get('shipped_at'),
            delivered_at=order_data.get('delivered_at'),
            cancelled_at=order_data.get('cancelled_at'),
            subtotal=Decimal('0.00'),
            discount=Decimal('0.00'),
            delivery_cost=Decimal('0.00'),
            total=Decimal('0.00')
        )
        
        # Создаем товары в заказе
        subtotal = Decimal('0.00')
        for item_data in order_data['items']:
            item = OrderItem.objects.create(
                order=order,
                manufacturer=item_data['manufacturer'],
                article=item_data['article'],
                name=item_data['name'],
                price=item_data['price'],
                quantity=item_data['quantity'],
                item_status=item_data['item_status'],
                supplier=item_data['supplier'],
                warehouse=item_data['warehouse']
            )
            subtotal += item.cost
        
        # Обновляем стоимость заказа
        order.subtotal = subtotal
        order.total = subtotal
        order.save()
        
        created_orders.append(order)
        print(f"Создан заказ {order.order_number} - {order.status_display}")
    
    print(f"\nСоздано {len(created_orders)} тестовых заказов")
    print(f"Логин: {user.username}")
    print(f"Пароль: testpass123")
    
    return created_orders


if __name__ == '__main__':
    create_test_orders() 