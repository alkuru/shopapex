#!/usr/bin/env python
"""
Очистка поставщиков - оставляем только VintTop.ru
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def clean_suppliers():
    """Удаляет всех поставщиков кроме VintTop.ru"""
    print("🗑️ ОЧИСТКА ПОСТАВЩИКОВ")
    print("=" * 50)
    
    # Получаем всех поставщиков
    all_suppliers = Supplier.objects.all()
    print(f"📊 Всего поставщиков: {all_suppliers.count()}")
    
    if all_suppliers.count() == 0:
        print("❌ Поставщики не найдены")
        return
    
    print("\n📋 ТЕКУЩИЕ ПОСТАВЩИКИ:")
    for supplier in all_suppliers:
        print(f"   📦 {supplier.name}")
        print(f"      🔗 {supplier.api_url}")
        print(f"      🤖 Mock: {'ВКЛЮЧЕН' if supplier.use_mock_admin_api else 'ВЫКЛЮЧЕН'}")
    
    # Находим VintTop
    vinttop_suppliers = Supplier.objects.filter(name__icontains='VintTop')
    other_suppliers = Supplier.objects.exclude(name__icontains='VintTop')
    
    print(f"\n✅ VintTop поставщиков (ОСТАВЛЯЕМ): {vinttop_suppliers.count()}")
    for supplier in vinttop_suppliers:
        print(f"   📦 {supplier.name}")
    
    print(f"\n❌ Лишних поставщиков (УДАЛЯЕМ): {other_suppliers.count()}")
    to_delete = []
    for supplier in other_suppliers:
        print(f"   🗑️ {supplier.name}")
        to_delete.append(supplier.name)
    
    # Удаляем лишних поставщиков
    if other_suppliers.exists():
        print(f"\n🔄 Удаляем {other_suppliers.count()} поставщиков...")
        deleted_count = other_suppliers.count()
        other_suppliers.delete()
        print(f"✅ УДАЛЕНО: {deleted_count} поставщиков")
        
        for name in to_delete:
            print(f"   🗑️ {name}")
    else:
        print("\n✅ Лишних поставщиков не найдено")
    
    # Проверяем результат
    remaining_suppliers = Supplier.objects.all()
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"📊 Осталось поставщиков: {remaining_suppliers.count()}")
    
    if remaining_suppliers.exists():
        for supplier in remaining_suppliers:
            print(f"\n📦 {supplier.name}:")
            print(f"   🔗 URL: {supplier.api_url}")
            print(f"   👤 API Login: {'✅ Есть' if supplier.api_login else '❌ Нет'}")
            print(f"   🔑 API Password: {'✅ Есть' if supplier.api_password else '❌ Нет'}")
            print(f"   👑 Admin Login: {'✅ Есть' if supplier.admin_login else '❌ Нет'}")
            print(f"   🔐 Admin Password: {'✅ Есть' if supplier.admin_password else '❌ Нет'}")
            print(f"   🤖 Mock режим: {'🔴 ВКЛЮЧЕН' if supplier.use_mock_admin_api else '✅ ВЫКЛЮЧЕН'}")
            print(f"   ⚡ Активен: {'Да' if supplier.is_active else 'Нет'}")
    else:
        print("❌ Не осталось ни одного поставщика!")
    
    return remaining_suppliers.count()

if __name__ == "__main__":
    remaining_count = clean_suppliers()
    
    print(f"\n🏁 ОЧИСТКА ЗАВЕРШЕНА!")
    if remaining_count == 1:
        print("🎉 Остался только VintTop.ru - система готова для production!")
    elif remaining_count == 0:
        print("⚠️ Все поставщики удалены - нужно будет создать VintTop.ru заново")
    else:
        print(f"⚠️ Осталось {remaining_count} поставщиков - проверьте результат")
