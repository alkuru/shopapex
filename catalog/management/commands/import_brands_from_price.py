import csv
from django.core.management.base import BaseCommand
from catalog.models import Brand

class Command(BaseCommand):
    help = 'Импортирует уникальные бренды из price.csv в Brand'

    def handle(self, *args, **options):
        path = r'c:/Users/Professional/Desktop/import/price.csv/price.csv'
        brands = set()
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                brand = row.get('Бренд')
                if brand:
                    brands.add(brand.strip())
        created = 0
        for b in brands:
            obj, was_created = Brand.objects.get_or_create(name=b)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Добавлено новых брендов: {created}'))
        self.stdout.write(self.style.SUCCESS(f'Всего уникальных брендов в прайсе: {len(brands)}'))
