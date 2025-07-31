from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.db import transaction
import pandas as pd
import os
import threading
import time
from .models import AutoKontinentProduct
from .models import MikadoProduct
from django.conf import settings


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_price_api(request):
    """API для загрузки прайса"""
    try:
        # Получаем загруженный файл
        uploaded_file = request.FILES.get('file')
        clear_existing = request.data.get('clear_existing', 'false').lower() == 'true'
        
        if not uploaded_file:
            return Response({'error': 'Файл не загружен'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Сохраняем файл во временную директорию
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Запускаем загрузку в фоновом потоке
        upload_thread = threading.Thread(
            target=process_price_upload,
            args=(temp_file_path, clear_existing)
        )
        upload_thread.daemon = True
        upload_thread.start()
        
        return Response({'message': 'Загрузка начата'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def upload_progress_api(request):
    """API для получения прогресса загрузки"""
    try:
        progress = cache.get('upload_price_progress', 0)
        created = cache.get('upload_price_created', 0)
        updated = cache.get('upload_price_updated', 0)
        
        return Response({
            'progress': progress,
            'created': created,
            'updated': updated
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_brands_api(request):
    """API для обновления брендов"""
    try:
        # Запускаем обновление в фоновом потоке
        update_thread = threading.Thread(target=process_brand_update)
        update_thread.daemon = True
        update_thread.start()
        
        return Response({'message': 'Обновление брендов начато'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def update_brands_progress_api(request):
    """API для получения прогресса обновления брендов"""
    try:
        progress = cache.get('update_brands_progress', 0)
        updated = cache.get('update_brands_updated', 0)
        
        return Response({
            'progress': progress,
            'updated': updated
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def process_price_upload(file_path, clear_existing):
    """Фоновая обработка загрузки прайса"""
    try:
        # Устанавливаем начальный прогресс
        cache.set('upload_price_progress', 0)
        cache.set('upload_price_created', 0)
        cache.set('upload_price_updated', 0)
        
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
                cache.set('upload_price_created', created_count)
                cache.set('upload_price_updated', updated_count)
        
        # Завершение
        cache.set('upload_price_progress', 100)
        cache.set('upload_price_created', created_count)
        cache.set('upload_price_updated', updated_count)
        
        print(f"Загрузка завершена. Создано: {created_count}, Обновлено: {updated_count}")
        
    except Exception as e:
        cache.set('upload_price_progress', 0)
        print(f"Ошибка загрузки: {str(e)}")
        raise e


def process_brand_update():
    """Фоновая обработка обновления брендов"""
    try:
        # Устанавливаем начальный прогресс
        cache.set('update_brands_progress', 0)
        cache.set('update_brands_updated', 0)
        
        # Загружаем маппинг брендов
        import json
        import os
        
        if not os.path.exists('brand_analysis_results.json'):
            print("Файл brand_analysis_results.json не найден")
            cache.set('update_brands_progress', 100)
            return
        
        with open('brand_analysis_results.json', 'r', encoding='utf-8') as f:
            brand_mapping = json.load(f)
        
        # Получаем все товары
        products = AutoKontinentProduct.objects.all()
        total_products = products.count()
        updated_count = 0
        
        print(f"Начинаем обновление {total_products} товаров")
        
        # Обновляем бренды
        for index, product in enumerate(products):
            try:
                old_brand = product.brand
                new_brand = brand_mapping.get(old_brand, old_brand)
                
                if old_brand != new_brand:
                    product.brand = new_brand
                    product.save()
                    updated_count += 1
                    
            except Exception as e:
                print(f"Ошибка обновления товара {product.id}: {str(e)}")
                continue
            
            # Обновляем прогресс каждые 1000 товаров
            if index % 1000 == 0:
                progress = int((index + 1) / total_products * 100)
                cache.set('update_brands_progress', progress)
                cache.set('update_brands_updated', updated_count)
                print(f"Прогресс: {progress}%, Обновлено: {updated_count}")
        
        # Завершение
        cache.set('update_brands_progress', 100)
        cache.set('update_brands_updated', updated_count)
        
        print(f"Обновление брендов завершено. Обновлено: {updated_count}")
        
    except Exception as e:
        cache.set('update_brands_progress', 0)
        print(f"Ошибка обновления брендов: {str(e)}")
        raise e 


@api_view(['POST'])
def clear_mikado_products(request):
    """API для очистки всех товаров Mikado"""
    try:
        deleted_count = MikadoProduct.objects.all().delete()[0]
        return Response({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Удалено {deleted_count} товаров Mikado'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def bulk_create_mikado_products(request):
    """API для массового создания товаров Mikado"""
    try:
        products_data = request.data.get('products', [])
        normalize_brands = request.data.get('normalize_brands', True)
        
        if not products_data:
            return Response({'error': 'Нет данных для загрузки'}, status=400)
        
        # Загрузка маппинга брендов для нормализации
        brand_mapping = {}
        if normalize_brands:
            try:
                import json
                import os
                mapping_file = os.path.join(settings.BASE_DIR, 'brand_analysis_results.json')
                if os.path.exists(mapping_file):
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        brand_mapping = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки brand_mapping: {e}")
        
        created_count = 0
        updated_count = 0
        
        for product_data in products_data:
            try:
                # Нормализация бренда
                original_brand = product_data.get('brand', '')
                normalized_brand = brand_mapping.get(original_brand, original_brand)
                
                # Создание или обновление товара
                mikado_product, created = MikadoProduct.objects.update_or_create(
                    brand=normalized_brand,
                    article=product_data.get('article', ''),
                    defaults={
                        'producer_number': product_data.get('producer_number', ''),
                        'code': product_data.get('code', ''),
                        'name': product_data.get('name', ''),
                        'price': product_data.get('price', 0),
                        'stock_quantity': product_data.get('stock_quantity', 0),
                        'multiplicity': product_data.get('multiplicity', 1),
                        'commentary': product_data.get('commentary', ''),
                        'unit': product_data.get('unit', 'шт'),
                        'warehouse': 'ЦС-МК',
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                print(f"Ошибка при создании товара {product_data.get('article', '')}: {e}")
                continue
        
        return Response({
            'success': True,
            'created_count': created_count,
            'updated_count': updated_count,
            'total_processed': len(products_data)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500) 