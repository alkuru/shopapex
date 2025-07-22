import requests
from django.core.management.base import BaseCommand
from catalog.sputnik_api import get_sputnik_token

API_URL = 'https://api.auto-sputnik.ru'
LOGIN = '89219520754'
PASSWORD = '89219520754'

class Command(BaseCommand):
    help = 'Автоматический поиск товаров через API auto-sputnik.ru по артикулу и бренду.'

    def add_arguments(self, parser):
        parser.add_argument('--articul', type=str, required=True, help='Артикул для поиска')
        parser.add_argument('--brand', type=str, required=True, help='Бренд для поиска')

    def handle(self, *args, **options):
        articul = options['articul']
        brand = options['brand']
        # Получаем токен
        token = get_sputnik_token()
        if not token:
            self.stdout.write(self.style.ERROR('Не удалось получить токен!'))
            return
        # Делаем поиск
        result = self.search_products(token, articul, brand)
        if result:
            self.stdout.write(self.style.SUCCESS('Результаты поиска:'))
            self.stdout.write(str(result))
        else:
            self.stdout.write(self.style.WARNING('Нет результатов или ошибка при поиске.'))

    def search_products(self, token, articul, brand):
        url = f'{API_URL}/products/getproducts'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        data = {'articul': articul, 'brand': brand}
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка поиска: {e}'))
            return None 