#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def price_label(pn: str) -> str:
    pn = (pn or '').lower()
    # Для АвтоКонтинента: новые названия складов
    if 'цс ак сев' in pn:
        return 'ЦС АК СЕВ'
    if 'цс ак' in pn:
        return 'ЦС АК'
    if 'цс акмск' in pn:
        return 'ЦС АКМСК'
    # Для автоспутник: оставить только 'цс воронеж', 'цс краснодар', 'цс ростов'
    if 'цс воронеж' in pn:
        return 'ЦС-ВР'
    if 'цс краснодар' in pn:
        return 'ЦС-КР'
    if 'цс ростов' in pn:
        return 'ЦС-РВ'
    if 'сторон' in pn:
        return 'СТ-СК'
    if 'транз' in pn:
        return 'Транзит'
    return pn or ''

def test_price_label():
    """Тестирует функцию price_label"""
    
    test_cases = [
        "ЦС АК СЕВ",
        "ЦС АК",
        "ЦС АКМСК",
        "сторонний",
        "транзит",
        "ЦС-ВР",
        "ЦС-КР",
        "ЦС-РВ",
    ]
    
    print("=== Тест функции price_label ===")
    for test_input in test_cases:
        result = price_label(test_input)
        print(f"Вход: '{test_input}' -> Выход: '{result}'")

if __name__ == "__main__":
    test_price_label() 