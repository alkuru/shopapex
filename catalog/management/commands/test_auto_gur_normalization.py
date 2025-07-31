from django.core.management.base import BaseCommand
from catalog.models import AutoKontinentProduct
from catalog.brand_mapping import BRAND_MAPPING

class Command(BaseCommand):
    help = 'Тестирует нормализацию бренда Auto Gur'

    def handle(self, *args, **options):
        """Тестирует нормализацию бренда Auto Gur"""
        
        # Проверяем текущее состояние
        self.stdout.write("🔍 Проверяем текущее состояние товаров Auto Gur:")
        auto_gur_products = AutoKontinentProduct.objects.filter(brand__icontains='Auto Gur')
        
        for product in auto_gur_products:
            self.stdout.write(f"  {product.brand} | {product.article} | {product.name[:50]}...")
        
        self.stdout.write(f"\n📊 Всего товаров Auto Gur: {auto_gur_products.count()}")
        
        # Проверяем маппинг
        self.stdout.write(f"\n🗺️  Маппинг в brand_mapping.py:")
        if 'Auto Gur' in BRAND_MAPPING:
            self.stdout.write(f"  Auto Gur → {BRAND_MAPPING['Auto Gur']}")
        else:
            self.stdout.write("  ❌ Маппинг для Auto Gur не найден!")
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
        auto_gur_after = AutoKontinentProduct.objects.filter(brand__icontains='AUTO-GUR')
        
        for product in auto_gur_after:
            self.stdout.write(f"  {product.brand} | {product.article} | {product.name[:50]}...")
        
        self.stdout.write(f"\n📊 Товаров AUTO-GUR после нормализации: {auto_gur_after.count()}")
        
        if auto_gur_after.count() > 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Нормализация Auto Gur → AUTO-GUR работает корректно!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Нормализация не сработала!')
            ) 