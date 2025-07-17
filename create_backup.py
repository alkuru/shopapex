#!/usr/bin/env python
"""
Создание резервной копии проекта ShopApex
Архивирует весь проект в ZIP файл с временной меткой
"""

import os
import zipfile
import datetime
from pathlib import Path

def create_backup():
    """Создает полную резервную копию проекта"""
    
    print("📦 СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ SHOPAPEX")
    print("=" * 50)
    
    # Получить текущую дату и время
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # Имена файлов
    backup_name = f"shopapex_backup_{timestamp}.zip"
    project_dir = Path(".")
    
    print(f"📅 Дата: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"📁 Проект: {project_dir.absolute()}")
    print(f"💾 Backup файл: {backup_name}")
    print()
    
    # Файлы и папки для исключения
    exclude_patterns = {
        '__pycache__',
        '.venv',
        'venv',
        '.git',
        'node_modules',
        '*.pyc',
        '*.pyo',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        'logs',
        'media/cache',
        'static/cache'
    }
    
    print("🚫 ИСКЛЮЧАЕМЫЕ ФАЙЛЫ:")
    for pattern in sorted(exclude_patterns):
        print(f"   ❌ {pattern}")
    print()
    
    # Подсчет файлов для архивирования
    total_files = 0
    total_size = 0
    
    print("🔍 СКАНИРОВАНИЕ ФАЙЛОВ...")
    
    with zipfile.ZipFile(backup_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Исключить директории
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                # Исключить файлы по паттернам
                if any(pattern.replace('*', '') in file for pattern in exclude_patterns if '*' in pattern):
                    continue
                if file in exclude_patterns:
                    continue
                
                file_path = Path(root) / file
                
                try:
                    # Относительный путь для архива
                    arcname = file_path.relative_to(project_dir)
                    
                    # Добавить в архив
                    zipf.write(file_path, arcname)
                    
                    # Статистика
                    file_size = file_path.stat().st_size
                    total_files += 1
                    total_size += file_size
                    
                    # Показать прогресс каждые 50 файлов
                    if total_files % 50 == 0:
                        print(f"   📁 Обработано файлов: {total_files}")
                    
                except Exception as e:
                    print(f"   ⚠️  Пропущен файл {file_path}: {e}")
    
    # Информация о созданном архиве
    backup_size = Path(backup_name).stat().st_size
    
    print("\n📊 РЕЗУЛЬТАТЫ АРХИВИРОВАНИЯ:")
    print(f"   📁 Файлов заархивировано: {total_files}")
    print(f"   📐 Размер исходных файлов: {format_size(total_size)}")
    print(f"   💾 Размер архива: {format_size(backup_size)}")
    print(f"   📉 Степень сжатия: {((total_size - backup_size) / total_size * 100):.1f}%")
    print(f"   💾 Файл backup: {backup_name}")
    
    return backup_name, total_files, backup_size


def format_size(size_bytes):
    """Форматирование размера файла"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def verify_backup(backup_name):
    """Проверка целостности backup"""
    print(f"\n🔍 ПРОВЕРКА BACKUP: {backup_name}")
    print("-" * 40)
    
    try:
        with zipfile.ZipFile(backup_name, 'r') as zipf:
            # Тест целостности
            bad_files = zipf.testzip()
            
            if bad_files:
                print(f"   ❌ Найдены поврежденные файлы: {bad_files}")
                return False
            else:
                print("   ✅ Архив целостен")
            
            # Проверка ключевых файлов
            key_files = [
                'manage.py',
                'shopapex_project/settings.py',
                'catalog/models.py',
                'catalog/views.py',
                'requirements.txt'
            ]
            
            file_list = zipf.namelist()
            
            print("\n📋 ПРОВЕРКА КЛЮЧЕВЫХ ФАЙЛОВ:")
            missing_files = []
            
            for key_file in key_files:
                if key_file in file_list:
                    print(f"   ✅ {key_file}")
                else:
                    print(f"   ❌ {key_file} - НЕ НАЙДЕН")
                    missing_files.append(key_file)
            
            if missing_files:
                print(f"\n⚠️  Отсутствуют критические файлы: {len(missing_files)}")
                return False
            else:
                print(f"\n✅ Все ключевые файлы присутствуют")
                return True
                
    except Exception as e:
        print(f"   ❌ Ошибка проверки: {e}")
        return False


def create_backup_info(backup_name, total_files, backup_size):
    """Создает информационный файл о backup"""
    
    info_name = backup_name.replace('.zip', '_info.txt')
    now = datetime.datetime.now()
    
    with open(info_name, 'w', encoding='utf-8') as f:
        f.write("📦 ИНФОРМАЦИЯ О РЕЗЕРВНОЙ КОПИИ SHOPAPEX\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"📅 Дата создания: {now.strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"💾 Имя файла: {backup_name}\n")
        f.write(f"📁 Файлов в архиве: {total_files}\n")
        f.write(f"📐 Размер архива: {format_size(backup_size)}\n\n")
        
        f.write("🎯 СОСТОЯНИЕ ПРОЕКТА НА МОМЕНТ BACKUP:\n")
        f.write("-" * 40 + "\n")
        f.write("✅ VintTop.ru поставщик настроен\n")
        f.write("✅ Mock режимы отключены\n")
        f.write("✅ ABCP API интеграция готова\n")
        f.write("✅ База данных настроена\n")
        f.write("✅ Веб-интерфейс работает\n")
        f.write("🔄 Аналоги по артикулу - планируется завтра\n")
        f.write("🔄 Загрузка 100,000 товаров - планируется завтра\n\n")
        
        f.write("🚀 ЦЕЛЬ BACKUP:\n")
        f.write("-" * 15 + "\n")
        f.write("Резервная копия перед загрузкой большого объема товаров\n")
        f.write("и реализацией поиска аналогов по артикулу.\n\n")
        
        f.write("📋 ДЛЯ ВОССТАНОВЛЕНИЯ:\n")
        f.write("-" * 20 + "\n")
        f.write("1. Распаковать архив в новую папку\n")
        f.write("2. Создать виртуальное окружение: python -m venv .venv\n")
        f.write("3. Активировать: .venv\\Scripts\\activate\n")
        f.write("4. Установить зависимости: pip install -r requirements.txt\n")
        f.write("5. Применить миграции: python manage.py migrate\n")
        f.write("6. Запустить сервер: python manage.py runserver\n\n")
        
        f.write("⚠️  ВАЖНО:\n")
        f.write("-" * 10 + "\n")
        f.write("- Архив НЕ содержит .venv (виртуальное окружение)\n")
        f.write("- Архив НЕ содержит __pycache__ (кэш Python)\n")
        f.write("- Архив НЕ содержит .git (история Git)\n")
        f.write("- После восстановления нужно настроить окружение заново\n")
    
    print(f"📄 Создан info файл: {info_name}")
    return info_name


if __name__ == "__main__":
    print("🚀 ЗАПУСК СОЗДАНИЯ BACKUP...")
    
    try:
        # Создание backup
        backup_name, total_files, backup_size = create_backup()
        
        # Проверка backup
        if verify_backup(backup_name):
            print("\n✅ BACKUP СОЗДАН УСПЕШНО!")
            
            # Создание info файла
            info_name = create_backup_info(backup_name, total_files, backup_size)
            
            print(f"\n🎉 РЕЗЕРВНАЯ КОПИЯ ГОТОВА!")
            print(f"💾 Backup: {backup_name}")
            print(f"📄 Info: {info_name}")
            print(f"📁 Файлов: {total_files}")
            print(f"📐 Размер: {format_size(backup_size)}")
            
        else:
            print("\n❌ ОШИБКА ПРИ СОЗДАНИИ BACKUP!")
            print("🔧 Проверьте файлы и повторите попытку")
            
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
