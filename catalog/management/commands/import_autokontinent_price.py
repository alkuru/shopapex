import pandas as pd
from django.core.management.base import BaseCommand
from catalog.models import AutoKontinentProduct
from django.utils import timezone
import os
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Импортирует прайс из Excel-файла в AutoKontinentProduct (обновляет по brand+article или создает новые)'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='shopapex/import/СПб-МСК 0033749_250725.xlsx', help='Путь к Excel-файлу прайса')

    def handle(self, *args, **options):
        file_path = options['file']
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return

        self.stdout.write(self.style.NOTICE(f'Загрузка прайса из файла: {file_path}'))
        df = pd.read_excel(file_path)
        required_columns = ['Бренд', 'Код товара', 'Наименование товара', 'Кол-во СПб', 'Кол-во МСК', 'Цена', 'Кратность', 'Ед. Изм.']
        for col in required_columns:
            if col not in df.columns:
                self.stderr.write(self.style.ERROR(f'Нет столбца: {col}'))
                self.stderr.write(self.style.WARNING(f'Список столбцов в файле: {list(df.columns)}'))
                return

        count_created = 0
        count_updated = 0
        total = len(df)
        self.stdout.write(self.style.NOTICE(f'Всего строк в файле: {total}'))
        for idx, row in tqdm(enumerate(df.itertuples(index=False), 1), total=total):
            brand = str(row[0]).strip()
            article = str(row[1]).strip()
            name = str(row[2]).strip()
            stock_spb = int(row[3]) if not pd.isna(row[3]) else 0
            stock_msk = int(row[4]) if not pd.isna(row[4]) else 0
            price = float(row[5]) if not pd.isna(row[5]) else 0.0
            multiplicity = int(row[6]) if not pd.isna(row[6]) else 1
            unit = str(row[7]).strip() if not pd.isna(row[7]) else ''

            obj, created = AutoKontinentProduct.objects.update_or_create(
                brand=brand,
                article=article,
                defaults={
                    'name': name,
                    'stock_spb': stock_spb,
                    'stock_msk': stock_msk,
                    'price': price,
                    'multiplicity': multiplicity,
                    'unit': unit,
                    'updated_at': timezone.now(),
                }
            )
            if created:
                count_created += 1
            else:
                count_updated += 1
            if idx % 1000 == 0:
                self.stdout.write(f'Импортировано строк: {idx}')

        self.stdout.write(self.style.SUCCESS(f'Импорт завершен: создано {count_created}, обновлено {count_updated}')) 