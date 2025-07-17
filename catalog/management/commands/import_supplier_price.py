import csv
from django.core.management.base import BaseCommand
from catalog.supplier_models import Supplier, SupplierProduct
from django.utils import timezone

SUPPLIER_NAME = "auto-sputnik.ru"
CSV_PATH = r"c:/Users/Professional/Desktop/import/price.csv/price.csv"

class Command(BaseCommand):
    help = "Импорт прайса поставщика auto-sputnik.ru в SupplierProduct"

    def handle(self, *args, **options):
        supplier, created = Supplier.objects.get_or_create(
            name=SUPPLIER_NAME,
            defaults={
                'is_active': True,
                'api_type': 'custom',
                'data_format': 'csv',
                'sync_frequency': 'manual',
                'website': 'https://auto-sputnik.ru',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Поставщик '{SUPPLIER_NAME}' создан."))
        else:
            self.stdout.write(f"Поставщик '{SUPPLIER_NAME}' уже существует.")

        count = 0
        debug_rows = []
        with open(CSV_PATH, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i < 3:
                    debug_rows.append(str(row))
                article = row.get('Артикул', '').strip()
                brand = row.get('Бренд', '').strip()
                name = row.get('Описание', '').strip()
                price = row.get('Цена', '').replace(',', '.').strip()
                availability = row.get('Количество', '0').strip()
                if not article or not brand or not name:
                    continue
                sp, _ = SupplierProduct.objects.update_or_create(
                    supplier=supplier,
                    article=article,
                    brand=brand,
                    defaults={
                        'name': name,
                        'price': price or 0,
                        'availability': int(availability) if availability.isdigit() else 0,
                        'is_active': True,
                        'updated_at': timezone.now(),
                        'delivery_time': '1-2 дня',  # Добавляем срок поставки
                    }
                )
                count += 1
        self.stdout.write(self.style.WARNING(f"Первые строки файла: {debug_rows}"))
        self.stdout.write(self.style.SUCCESS(f"Импортировано {count} товаров для '{SUPPLIER_NAME}'."))
