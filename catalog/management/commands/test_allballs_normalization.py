from django.core.management.base import BaseCommand
from catalog.models import AutoKontinentProduct
from catalog.brand_mapping import BRAND_MAPPING

class Command(BaseCommand):
    help = 'Тестирует нормализацию бренда AllBalls'

    def handle(self, *args, **options):
        """Тестирует нормализацию бренда AllBalls"""
        
        # Проверяем текущее состояние
        self.stdout.write("🔍 Проверяем текущее состояние товаров AllBalls:")
        allballs_products = AutoKontinentProduct.objects.filter(brand__icontains='AllBalls')
        
        for product in allballs_products:
            self.stdout.write(f"  {product.brand} | {product.article} | {product.name[:50]}...")
        
        self.stdout.write(f"\n📊 Всего товаров AllBalls: {allballs_products.count()}")
        
        # Проверяем маппинг
        self.stdout.write(f"\n🗺️  Маппинг в brand_mapping.py:")
        if 'AllBalls' in BRAND_MAPPING:
            self.stdout.write(f"  AllBalls → {BRAND_MAPPING['AllBalls']}")
        else:
            self.stdout.write("  ❌ Маппинг для AllBalls не найден!")
            return
        
        # Применяем нормализацию
        self.stdout.write(f"\n🚀 Применяем нормализацию...")
        updated_count = 0
        
        for old_brand, new_brand in BRAND_MAPPING.items():
            count = AutoKontinentProduct.objects.filter(brand__iexact=old_brand).update(brand=new_brand)
            if count > 0:
                self.stdout.write(f"  {old_brand} → {new_brand}: {count} товаров")
                updated_count += count
        
        self.stdout.write(f"\n✅ Нормализация завершена! Обновлено: {updated_count} товаров")
        
        # Проверяем результат
        self.stdout.write(f"\n🔍 Проверяем результат:")
        allballs_after = AutoKontinentProduct.objects.filter(brand__icontains='ALL BALLS RACING')
        
        for product in allballs_after:
            self.stdout.write(f"  {product.brand} | {product.article} | {product.name[:50]}...")
        
        self.stdout.write(f"\n📊 Товаров ALL BALLS RACING после нормализации: {allballs_after.count()}")
        
        if allballs_after.count() > 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Нормализация AllBalls → ALL BALLS RACING работает корректно!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Нормализация не сработала!')
            ) 