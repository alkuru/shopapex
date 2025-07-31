from django.core.management.base import BaseCommand
import json
import os

class Command(BaseCommand):
    help = 'Проверка маппингов брендов'

    def handle(self, *args, **options):
        self.stdout.write('=== ПРОВЕРКА КЛЮЧЕВЫХ МАППИНГОВ ===\n')
        
        try:
            with open('mikado_complete_mapping.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            key_brands = ['Victor Reinz', 'VICTOR REINZ', 'Zimmermann', 'ZIMMERMANN', 'Otto Zimmermann', 'MANN-FILTER']
            
            for brand in key_brands:
                mapped = data.get(brand, 'НЕ НАЙДЕН')
                self.stdout.write(f'{brand}: {mapped}')
            
            self.stdout.write(f'\nВсего маппингов: {len(data)}')
            
        except Exception as e:
            self.stdout.write(f'Ошибка: {e}') 