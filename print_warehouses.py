from catalog.models import Product

# Вывести все уникальные значения поля warehouse
warehouses = Product.objects.values_list('warehouse', flat=True).distinct()
for w in warehouses:
    print(f'"{w}"')
