from django.core.management.base import BaseCommand
from catalog.models import MikadosProduct

class Command(BaseCommand):
    help = 'Добавляет тестовые товары бренда ZF PARTS'

    def handle(self, *args, **options):
        # Данные для товаров ZF PARTS
        zf_products = [
            {
                'brand': 'ZF PARTS',
                'article': 'ZF123456',
                'name': 'Подшипник ZF Sachs',
                'price': 2500,
                'stock_quantity': 15,
                'producer_number': 'ZF123456',
                'code': 'ZF001',
                'multiplicity': 1,
                'unit': 'шт',
                'warehouse': 'ЦС-МК'
            },
            {
                'brand': 'ZF PARTS',
                'article': 'ZF789012',
                'name': 'Сцепление ZF Sachs',
                'price': 15000,
                'stock_quantity': 7,
                'producer_number': 'ZF789012',
                'code': 'ZF002',
                'multiplicity': 1,
                'unit': 'шт',
                'warehouse': 'ЦС-МК'
            },
            {
                'brand': 'ZF PARTS',
                'article': 'ZF345678',
                'name': 'Коробка передач ZF',
                'price': 45000,
                'stock_quantity': 3,
                'producer_number': 'ZF345678',
                'code': 'ZF003',
                'multiplicity': 1,
                'unit': 'шт',
                'warehouse': 'ЦС-МК'
            },
            {
                'brand': 'ZF PARTS',
                'article': 'ZF901234',
                'name': 'Тормозная система ZF',
                'price': 8000,
                'stock_quantity': 18,
                'producer_number': 'ZF901234',
                'code': 'ZF004',
                'multiplicity': 1,
                'unit': 'шт',
                'warehouse': 'ЦС-МК'
            },
            {
                'brand': 'ZF PARTS',
                'article': 'ZF567890',
                'name': 'Рулевое управление ZF',
                'price': 12000,
                'stock_quantity': 10,
                'producer_number': 'ZF567890',
                'code': 'ZF005',
                'multiplicity': 1,
                'unit': 'шт',
                'warehouse': 'ЦС-МК'
            }
        ]

        # Добавляем товары
        added_count = 0
        for product_data in zf_products:
            try:
                MikadosProduct.objects.create(**product_data)
                added_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Добавлен товар: {product_data['name']} ({product_data['article']})")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка при добавлении {product_data['article']}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nВсего добавлено товаров ZF PARTS: {added_count}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Общее количество товаров в базе: {MikadosProduct.objects.count()}")
        ) 