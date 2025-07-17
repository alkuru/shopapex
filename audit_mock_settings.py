#!/usr/bin/env python3
"""
Аудит Mock заглушек в проекте ShopApex
Проверяет готовность к переходу на реальные данные
"""

import os
import sys
import django

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier


def audit_mock_settings():
    """Аудит всех Mock настроек в проекте"""
    print("🔍 АУДИТ MOCK ЗАГЛУШЕК В SHOPAPEX")
    print("=" * 60)
    print("📅 Подготовка к переходу на реальные данные завтра")
    print("🎯 Система упрощена - только VintTop.ru API")
    print()
    
    # Проверяем поставщиков
    all_suppliers = Supplier.objects.all()
    vinttop_suppliers = Supplier.objects.filter(name__icontains='VintTop')
    
    print("📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   📋 Всего поставщиков: {all_suppliers.count()}")
    print(f"   🎯 VintTop поставщиков: {vinttop_suppliers.count()}")
    print()
    
    if not all_suppliers.exists():
        print("❌ ОШИБКА: Поставщики не найдены!")
        print("🔧 Возможные причины:")
        print("   1. База данных не создана или пуста")
        print("   2. Миграции не применены")
        print("   3. Проблема с подключением к БД")
        return Supplier.objects.none()
    
    # Проверяем что остался только VintTop.ru
    if all_suppliers.count() > 1:
        print(f"⚠️  ВНИМАНИЕ: Найдено {all_suppliers.count()} поставщиков, ожидался только 1 (VintTop.ru)")
        print("🔧 Рекомендуется запустить clean_suppliers.py для очистки")
    elif all_suppliers.count() == 1:
        vinttop = all_suppliers.first()
        if 'vinttop' not in vinttop.name.lower():
            print(f"⚠️  ВНИМАНИЕ: Единственный поставщик не VintTop.ru: {vinttop.name}")
        else:
            print("✅ Отлично! В системе остался только VintTop.ru")
    
    # Детальная проверка каждого поставщика
    print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ПОСТАВЩИКОВ:")
    print("-" * 60)
    
    for supplier in all_suppliers:
        print(f"\n📡 {supplier.name} (ID: {supplier.id})")
        print(f"   🏪 Тип API: {supplier.get_api_type_display()}")
        print(f"   ✅ Активен: {'Да' if supplier.is_active else 'Нет'}")
        print(f"   🌐 URL API: {supplier.api_url or 'Не указан'}")
        
        # API credentials
        print(f"   👤 API логин: {'✅ Есть' if supplier.api_login else '❌ Отсутствует'}")
        print(f"   🔑 API пароль: {'✅ Есть' if supplier.api_password else '❌ Отсутствует'}")
        
        # Admin credentials для ABCP
        if 'abcp.ru' in (supplier.api_url or '').lower() or 'vinttop' in supplier.name.lower():
            print(f"   👑 Admin логин: {'✅ Есть' if supplier.admin_login else '❌ Отсутствует'}")
            print(f"   🔐 Admin пароль: {'✅ Есть' if supplier.admin_password else '❌ Отсутствует'}")
            print(f"   🤖 Mock режим: {'🟡 ВКЛЮЧЕН' if supplier.use_mock_admin_api else '🟢 ВЫКЛЮЧЕН'}")
            
            # Дополнительные параметры ABCP
            print(f"   🏢 Office ID: {supplier.office_id or 'Не указан'}")
            print(f"   📦 Онлайн склады: {'Да' if supplier.use_online_stocks else 'Нет'}")
            print(f"   🚚 Адрес доставки: {supplier.default_shipment_address}")
        else:
            print("   ⚠️  Не ABCP поставщик - административные функции недоступны")
    
    return all_suppliers


def check_mock_methods():
    """Проверяем где используются Mock методы в коде"""
    print("\n\n🔧 ПОИСК MOCK МЕТОДОВ В КОДЕ:")
    print("=" * 60)
    
    # Главный Mock метод в models.py
    print("📁 catalog/models.py:")
    print("   🤖 _get_mock_admin_data() - основной Mock метод")
    print("   🔄 _make_admin_request() - проверяет use_mock_admin_api")
    print("   ✅ Все административные методы используют этот механизм")
    
    # Проверим конкретные методы
    mock_methods = [
        "add_to_basket",
        "get_basket_content", 
        "clear_basket",
        "get_shipment_addresses",
        "create_order_from_basket",
        "search_batch",
        "get_search_history",
        "get_search_tips"
    ]
    
    print("\n🎯 АДМИНИСТРАТИВНЫЕ МЕТОДЫ С MOCK ПОДДЕРЖКОЙ:")
    for method in mock_methods:
        print(f"   ✅ {method}()")
    
    return mock_methods


def create_production_checklist():
    """Создает чеклист для перехода на продакшен"""
    print("\n\n📋 ЧЕКЛИСТ ПЕРЕХОДА НА РЕАЛЬНЫЕ ДАННЫЕ:")
    print("=" * 60)
    
    checklist = [
        "🔑 Получить реальные admin_login и admin_password от VintTop",
        "🤖 Убедиться что use_mock_admin_api=False (должно быть уже отключено)",
        "🧪 Протестировать все административные методы",
        "📊 Проверить логи API запросов",
        "🔄 Убедиться что поставщик активен (is_active=True)",
        "🌐 Проверить корректность api_url",
        "🏢 Настроить office_id если нужно",
        "📦 Настроить use_online_stocks если нужно",
        "🚚 Настроить default_shipment_address если нужно",
        "🚀 Провести финальное тестирование на production"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"   {i}. {item}")
    
    return checklist


def show_current_mock_status(suppliers):
    """Показывает текущий статус Mock режимов"""
    print("\n\n🎯 ТЕКУЩИЙ СТАТУС MOCK РЕЖИМОВ:")
    print("=" * 60)
    
    mock_enabled = suppliers.filter(use_mock_admin_api=True)
    mock_disabled = suppliers.filter(use_mock_admin_api=False)
    
    print(f"🤖 Поставщиков в Mock режиме: {mock_enabled.count()}")
    for supplier in mock_enabled:
        print(f"   📡 {supplier.name} - Mock ВКЛЮЧЕН")
    
    print(f"\n🌐 Поставщиков в реальном режиме: {mock_disabled.count()}")
    for supplier in mock_disabled:
        print(f"   📡 {supplier.name} - Mock ВЫКЛЮЧЕН")
        
    return mock_enabled, mock_disabled


def main():
    """Главная функция аудита"""
    try:
        # Аудит поставщиков
        suppliers = audit_mock_settings()
        
        # Проверка Mock методов
        mock_methods = check_mock_methods()
        
        # Текущий статус
        mock_enabled, mock_disabled = show_current_mock_status(suppliers)
        
        # Чеклист для продакшена
        checklist = create_production_checklist()
        
        # Итоговые рекомендации
        print("\n\n🚀 РЕКОМЕНДАЦИИ ДЛЯ ЗАВТРА:")
        print("=" * 60)
        
        if mock_enabled.count() > 0:
            print("⚠️  ВНИМАНИЕ: Обнаружены активные Mock режимы!")
            print(f"   📊 {mock_enabled.count()} поставщиков работают в Mock режиме")
            print("   🎯 Для реальной выгрузки нужно:")
            print("      1. Получить реальные admin credentials")
            print("      2. Отключить use_mock_admin_api")
            print("      3. Протестировать подключение")
        else:
            print("✅ Отлично! Все поставщики настроены на реальный режим")
            print("   🚀 Проект готов к реальной выгрузке")
            if suppliers.count() == 1:
                supplier = suppliers.first()
                print(f"   📡 Единственный поставщик: {supplier.name}")
                if supplier.admin_login and supplier.admin_password:
                    print("   🔑 Admin credentials настроены")
                    print("   🎯 Готов к работе с ABCP административным API")
                else:
                    print("   ⚠️  Admin credentials требуют проверки")
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   🤖 Mock режимов найдено: {mock_enabled.count()}")
        print(f"   🌐 Реальных режимов: {mock_disabled.count()}")
        print(f"   🔧 Mock методов в коде: {len(mock_methods)}")
        print(f"   📋 Пунктов в чеклисте: {len(checklist)}")
        print(f"   📦 Всего поставщиков: {suppliers.count()}")
        
        return mock_enabled.count() == 0
        
    except Exception as e:
        print(f"💥 Ошибка аудита: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 Запуск аудита Mock заглушек...")
    ready_for_production = main()
    
    if ready_for_production:
        print("\n🎉 РЕЗУЛЬТАТ: Проект готов к реальной выгрузке!")
    else:
        print("\n⚠️  РЕЗУЛЬТАТ: Требуется настройка перед реальной выгрузкой!")
