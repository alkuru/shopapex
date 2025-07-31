import pandas as pd
import os
from django.core.management.base import BaseCommand
from catalog.models import AutoKontinentProduct

class Command(BaseCommand):
    help = 'Загружает 5 товаров бренда Auto Gur из прайса AutoKontinent'

    def handle(self, *args, **options):
        """Загружает 5 товаров бренда Auto Gur из прайса AutoKontinent"""
        
        # Путь к файлу прайса
        price_file = "/app/import/СЕВ_СПб-СПб-МСК 05141_310725.xlsx"
        
        if not os.path.exists(price_file):
            self.stdout.write(
                self.style.ERROR(f'❌ Файл не найден: {price_file}')
            )
            return
        
        try:
            # Читаем Excel файл
            self.stdout.write(f"📊 Загружаю прайс: {price_file}")
            df = pd.read_excel(price_file)
            self.stdout.write(f"📋 Всего строк в прайсе: {len(df)}")
            
            # Показываем колонки для понимания структуры
            self.stdout.write(f"📝 Колонки в файле: {list(df.columns)}")
            
            # Фильтруем по бренду Auto Gur
            brand_filter = 'Auto Gur'
            filtered_df = df[df['Бренд'].str.contains(brand_filter, case=False, na=False)]
            
            self.stdout.write(f"🔍 Найдено товаров бренда {brand_filter}: {len(filtered_df)}")
            
            if len(filtered_df) == 0:
                self.stdout.write(
                    self.style.ERROR(f'❌ Товары бренда {brand_filter} не найдены')
                )
                # Показываем уникальные бренды для справки
                unique_brands = df['Бренд'].dropna().unique()
                self.stdout.write(f"📋 Доступные бренды: {sorted(unique_brands)}")
                return
            
            # Берем первые 5 товаров
            test_products = filtered_df.head(5)
            
            created_count = 0
            updated_count = 0
            
            self.stdout.write(f"\n🚀 Загружаю 5 товаров бренда {brand_filter}:")
            self.stdout.write("=" * 80)
            
            for index, row in test_products.iterrows():
                try:
                    # Извлекаем данные из строки
                    brand = str(row.get('Бренд', '')).strip()
                    article = str(row.get('Код товара', '')).strip()
                    name = str(row.get('Наименование товара', '')).strip()
                    
                    # Количество на складах
                    stock_spb_north = int(row.get('Кол-во СЕВ_СПб', 0)) if pd.notna(row.get('Кол-во СЕВ_СПб')) else 0
                    stock_spb = int(row.get('Кол-во СПб', 0)) if pd.notna(row.get('Кол-во СПб')) else 0
                    stock_msk = int(row.get('Кол-во МСК', 0)) if pd.notna(row.get('Кол-во МСК')) else 0
                    
                    # Цена и другие параметры
                    price = float(row.get('Цена', 0)) if pd.notna(row.get('Цена')) else 0
                    multiplicity = int(row.get('Кратность', 1)) if pd.notna(row.get('Кратность')) else 1
                    unit = str(row.get('Ед. изм.', 'шт')).strip()
                    
                    if brand and article and name:
                        # Создаем или обновляем товар
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
                            status = "✅ СОЗДАН"
                        else:
                            updated_count += 1
                            status = "🔄 ОБНОВЛЕН"
                        
                        self.stdout.write(f"{status} | {brand} | {article} | {name[:50]}...")
                        self.stdout.write(f"    Цена: {price} руб | СПб: {stock_spb} | МСК: {stock_msk} | СЕВ_СПб: {stock_spb_north}")
                        
                    else:
                        self.stdout.write(f"⚠️  Пропущена строка {index + 2}: недостаточно данных")
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка в строке {index + 2}: {str(e)}')
                    )
                    continue
            
            self.stdout.write("=" * 80)
            self.stdout.write(
                self.style.SUCCESS(f'🎉 Загрузка завершена!')
            )
            self.stdout.write(f"📊 Создано: {created_count}, Обновлено: {updated_count}")
            
            # Проверяем результат
            total_auto_gur = AutoKontinentProduct.objects.filter(brand__icontains='Auto Gur').count()
            self.stdout.write(f"📋 Всего товаров Auto Gur в базе: {total_auto_gur}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при загрузке файла: {str(e)}')
            ) 