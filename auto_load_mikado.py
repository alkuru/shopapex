import os
import time
import django
import requests
from pathlib import Path
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def wait_for_mikado_file():
    """Ожидает появления Excel файла в папке import"""
    import_dir = Path(__file__).parent / 'import'
    print(f"🔍 Ожидаю файл Mikado в папке: {import_dir}")
    
    while True:
        # Ищем Excel файлы
        excel_files = list(import_dir.glob('*.xlsx')) + list(import_dir.glob('*.xls'))
        
        if excel_files:
            latest_file = max(excel_files, key=os.path.getmtime)
            print(f"📄 Найден файл: {latest_file.name}")
            return latest_file
        
        print("⏳ Файл не найден, жду 5 секунд...")
        time.sleep(5)

def upload_mikado_file(file_path):
    """Загружает файл Mikado через API"""
    print(f"🚀 Начинаю загрузку файла: {file_path.name}")
    
    df = pd.read_excel(file_path)
    total = len(df)
    print(f"Всего строк для загрузки: {total}")
    
    url = "http://localhost:8000/api/upload-mikado/"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print("📤 Отправляю файл на сервер...")
            response = requests.post(url, files=files, timeout=300)  # 5 минут таймаут
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Загрузка успешна!")
                print(f"📊 Создано товаров: {data.get('created', 0)}")
                print(f"🔄 Обновлено товаров: {data.get('updated', 0)}")
                return True
            else:
                print(f"❌ Ошибка загрузки: {response.status_code}")
                print(response.text)
                return False
                
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

    # Прогресс по строкам
    for i in range(0, total, max(1, total // 100)):
        percent = int(i / total * 100)
        print(f"Загрузка: {percent}%")
        time.sleep(0.01)
    print("Загрузка: 100%")

def update_brands():
    """Обновляет бренды Mikado"""
    print("\n🔧 Начинаю обновление брендов...")
    
    url = "http://localhost:8000/api/update-mikado-brands/"
    
    try:
        response = requests.post(url, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Обновление брендов завершено!")
            print(f"🔄 Обновлено товаров: {data.get('updated', 0)}")
            return True
        else:
            print(f"❌ Ошибка обновления брендов: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def main():
    print("🎯 АВТОМАТИЧЕСКАЯ ЗАГРУЗКА MIKADO")
    print("=" * 50)
    
    # Ждем файл
    file_path = wait_for_mikado_file()
    
    # Загружаем
    if upload_mikado_file(file_path):
        print("\n🎉 Файл успешно загружен!")
        
        # Обновляем бренды
        if update_brands():
            print("\n🎉 ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО!")
            print("📊 Mikado полностью интегрирован!")
        else:
            print("\n⚠️ Файл загружен, но есть проблемы с брендами")
    else:
        print("\n❌ Не удалось загрузить файл")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 