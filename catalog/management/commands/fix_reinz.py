from django.core.management.base import BaseCommand
from catalog.models import MikadoProduct
from django.db import transaction

class Command(BaseCommand):
    help = 'Исправление брендов Victor Reinz на REINZ'

    def handle(self, *args, **options):
        self.stdout.write('=== ИСПРАВЛЕНИЕ БРЕНДОВ VICTOR REINZ ===\n')
        
        try:
            with transaction.atomic():
                # Обновляем все варианты Victor Reinz на REINZ
                variants = ['Victor Reinz', 'VICTOR REINZ', 'VictorReinz']
                
                total_updated = 0
                for brand in variants:
                    count = MikadoProduct.objects.filter(brand=brand).update(brand='REINZ')
                    if count > 0:
                        self.stdout.write(f'✅ Обновлено "{brand}" -> "REINZ": {count} товаров')
                        total_updated += count
                
                self.stdout.write(f'\n✅ Всего обновлено: {total_updated} товаров')
                
                # Проверяем результат
                remaining = MikadoProduct.objects.filter(
                    brand__icontains='reinz'
                ).exclude(brand='REINZ').count()
                
                if remaining > 0:
                    self.stdout.write(f'\n❌ ВНИМАНИЕ: Осталось {remaining} товаров с неправильным брендом!')
                else:
                    self.stdout.write('\n✅ Все товары Victor Reinz успешно обновлены до REINZ')
        
        except Exception as e:
            self.stdout.write(f'\n❌ ОШИБКА: {str(e)}') 