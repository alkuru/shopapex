#!/usr/bin/env python

def analyze_html():
    """Анализирует HTML файл"""
    
    print("🔍 Анализ HTML файла...")
    
    try:
        with open('/tmp/test_search.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Ищем строки с brand-mann
        lines = html_content.split('\n')
        for i, line in enumerate(lines):
            if 'brand-mann' in line:
                print(f"\n📝 Строка {i+1}:")
                print(f"   {line.strip()}")
                
                # Показываем контекст
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print(f"\n   Контекст (строки {start+1}-{end}):")
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"   {marker}{lines[j].strip()}")
                break
        
        # Подсчитываем количество вхождений
        brand_mann_count = html_content.count('brand-mann')
        mann_count = html_content.count('Mann')
        
        print(f"\n📊 Статистика:")
        print(f"   Вхождений 'brand-mann': {brand_mann_count}")
        print(f"   Вхождений 'Mann': {mann_count}")
        
    except FileNotFoundError:
        print("❌ Файл /tmp/test_search.html не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    analyze_html() 