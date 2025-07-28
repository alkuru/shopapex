import pandas as pd
from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from .models import AutoKontinentProduct


@shared_task(bind=True)
def upload_price_task(self, file_path, clear_existing=False):
    """Фоновая задача для загрузки прайса"""
    try:
        # Устанавливаем начальный прогресс
        cache.set('upload_price_progress', 0)
        
        if clear_existing:
            deleted_count = AutoKontinentProduct.objects.count()
            AutoKontinentProduct.objects.all().delete()
            cache.set('upload_price_progress', 5)  # 5% за удаление
        
        # Читаем Excel файл
        df = pd.read_excel(file_path)
        total_rows = len(df)
        created_count = 0
        updated_count = 0
        
        # Обрабатываем каждую строку
        for index, row in df.iterrows():
            try:
                brand = str(row.get('Бренд', '')).strip()
                article = str(row.get('Код товара', '')).strip()
                name = str(row.get('Наименование товара', '')).strip()
                stock_spb_north = int(row.get('Кол-во СЕВ_СПб', 0)) if pd.notna(row.get('Кол-во СЕВ_СПб')) else 0
                stock_spb = int(row.get('Кол-во СПб', 0)) if pd.notna(row.get('Кол-во СПб')) else 0
                stock_msk = int(row.get('Кол-во МСК', 0)) if pd.notna(row.get('Кол-во МСК')) else 0
                price = float(row.get('Цена', 0)) if pd.notna(row.get('Цена')) else 0
                multiplicity = int(row.get('Кратность', 1)) if pd.notna(row.get('Кратность')) else 1
                unit = str(row.get('Ед. изм.', 'шт')).strip()
                
                if brand and article and name:
                    with transaction.atomic():
                        product, created = AutoKontinentProduct.objects.update_or_create(
                            brand=brand,
                            article=article,
                            defaults={
                                'name': name,
                                'stock_spb_north': stock_spb_north,
                                'stock_spb': stock_spb,
                                'stock_msk': stock_msk,
                                'price': price,
                                'multiplicity': multiplicity,
                                'unit': unit,
                            }
                        )
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
            except Exception as e:
                # Логируем ошибку, но продолжаем обработку
                print(f"Ошибка в строке {index + 2}: {str(e)}")
                continue
            
            # Обновляем прогресс каждые 100 строк
            if index % 100 == 0:
                progress = int((index + 1) / total_rows * 90) + 5  # 5-95%
                cache.set('upload_price_progress', progress)
        
        # Завершение
        cache.set('upload_price_progress', 100)
        
        return {
            'created': created_count,
            'updated': updated_count,
            'total_processed': total_rows
        }
        
    except Exception as e:
        cache.set('upload_price_progress', 0)
        raise e 