from django.core.management.base import BaseCommand
from catalog.models import MikadoProduct

class Command(BaseCommand):
    help = 'Проверка брендов Victor Reinz'

    def handle(self, *args, **options):
        self.stdout.write('=== ПРОВЕРКА БРЕНДОВ VICTOR REINZ ===\n')
        
        # Проверяем все варианты написания
        variants = ['Victor Reinz', 'VICTOR REINZ', 'VictorReinz', 'REINZ']
        
        for brand in variants:
            count = MikadoProduct.objects.filter(brand=brand).count()
            self.stdout.write(f'Бренд "{brand}": {count} товаров')
        
        # Проверяем все бренды содержащие "reinz"
        all_reinz = MikadoProduct.objects.filter(brand__icontains='reinz').values_list('brand', flat=True).distinct()
        
        if all_reinz:
            self.stdout.write('\nВсе бренды содержащие "reinz":')
            for brand in all_reinz:
                count = MikadoProduct.objects.filter(brand=brand).count()
                self.stdout.write(f'- {brand}: {count} товаров') 