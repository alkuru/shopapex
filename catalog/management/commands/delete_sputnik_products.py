from django.core.management.base import BaseCommand
from catalog.supplier_models import Supplier, SupplierProduct

class Command(BaseCommand):
    help = 'Удаляет все товары auto-sputnik.ru из локальной базы.'

    def handle(self, *args, **options):
        try:
            supplier = Supplier.objects.get(name='auto-sputnik.ru')
        except Supplier.DoesNotExist:
            self.stdout.write(self.style.WARNING('Поставщик auto-sputnik.ru не найден.'))
            return
        count, _ = SupplierProduct.objects.filter(supplier=supplier).delete()
        self.stdout.write(self.style.SUCCESS(f'Удалено {count} товаров auto-sputnik.ru из локальной базы.')) 