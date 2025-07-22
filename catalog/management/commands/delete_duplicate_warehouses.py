from django.core.management.base import BaseCommand
from catalog.models import Product
from django.db import transaction

class Command(BaseCommand):
    help = 'Автоматически удаляет дублирующиеся склады (warehouse) в Product и переназначает все связи.'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Получаем все уникальные значения складов, кроме пустых
            warehouses = Product.objects.values_list('warehouse', flat=True).exclude(warehouse='').distinct()
            total_merged = 0
            for wh in warehouses:
                # Находим все продукты с этим складом (игнорируем регистр и пробелы)
                products = Product.objects.filter(warehouse__iexact=wh.strip())
                if products.count() > 1:
                    # Оставляем только первый продукт с этим складом
                    main_product = products.first()
                    # Остальные продукты переводим на основной склад (если нужно)
                    for p in products.exclude(id=main_product.id):
                        p.warehouse = main_product.warehouse
                        p.save()
                        total_merged += 1
            self.stdout.write(self.style.SUCCESS(f'Обработано {len(warehouses)} складов. Переназначено {total_merged} записей.'))
            # Теперь удаляем дублирующиеся склады (если бы была отдельная модель складов)
            # В данном случае warehouse - это строковое поле, поэтому просто нормализуем значения
            # Если нужно удалить продукты-дубли (с одинаковым warehouse), раскомментируйте ниже:
            # for wh in warehouses:
            #     products = Product.objects.filter(warehouse__iexact=wh.strip())
            #     if products.count() > 1:
            #         products.exclude(id=products.first().id).delete()
            #         self.stdout.write(self.style.WARNING(f'Удалены дубли продуктов для склада: {wh}')) 