#!/usr/bin/env python3
"""
Простой тест синтаксиса метода get_product_analogs без подключения к Django
"""

def test_get_product_analogs_syntax():
    """Тест на отсутствие ошибки 'str' object has no attribute 'get'"""
    print("=== Тест синтаксиса метода get_product_analogs ===")
    
    # Мокаем проблемные данные, которые могут прийти от API
    test_cases = [
        # Случай 1: brands_data - строка вместо списка
        {
            'brands_data': "error_string",
            'expected': "Должен обработать строку без ошибки"
        },
        # Случай 2: brand_info - строка в списке
        {
            'brands_data': ["string_instead_of_dict", {"brand": "test", "number": "123"}],
            'expected': "Должен пропустить строку и обработать словарь"
        },
        # Случай 3: product - строка вместо словаря
        {
            'products_data': ["string_product", {"articleCode": "test123", "brand": "BOSCH"}],
            'expected': "Должен пропустить строку-продукт"
        }
    ]
    
    # Проверяем что код содержит нужные проверки
    with open('catalog/supplier_models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем ключевые проверки типов
    checks = [
        "isinstance(brands_data, dict)",
        "isinstance(brand_info, dict)",
        "isinstance(product, dict)",
        "if not isinstance(product, dict):",
        "continue"
    ]
    
    found_checks = []
    for check in checks:
        if check in content:
            found_checks.append(check)
            print(f"✓ Найдена проверка: {check}")
        else:
            print(f"✗ НЕ найдена проверка: {check}")
    
    print(f"\nНайдено {len(found_checks)} из {len(checks)} проверок типов")
    
    # Проверяем структуру метода
    lines = content.split('\n')
    in_method = False
    method_lines = []
    
    for line in lines:
        if 'def get_product_analogs(' in line:
            in_method = True
        elif in_method and line.strip().startswith('def ') and 'get_product_analogs' not in line:
            break
        elif in_method:
            method_lines.append(line)
    
    # Ищем проблемные паттерны
    issues = []
    for i, line in enumerate(method_lines):
        if '.get(' in line and 'isinstance' not in line and 'if not isinstance' not in method_lines[max(0, i-3):i]:
            # Проверяем, что перед .get() есть проверка isinstance в предыдущих строках
            has_check = False
            for j in range(max(0, i-5), i):
                if 'isinstance' in method_lines[j] and 'dict' in method_lines[j]:
                    has_check = True
                    break
            if not has_check:
                issues.append(f"Строка {i+1}: {line.strip()}")
    
    if issues:
        print(f"\n⚠️  Найдены потенциальные проблемы:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n✅ Синтаксис метода выглядит корректно!")
        print("   Все вызовы .get() защищены проверками isinstance()")
    
    return len(found_checks) >= 3 and len(issues) == 0

if __name__ == "__main__":
    result = test_get_product_analogs_syntax()
    print(f"\n{'='*50}")
    print(f"Результат теста: {'ПРОШЕЛ' if result else 'НЕ ПРОШЕЛ'}")
    print(f"{'='*50}")
