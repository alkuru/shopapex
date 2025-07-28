#!/usr/bin/env python

def debug_template():
    """Детальный анализ шаблона"""
    
    print("🔍 Детальный анализ шаблона...")
    
    try:
        with open('/tmp/test_search.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Ищем все вхождения strong тегов
        lines = html_content.split('\n')
        strong_lines = []
        
        for i, line in enumerate(lines):
            if '<strong' in line:
                strong_lines.append((i+1, line.strip()))
        
        print(f"\n📝 Найдено {len(strong_lines)} тегов <strong>:")
        for line_num, line in strong_lines:
            print(f"   Строка {line_num}: {line}")
        
        # Ищем строки с Mann
        mann_lines = []
        for i, line in enumerate(lines):
            if 'Mann' in line:
                mann_lines.append((i+1, line.strip()))
        
        print(f"\n📝 Найдено {len(mann_lines)} строк с 'Mann':")
        for line_num, line in mann_lines[:5]:  # Показываем первые 5
            print(f"   Строка {line_num}: {line}")
        
        # Проверяем, есть ли class="brand-mann" в HTML
        if 'class="brand-mann"' in html_content:
            print("\n✅ Найдено class=\"brand-mann\" в HTML")
        else:
            print("\n❌ class=\"brand-mann\" НЕ найден в HTML")
        
        # Проверяем, есть ли class='brand-mann' в HTML
        if "class='brand-mann'" in html_content:
            print("✅ Найдено class='brand-mann' в HTML")
        else:
            print("❌ class='brand-mann' НЕ найден в HTML")
        
    except FileNotFoundError:
        print("❌ Файл /tmp/test_search.html не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    debug_template() 