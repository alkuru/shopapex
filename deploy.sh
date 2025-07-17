#!/bin/bash
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
