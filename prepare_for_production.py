#!/usr/bin/env python
"""
Скрипт подготовки проекта ShopApex к production развертыванию
Отключает все mock-режимы и настраивает production конфигурацию
"""

import os
import sys
import django
import secrets
import string

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier
from django.conf import settings

def generate_secure_secret_key():
    """Генерирует безопасный SECRET_KEY"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

def disable_all_mock_modes():
    """Отключает mock режимы у всех поставщиков"""
    print("🤖 ОТКЛЮЧЕНИЕ MOCK РЕЖИМОВ:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.all()
        
        mock_disabled_count = 0
        for supplier in suppliers:
            if hasattr(supplier, 'use_mock_admin_api') and supplier.use_mock_admin_api:
                supplier.use_mock_admin_api = False
                supplier.save()
                mock_disabled_count += 1
                print(f"   ✅ {supplier.name}: Mock режим отключен")
            else:
                print(f"   ✅ {supplier.name}: Mock режим уже был отключен")
        
        print(f"\n📊 Результат: Mock режим отключен у {mock_disabled_count} поставщиков")
        
    except Exception as e:
        print(f"   ❌ Ошибка при отключении mock режимов: {e}")
    
    print()

def create_production_env():
    """Создает .env.production файл с production настройками"""
    print("🌍 СОЗДАНИЕ PRODUCTION ОКРУЖЕНИЯ:")
    print("=" * 50)
    
    # Генерируем новый SECRET_KEY
    new_secret_key = generate_secure_secret_key()
    
    production_env_content = f"""# Production настройки для ShopApex
# ВНИМАНИЕ: Не добавляйте этот файл в Git!

# Django настройки
DEBUG=False
SECRET_KEY={new_secret_key}
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# База данных PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/shopapex

# Безопасность
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email настройки
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.youremailprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# Redis (для кэширования и Celery)
REDIS_URL=redis://localhost:6379/0

# Celery настройки
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Статические файлы
STATIC_ROOT=/var/www/shopapex/static
MEDIA_ROOT=/var/www/shopapex/media
STATIC_URL=/static/
MEDIA_URL=/media/

# Логирование
LOG_LEVEL=INFO
LOG_FILE=/var/log/shopapex/django.log

# API настройки
API_RATE_LIMIT=1000/hour
"""

    # Записываем файл
    try:
        with open('.env.production', 'w', encoding='utf-8') as f:
            f.write(production_env_content)
        
        print("   ✅ Создан файл .env.production")
        print("   🔐 Сгенерирован новый безопасный SECRET_KEY")
        print("   ⚠️  ВАЖНО: Отредактируйте .env.production и укажите свои настройки!")
        
    except Exception as e:
        print(f"   ❌ Ошибка при создании .env.production: {e}")
    
    print()

def create_production_requirements():
    """Создает requirements-production.txt с production зависимостями"""
    print("📦 СОЗДАНИЕ PRODUCTION ЗАВИСИМОСТЕЙ:")
    print("=" * 50)
    
    production_requirements = """# Production зависимости для ShopApex
# Основные Django зависимости
Django>=4.2.0,<5.0
django-cors-headers
django-filter
djangorestframework
django-environ
psycopg2-binary

# База данных и кэширование
redis
django-redis

# Фоновые задачи
celery
celery[redis]

# Мониторинг и логирование
sentry-sdk[django]
django-debug-toolbar  # Только для development

# Веб-сервер
gunicorn
whitenoise[brotli]

# Безопасность
django-ratelimit
django-csp

# API документация
drf-spectacular

# Обработка изображений
Pillow

# Утилиты
requests
python-dateutil
pytz

# Тестирование (только для CI)
pytest
pytest-django
coverage
"""

    try:
        with open('requirements-production.txt', 'w', encoding='utf-8') as f:
            f.write(production_requirements)
        
        print("   ✅ Создан файл requirements-production.txt")
        print("   📋 Включены все необходимые production зависимости")
        
    except Exception as e:
        print(f"   ❌ Ошибка при создании requirements-production.txt: {e}")
    
    print()

def check_supplier_credentials():
    """Проверяет настройки поставщиков для production"""
    print("🔐 ПРОВЕРКА НАСТРОЕК ПОСТАВЩИКОВ:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.filter(is_active=True)
        
        ready_count = 0
        need_setup = []
        
        for supplier in suppliers:
            print(f"\n📦 {supplier.name}:")
            
            issues = []
            
            # Проверяем основные credentials
            if not supplier.api_login:
                issues.append("❌ Не указан api_login")
            else:
                print("   ✅ API Login настроен")
            
            if not supplier.api_password:
                issues.append("❌ Не указан api_password")
            else:
                print("   ✅ API Password настроен")
            
            # Для ABCP API проверяем дополнительные параметры
            if 'abcp.ru' in supplier.api_url.lower():
                if not supplier.admin_login:
                    issues.append("❌ Не указан admin_login для ABCP")
                else:
                    print("   ✅ Admin Login настроен")
                
                if not supplier.admin_password:
                    issues.append("❌ Не указан admin_password для ABCP")
                else:
                    print("   ✅ Admin Password настроен")
                
                if not supplier.office_id:
                    issues.append("⚠️  Рекомендуется указать office_id")
                else:
                    print("   ✅ Office ID настроен")
            
            # Проверяем mock режим
            if hasattr(supplier, 'use_mock_admin_api') and supplier.use_mock_admin_api:
                issues.append("🤖 Mock режим все еще включен!")
            else:
                print("   ✅ Mock режим отключен")
            
            if issues:
                print("   🔴 Требует настройки:")
                for issue in issues:
                    print(f"      {issue}")
                need_setup.append(supplier.name)
            else:
                print("   ✅ Готов к production")
                ready_count += 1
        
        print(f"\n📊 СВОДКА:")
        print(f"   ✅ Готовы к production: {ready_count} поставщиков")
        print(f"   🔴 Требуют настройки: {len(need_setup)} поставщиков")
        
        if need_setup:
            print("\n🔧 ПОСТАВЩИКИ, ТРЕБУЮЩИЕ НАСТРОЙКИ:")
            for name in need_setup:
                print(f"      - {name}")
        
    except Exception as e:
        print(f"   ❌ Ошибка при проверке поставщиков: {e}")
    
    print()

def create_deployment_script():
    """Создает скрипт развертывания"""
    print("🚀 СОЗДАНИЕ СКРИПТА РАЗВЕРТЫВАНИЯ:")
    print("=" * 50)
    
    deployment_script = """#!/bin/bash
# Скрипт развертывания ShopApex в production

echo "🚀 Развертывание ShopApex в production..."

# Проверяем переменные окружения
if [ -f ".env.production" ]; then
    export $(cat .env.production | xargs)
    echo "✅ Загружены production переменные"
else
    echo "❌ Файл .env.production не найден!"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install -r requirements-production.txt

# Собираем статические файлы
echo "📁 Сборка статических файлов..."
python manage.py collectstatic --noinput

# Выполняем миграции
echo "🗃️ Выполнение миграций..."
python manage.py migrate

# Создаем суперпользователя (если нужно)
echo "👤 Создание суперпользователя..."
python manage.py createsuperuser --noinput || echo "Суперпользователь уже существует"

# Загружаем фикстуры (если есть)
if [ -f "fixtures/initial_data.json" ]; then
    echo "📋 Загрузка начальных данных..."
    python manage.py loaddata fixtures/initial_data.json
fi

# Проверяем конфигурацию
echo "🔍 Проверка конфигурации..."
python manage.py check --deploy

# Запускаем тесты
echo "🧪 Запуск тестов..."
python manage.py test --keepdb

echo "✅ Развертывание завершено!"
echo "🌐 Не забудьте настроить веб-сервер (nginx/apache)"
echo "🔄 Запустите Celery для фоновых задач"
echo "📊 Настройте мониторинг и логирование"
"""

    try:
        with open('deploy.sh', 'w', encoding='utf-8') as f:
            f.write(deployment_script)
        
        # Делаем файл исполняемым (на Unix системах)
        os.chmod('deploy.sh', 0o755)
        
        print("   ✅ Создан скрипт развертывания deploy.sh")
        print("   🔧 Скрипт готов для использования в production")
        
    except Exception as e:
        print(f"   ❌ Ошибка при создании скрипта развертывания: {e}")
    
    print()

def show_final_instructions():
    """Показывает финальные инструкции"""
    print("📋 ФИНАЛЬНЫЕ ИНСТРУКЦИИ ДЛЯ PRODUCTION:")
    print("=" * 60)
    
    instructions = [
        "🔧 НАСТРОЙКИ:",
        "   1. Отредактируйте .env.production с вашими настройками",
        "   2. Настройте PostgreSQL базу данных",
        "   3. Настройте Redis для кэширования и Celery",
        "   4. Получите SSL сертификат для HTTPS",
        "",
        "🤖 API ПОСТАВЩИКОВ:",
        "   1. Свяжитесь с поставщиками для получения production credentials",
        "   2. Обновите api_login, api_password для всех поставщиков",
        "   3. Для ABCP API получите admin_login, admin_password",
        "   4. Уточните office_id и другие параметры",
        "",
        "🚀 РАЗВЕРТЫВАНИЕ:",
        "   1. Скопируйте проект на production сервер",
        "   2. Запустите ./deploy.sh",
        "   3. Настройте nginx/apache",
        "   4. Настройте systemd сервисы для Django и Celery",
        "",
        "🔒 БЕЗОПАСНОСТЬ:",
        "   1. Настройте firewall",
        "   2. Настройте backup базы данных",
        "   3. Настройте мониторинг логов",
        "   4. Протестируйте все функции API",
        "",
        "📊 МОНИТОРИНГ:",
        "   1. Настройте Sentry для отслеживания ошибок",
        "   2. Настройте мониторинг производительности",
        "   3. Настройте уведомления о проблемах",
        "   4. Создайте дашборд для метрик API",
        "",
        "✅ ПРОВЕРКА:",
        "   - Все mock режимы отключены",
        "   - Production настройки созданы",
        "   - Скрипт развертывания готов",
        "   - Документация обновлена"
    ]
    
    for instruction in instructions:
        print(instruction)
    
    print()

def main():
    """Основная функция подготовки к production"""
    print("🚀 ПОДГОТОВКА SHOPAPEX К PRODUCTION")
    print("=" * 60)
    print("Автоматическое отключение mock-режимов и настройка production\n")
    
    # Выполняем все этапы подготовки
    disable_all_mock_modes()
    create_production_env()
    create_production_requirements()
    check_supplier_credentials()
    create_deployment_script()
    show_final_instructions()
    
    print("🎯 ПОДГОТОВКА К PRODUCTION ЗАВЕРШЕНА!")
    print("=" * 60)
    print("📁 Созданы файлы:")
    print("   - .env.production")
    print("   - requirements-production.txt")
    print("   - deploy.sh")
    print("\n🔧 Следуйте инструкциям выше для завершения настройки")

if __name__ == "__main__":
    main()
