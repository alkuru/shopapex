#!/usr/bin/env python
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    # Находим артикул с хорошим остатком
    products = MikadoProduct.objects.filter(stock_quantity__gt=0).order_by('?')[:10]
    
    if products:
        test_product = products[0]
        print(f"Тестовый артикул: {test_product.article}")
        print(f"Бренд: {test_product.brand}")
        print(f"Склад: {test_product.warehouse}")
        print(f"Остаток: {test_product.stock_quantity}")
        print(f"Цена: {test_product.price}")
        print(f"Описание: {test_product.name}")
        
        # Проверяем все товары с этим артикулом
        same_article = MikadoProduct.objects.filter(article=test_product.article)
        print(f"\nВсе товары с артикулом {test_product.article}:")
        for p in same_article:
            print(f"  {p.brand} | {p.warehouse} | остаток: {p.stock_quantity}")
    else:
        print("Товары не найдены")

if __name__ == '__main__':
    main() 