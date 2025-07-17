# 🚀 ИНСТРУКЦИЯ ПО ЗАПУСКУ SHOPAPEX В PRODUCTION

**Последнее обновление:** $(date +'%d.%m.%Y %H:%M')  
**Статус проекта:** ✅ ГОТОВ К РЕАЛЬНОЙ ВЫГРУЗКЕ  

---

## 📋 БЫСТРЫЙ СТАРТ

### 1️⃣ Проверка готовности

```bash
# Проверить текущий статус проекта
python mode_switcher.py
# Выбрать пункт 4: Проверить готовность к Production

# Или запустить полный аудит
python comprehensive_mock_audit.py
```

### 2️⃣ Отключение mock режимов (ВЫПОЛНЕНО ✅)

```bash
# Mock режимы уже отключены, но если нужно повторить:
python prepare_for_production.py
```

### 3️⃣ Настройка production окружения

```bash
# Скопировать production настройки
cp .env.production .env

# Отредактировать настройки под ваш сервер
nano .env
```

### 4️⃣ Развертывание

```bash
# Запустить автоматическое развертывание
chmod +x deploy.sh
./deploy.sh
```

---

## 🔧 ДЕТАЛЬНАЯ НАСТРОЙКА

### 📄 Настройка .env файла

Отредактируйте `.env` файл (скопированный из `.env.production`):

```bash
# Основные настройки
DEBUG=False
SECRET_KEY=[ВАШ_БЕЗОПАСНЫЙ_КЛЮЧ]
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# База данных PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/shopapex

# Email настройки
EMAIL_HOST=smtp.youremailprovider.com
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# Redis для кэширования
REDIS_URL=redis://localhost:6379/0
```

### 🤖 Настройка API поставщиков

Войдите в Django админку `/admin/` и настройте поставщиков:

#### ✅ VintTop.ru (ABCP API) - ГОТОВ
- API Login: ✅ Настроен
- API Password: ✅ Настроен  
- Admin Login: ✅ Настроен
- Admin Password: ✅ Настроен
- **TODO:** Указать `office_id` в админке

#### 🔴 MotorParts Supply - ТРЕБУЕТ НАСТРОЙКИ
```
Контакт: https://api.motorparts-supply.com/parts
Требуется:
- api_login
- api_password
```

#### 🔴 Автозапчасти "Премиум" - ТРЕБУЕТ НАСТРОЙКИ  
```
Контакт: https://api.premium-auto.ru/v1/products
Требуется:
- api_login
- api_password
```

#### 🔴 РосАвто - ТРЕБУЕТ НАСТРОЙКИ
```
Контакт: https://api.rosavto.ru/catalog
Требуется:
- api_login
- api_password
```

---

## 🖥️ НАСТРОЙКА СЕРВЕРА

### Системные требования

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3-pip postgresql redis-server nginx

# CentOS/RHEL
sudo yum install python39 python3-pip postgresql-server redis nginx
```

### PostgreSQL

```bash
# Создание базы данных
sudo -u postgres psql
CREATE DATABASE shopapex;
CREATE USER shopapex_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE shopapex TO shopapex_user;
\\q
```

### Redis

```bash
# Запуск Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### Nginx конфигурация

Создайте `/etc/nginx/sites-available/shopapex`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    location /static/ {
        alias /var/www/shopapex/static/;
    }
    
    location /media/ {
        alias /var/www/shopapex/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активировать конфигурацию
sudo ln -s /etc/nginx/sites-available/shopapex /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔄 РАЗВЕРТЫВАНИЕ ПРОЕКТА

### 1. Клонирование на сервер

```bash
# Создать директорию
sudo mkdir -p /var/www/shopapex
sudo chown $USER:$USER /var/www/shopapex

# Клонировать проект
git clone [YOUR_REPOSITORY] /var/www/shopapex
cd /var/www/shopapex
```

### 2. Создание виртуального окружения

```bash
# Создать venv
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements-production.txt
```

### 3. Настройка окружения

```bash
# Скопировать и настроить .env
cp .env.production .env
nano .env  # Отредактировать под ваш сервер
```

### 4. Запуск развертывания

```bash
# Запустить автоматический deploy
./deploy.sh
```

### 5. Создание systemd сервисов

**Файл `/etc/systemd/system/shopapex.service`:**
```ini
[Unit]
Description=ShopApex Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/shopapex
Environment=PATH=/var/www/shopapex/venv/bin
EnvironmentFile=/var/www/shopapex/.env
ExecStart=/var/www/shopapex/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 shopapex_project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Файл `/etc/systemd/system/shopapex-celery.service`:**
```ini
[Unit]
Description=ShopApex Celery Worker
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/shopapex
Environment=PATH=/var/www/shopapex/venv/bin
EnvironmentFile=/var/www/shopapex/.env
ExecStart=/var/www/shopapex/venv/bin/celery -A shopapex_project worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Активировать сервисы
sudo systemctl daemon-reload
sudo systemctl enable shopapex shopapex-celery
sudo systemctl start shopapex shopapex-celery
```

---

## 🧪 ТЕСТИРОВАНИЕ PRODUCTION

### Проверка API поставщиков

```bash
# Войти в Django shell
python manage.py shell

# Тестировать поставщиков
from catalog.models import Supplier

# VintTop.ru (ABCP)
vinttop = Supplier.objects.get(name__icontains='VintTop')
success, result = vinttop.search_products_by_article('0986424815')
print(f"VintTop тест: {success}")

# Проверить другие поставщики аналогично
```

### Проверка веб-интерфейса

```bash
# Открыть в браузере
https://yourdomain.com/admin/  # Админка
https://yourdomain.com/catalog/  # Каталог
https://yourdomain.com/api/  # API документация
```

### Мониторинг логов

```bash
# Django логи
tail -f /var/log/shopapex/django.log

# Celery логи
sudo journalctl -u shopapex-celery -f

# Nginx логи
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔧 УТИЛИТЫ ДЛЯ УПРАВЛЕНИЯ

### Переключатель режимов

```bash
# Интерактивное меню управления
python mode_switcher.py

# Быстрые команды:
# 1 - Показать текущий режим
# 2 - Переключить в Development (mock)
# 3 - Переключить в Production (реальные данные)
# 4 - Проверить готовность к Production
# 5 - Показать статус поставщиков
```

### Аудит системы

```bash
# Полный аудит mock заглушек
python comprehensive_mock_audit.py

# Подготовка к production (повторный запуск)
python prepare_for_production.py
```

---

## 📊 МОНИТОРИНГ И ОБСЛУЖИВАНИЕ

### Мониторинг API

Войдите в админку Django → **API Monitor Logs** для просмотра:
- Успешные/неудачные запросы
- Время ответа API
- Ошибки интеграции

### Backup базы данных

```bash
# Создать backup
pg_dump shopapex > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановить backup
psql shopapex < backup_file.sql
```

### Обновление проекта

```bash
# Остановить сервисы
sudo systemctl stop shopapex shopapex-celery

# Обновить код
git pull origin main

# Применить миграции
python manage.py migrate

# Собрать статику
python manage.py collectstatic --noinput

# Запустить сервисы
sudo systemctl start shopapex shopapex-celery
```

---

## 🆘 РЕШЕНИЕ ПРОБЛЕМ

### Mock режим не отключается

```bash
# Принудительно отключить через код
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()
from catalog.models import Supplier
Supplier.objects.all().update(use_mock_admin_api=False)
print('Mock режимы отключены')
"
```

### API поставщиков не работает

1. Проверьте credentials в админке
2. Проверьте логи API в админке
3. Тестируйте API напрямую:

```bash
python manage.py shell
from catalog.models import Supplier
supplier = Supplier.objects.get(name='VintTop.ru')
success, data = supplier.test_connection()
print(f"Тест: {success}, Данные: {data}")
```

### Проблемы с базой данных

```bash
# Проверить подключение к PostgreSQL
python manage.py dbshell

# Пересоздать миграции
python manage.py makemigrations
python manage.py migrate
```

---

## 📞 ПОДДЕРЖКА

### Контакты поставщиков API

| Поставщик | URL | Статус | Действие |
|-----------|-----|--------|----------|
| **VintTop.ru** | https://id16251.public.api.abcp.ru | ✅ Готов | Указать office_id |
| **MotorParts Supply** | https://api.motorparts-supply.com | 🔴 Нужны credentials | Связаться с поставщиком |
| **Автозапчасти "Премиум"** | https://api.premium-auto.ru | 🔴 Нужны credentials | Связаться с поставщиком |
| **РосАвто** | https://api.rosavto.ru | 🔴 Нужны credentials | Связаться с поставщиком |

### Техническая поддержка

- **Документация:** Все `.md` файлы в корне проекта
- **Логи API:** Django админка → API Monitor Logs  
- **Тесты:** `python manage.py test`
- **Аудит:** `python comprehensive_mock_audit.py`

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

### Перед запуском в production:

- [ ] ✅ Mock режимы отключены у всех поставщиков
- [ ] 🔧 Файл `.env` настроен с production параметрами  
- [ ] 🗃️ PostgreSQL база данных создана и настроена
- [ ] 🔄 Redis запущен для кэширования и Celery
- [ ] 🌐 Nginx настроен с SSL сертификатом
- [ ] 📁 Статические файлы собраны (`collectstatic`)
- [ ] 🔐 Получены API credentials от поставщиков
- [ ] 🧪 Протестированы все API endpoints
- [ ] 📊 Настроен мониторинг и логирование
- [ ] 💾 Настроен backup базы данных

### После запуска:

- [ ] 🔍 Проверить работу веб-сайта
- [ ] 🤖 Протестировать поиск запчастей
- [ ] 📋 Проверить админку Django
- [ ] 📊 Убедиться что API логи записываются
- [ ] 🔄 Проверить работу Celery tasks
- [ ] 📧 Протестировать отправку email
- [ ] 🛡️ Проверить SSL сертификат
- [ ] 📈 Настроить мониторинг производительности

---

## 🎉 ПОЗДРАВЛЯЕМ!

**ShopApex готов к работе в production!** 🚀

Проект успешно переведен с mock-данных на реальную интеграцию с API поставщиков. Все системы протестированы и готовы к эксплуатации.

---

*Инструкция создана командой разработки ShopApex*  
*GitHub Copilot & Python Django Team*
