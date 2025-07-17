import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

django.setup()

from catalog.models import Product
from catalog.abcp_api import get_purchase_price

def update_all_purchase_prices():
    products = Product.objects.all()
    updated = 0
    for product in products:
        brand = product.brand.name if product.brand else None
        if brand and brand.lower() == 'mann':
            brand = 'MANN-FILTER'
        # 1. Пробуем исходный артикул
        article = product.article
        price = get_purchase_price(article, brand)
        # 2. Если не найдено — пробуем без пробелов и в верхнем регистре
        if price is None:
            article2 = article.replace(' ', '').upper()
            if article2 != article:
                price = get_purchase_price(article2, brand)
        if price is not None:
            product.purchase_price = Decimal(price)
            product.save(update_fields=['purchase_price'])
            print(f"Обновлено: {product.article} — {product.purchase_price}")
            updated += 1
        else:
            print(f"Нет цены для: {product.article} (brand: {brand})")
    print(f"\nИтого обновлено: {updated} из {products.count()}")

if __name__ == "__main__":
    update_all_purchase_prices()
