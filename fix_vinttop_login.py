#!/usr/bin/env python
"""
Скрипт для исправления логина поставщика VintTop.ru
Устанавливает правильный логин: Autovag@bk.ru (с большой буквы)
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def fix_vinttop_login():
    """Исправляет логин поставщика VintTop.ru"""
    
    print("🔍 Поиск поставщика VintTop.ru...")
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        print(f"   Текущий логин: '{supplier.api_login}'")
        
        # Исправляем логин на правильный
        correct_login = "Autovag@bk.ru"
        
        if supplier.api_login != correct_login:
            print(f"🔧 Исправляем логин с '{supplier.api_login}' на '{correct_login}'")
            supplier.api_login = correct_login
            supplier.save()
            print("✅ Логин успешно исправлен!")
        else:
            print("✅ Логин уже правильный!")
        
        # Проверяем все настройки после исправления
        print(f"\n📋 Итоговые настройки поставщика:")
        print(f"   Название: {supplier.name}")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Пароль: {'*' * len(supplier.api_password) if supplier.api_password else 'НЕ ЗАДАН'}")
        print(f"   Тип API: {supplier.get_api_type_display()}")
        
        return True
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        
        # Попробуем найти по другим критериям
        print("\n🔍 Поиск поставщиков с похожими названиями...")
        similar_suppliers = Supplier.objects.filter(
            name__icontains='vint'
        ) | Supplier.objects.filter(
            name__icontains='top'
        ) | Supplier.objects.filter(
            api_url__icontains='abcp'
        )
        
        if similar_suppliers.exists():
            print("📋 Найденные похожие поставщики:")
            for s in similar_suppliers:
                print(f"   - {s.name} (ID: {s.id})")
                print(f"     URL: {s.api_url}")
                print(f"     Логин: {s.api_login}")
        else:
            print("❌ Похожие поставщики не найдены")
        
        return False
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Исправление логина поставщика VintTop.ru")
    print("=" * 50)
    
    success = fix_vinttop_login()
    
    if success:
        print(f"\n✅ Логин успешно исправлен!")
        print(f"🔧 Теперь можно запустить тестирование API")
    else:
        print(f"\n❌ Не удалось исправить логин")
        print(f"🔧 Проверьте наличие поставщика в базе данных")
