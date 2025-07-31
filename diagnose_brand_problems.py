#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== ДИАГНОСТИКА ПРОБЛЕМ С БРЕНДАМИ MIKADO ===")
    
    # Проверяем подозрительные сочетания
    suspicious_cases = [
        {
            "brand": "MANN-FILTER",
            "suspicious_keywords": ["диск", "тормозной", "колодки", "барабан", "ротор"],
            "description": "MANN-FILTER делает фильтры, не тормоза"
        },
        {
            "brand": "BOSCH",
            "suspicious_keywords": ["фильтр масляный", "фильтр воздушный", "фильтр топливный"],
            "description": "Проверяем правильность фильтров BOSCH"
        },
        {
            "brand": "Knecht/Mahle", 
            "suspicious_keywords": ["диск", "тормозной", "колодки", "свеча"],
            "description": "Knecht/Mahle делает фильтры и поршни, не тормоза"
        },
        {
            "brand": "FILTRON",
            "suspicious_keywords": ["диск", "тормозной", "колодки", "амортизатор"],
            "description": "FILTRON делает фильтры, не другие детали"
        }
    ]
    
    total_problems = 0
    
    for case in suspicious_cases:
        brand = case["brand"]
        keywords = case["suspicious_keywords"]
        description = case["description"]
        
        print(f"\n=== {brand} ===")
        print(f"Проверка: {description}")
        
        brand_products = MikadoProduct.objects.filter(brand=brand)
        brand_count = brand_products.count()
        print(f"Всего товаров с брендом {brand}: {brand_count}")
        
        if brand_count == 0:
            continue
            
        # Ищем подозрительные товары
        suspicious_products = []
        for keyword in keywords:
            found = brand_products.filter(name__icontains=keyword)
            for product in found:
                suspicious_products.append({
                    "article": product.article,
                    "name": product.name,
                    "keyword": keyword,
                    "brand": product.brand
                })
        
        if suspicious_products:
            print(f"❌ НАЙДЕНО {len(suspicious_products)} подозрительных товаров:")
            for i, prod in enumerate(suspicious_products[:10]):  # Показываем первые 10
                print(f"  {i+1}. {prod['article']} | {prod['name'][:80]}...")
                total_problems += 1
        else:
            print(f"✅ Подозрительных товаров не найдено")
    
    print(f"\n=== ОБЩАЯ СТАТИСТИКА ===")
    print(f"Всего проблем найдено: {total_problems}")
    
    # Проверим оригинальные бренды
    print(f"\n=== АНАЛИЗ ОРИГИНАЛЬНЫХ БРЕНДОВ ===")
    
    # Находим товары, которые могли быть неправильно изменены
    problem_articles = [
        "610.3718.20",  # Диск тормозной из скриншота
        "610.3719.20",
        "610.3715.20"
    ]
    
    for article in problem_articles:
        products = MikadoProduct.objects.filter(article=article)
        if products.exists():
            product = products.first()
            print(f"\nАртикул: {article}")
            print(f"Текущий бренд: {product.brand}")
            print(f"Описание: {product.name}")
            
            # Пытаемся определить правильный бренд по описанию
            name_lower = product.name.lower()
            if "zimmermann" in name_lower:
                print(f"💡 Возможный правильный бренд: ZIMMERMANN")
            elif "brembo" in name_lower:
                print(f"💡 Возможный правильный бренд: BREMBO")
            elif "bosch" in name_lower and "диск" in name_lower:
                print(f"💡 Возможный правильный бренд: BOSCH (тормозная система)")
            else:
                print(f"💡 Нужно найти оригинальный бренд")

if __name__ == '__main__':
    main() 