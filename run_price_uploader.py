#!/usr/bin/env python3
"""
Простой скрипт для запуска программы загрузки прайса
"""

import sys
import os

# Добавляем путь к Django проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')

# Импортируем Django
import django
django.setup()

# Запускаем программу
from price_uploader import main

if __name__ == "__main__":
    main() 