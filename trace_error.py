#!/usr/bin/env python
"""
Ловим ошибку с трассировкой стека
"""

import os
import django
import traceback
import sys

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def trace_error():
    """Ловим ошибку с детальной трассировкой"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Тестируем проблемный случай
        print(f"\n🎯 Вызываем get_product_analogs с проблемными параметрами...")
        
        try:
            success, result = supplier.get_product_analogs(
                article="1234567890",
                brand=None,  # Без фильтрации по бренду
                limit=5
            )
            
            print(f"Результат: success={success}")
            if success:
                print(f"Найдено аналогов: {result.get('total_found', 0)}")
            else:
                print(f"Ошибка: {result}")
                
        except AttributeError as e:
            if "'str' object has no attribute 'get'" in str(e):
                print(f"🎯 ПОЙМАЛИ ОШИБКУ: {e}")
                print(f"📍 Трассировка стека:")
                
                # Печатаем полную трассировку
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                
                for line in tb_lines:
                    print(line.rstrip())
                    
                # Дополнительная информация о том, где именно вызывается .get()
                print(f"\n🔍 Анализ места ошибки:")
                
                tb = exc_traceback
                while tb is not None:
                    frame = tb.tb_frame
                    filename = frame.f_code.co_filename
                    lineno = tb.tb_lineno
                    func_name = frame.f_code.co_name
                    
                    if 'catalog/models.py' in filename:
                        print(f"  📁 Файл: {filename}")
                        print(f"  📄 Строка: {lineno}")
                        print(f"  🔧 Функция: {func_name}")
                        
                        # Локальные переменные в этом фрейме
                        local_vars = frame.f_locals
                        print(f"  📊 Локальные переменные:")
                        for var_name, var_value in local_vars.items():
                            if isinstance(var_value, str) and len(var_value) < 200:
                                print(f"    {var_name} (str): {var_value}")
                            else:
                                print(f"    {var_name} ({type(var_value).__name__}): {str(var_value)[:50]}...")
                        
                        print(f"  ─" * 50)
                    
                    tb = tb.tb_next
                    
            else:
                print(f"❌ Другая ошибка AttributeError: {e}")
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    trace_error()
