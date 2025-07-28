#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_c33010_display():
    """Тестирует отображение C33010 AZUMI в поиске OC47"""

    print("=== Тест отображения C33010 AZUMI в поиске OC47 ===\n")

    # Тестируем поиск OC47 через веб-интерфейс
    try:
        url = "http://localhost/catalog/search/"
        params = {"q": "OC47", "brand": "Knecht/Mahle"}

        print(f"Запрос к Django: {url}")
        print(f"Параметры: {params}")

        response = requests.get(url, params=params, timeout=30)

        print(f"Статус ответа: {response.status_code}")

        if response.status_code == 200:
            content = response.text

            # Ищем C33010 AZUMI
            if "C33010" in content and "AZUMI" in content:
                print("✅ НАЙДЕН C33010 AZUMI в ответе Django!")
                
                # Ищем контекст вокруг C33010
                c33010_index = content.find("C33010")
                if c33010_index != -1:
                    start = max(0, c33010_index - 100)
                    end = min(len(content), c33010_index + 200)
                    context = content[start:end]
                    print(f"Контекст C33010: {context}")
            else:
                print("❌ C33010 AZUMI НЕ НАЙДЕН в ответе Django")

            # Ищем информацию о складах
            if "ЦС АК СЕВ" in content:
                print("✅ НАЙДЕН 'ЦС АК СЕВ' в ответе Django!")
            else:
                print("❌ 'ЦС АК СЕВ' НЕ НАЙДЕН в ответе Django")

            if "ЦС АК" in content:
                print("✅ НАЙДЕН 'ЦС АК' в ответе Django")
            else:
                print("❌ 'ЦС АК' НЕ НАЙДЕН в ответе Django")

            # Проверяем общее количество товаров
            if "OC47" in content:
                print("✅ Товар OC47 найден в ответе")
            else:
                print("❌ Товар OC47 НЕ найден в ответе")

        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")

    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_c33010_display() 