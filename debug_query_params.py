#!/usr/bin/env python3
"""
Отладка параметров запроса
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.test import RequestFactory

def debug_query_params():
    rf = RequestFactory()
    req = rf.get('/catalog/search/', {'article': '12-33876-01', 'brand': 'REINZ'})
    
    print("=== ОТЛАДКА ПАРАМЕТРОВ ===")
    print(f"GET params: {dict(req.GET)}")
    print(f"q param: '{req.GET.get('q')}'")
    print(f"article param: '{req.GET.get('article')}'")
    print(f"brand param: '{req.GET.get('brand')}'")
    
    # Тестируем нашу логику
    query = req.GET.get('q', '') or req.GET.get('article', '')
    print(f"query (после логики): '{query}'")
    
    if query:
        print("✅ query не пустой")
    else:
        print("❌ query пустой")

if __name__ == "__main__":
    debug_query_params() 