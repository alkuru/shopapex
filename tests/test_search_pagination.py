from django.test import TestCase
from django.urls import reverse
from catalog.models import Product, ProductCategory

class SearchPaginationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name='Тестовая категория', is_active=True)
        for i in range(35):
            Product.objects.create(
                name=f'Тестовый товар {i}',
                article=f'ART{i}',
                is_active=True,
                category=category
            )

    def test_search_pagination_30_per_page(self):
        response = self.client.get(reverse('catalog_web:search'), {'q': 'Тестовый'})
        self.assertEqual(response.status_code, 200)
        # Проверяем, что на первой странице 30 товаров
        products = response.context['products']
        self.assertEqual(products.paginator.per_page, 30)
        self.assertEqual(len(products.object_list), 30)
        # Проверяем, что на второй странице оставшиеся 5
        response2 = self.client.get(reverse('catalog_web:search'), {'q': 'Тестовый', 'page': 2})
        products2 = response2.context['products']
        self.assertEqual(len(products2.object_list), 5)
