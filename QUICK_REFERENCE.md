# Быстрая справка по проекту ShopApex

## 🚀 Быстрый старт

### Запуск проекта
```bash
cd "c:\Users\Professional\Desktop\shopapex"
python manage.py runserver 127.0.0.1:8000
```

### Основные URL
- **Главная**: http://127.0.0.1:8000/
- **Каталог**: http://127.0.0.1:8000/catalog/
- **Поиск**: http://127.0.0.1:8000/catalog/search/?q=артикул
- **VIN поиск**: http://127.0.0.1:8000/vin-search/
- **Админка**: http://127.0.0.1:8000/admin/

---

## 📁 Структура файлов

### Ключевые файлы конфигурации
```
shopapex_project/
├── settings.py           # Основные настройки
├── urls.py              # Главные маршруты
└── wsgi.py              # WSGI для продакшена
```

### Приложения
```
catalog/                 # Каталог товаров
├── models.py           # Product, Supplier, Category
├── web_views.py        # Веб-страницы
├── admin.py            # Админка
└── web_urls.py         # Маршруты

orders/                  # Заказы
customers/              # Клиенты  
vin_search/             # VIN поиск
cms/                    # Контент
accounts/               # Пользователи
```

### Шаблоны
```
templates/
├── base.html           # Базовый шаблон
├── cms/home.html       # Главная страница
├── catalog/search.html # Поиск товаров
└── vin_search/        # VIN поиск
```

---

## 🔧 Полезные команды

### Django команды
```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Django shell
python manage.py shell

# Сбор статики
python manage.py collectstatic
```

### Тестирование
```bash
# Тест поиска по артикулу
python test_article_search.py

# Анализ форм поиска
python analyze_search_forms.py

# Полная диагностика API
python diagnose_abcp_full.py

# Тест веб-сайта
python test_website_search.py
```

### Работа с API
```bash
# Загрузка товаров из ABCP
python load_real_products_test.py

# Улучшение данных товаров
python improve_products_data.py

# Диагностика API
python diagnose_abcp_api.py
```

---

## 📊 Данные в проекте

### Товары
- **Всего**: 22 активных товара
- **Поставщики**: VintTop, ABCP
- **Категории**: Автошины, Покрышки, Провода зажигания

### Примеры артикулов для тестирования
- `TS71912` - Автошина Nordman
- `2286223` - Покрышка KUMHO
- `RCBW223` - Провода зажигания BMW

---

## 🔍 Система поиска

### Настройки поиска
- **Поиск работает только по артикулу** (не по названию)
- **Частичный поиск** поддерживается
- **Регистр не важен**

### Примеры поисковых запросов
```
✅ Работает:
- TS71912 (точный артикул)
- TS7 (частичный артикул)
- 2286 (числовой фрагмент)

❌ Не работает (как и требовалось):
- Автошина (поиск по названию)
- Покрышка (поиск по названию)
```

---

## 🏗️ API интеграция

### ABCP API
```python
# Клиентские методы (работают)
supplier.search_products("масло")
supplier.get_product_info("TS71912")

# Административные методы (mock-режим)
supplier.get_staff_list()
supplier.get_delivery_methods()
supplier.sync_order_statuses()
```

### Переключение mock-режима
В админке Django: **Поставщики** → **ABCP** → поле **"Использовать mock admin API"**

---

## 📝 Документация

### Отчеты и руководства
- `COMPLETE_GUIDE_AUTOPARTS_WEBSITE.md` - **Полное руководство**
- `SEARCH_FIX_REPORT.md` - Отчет об исправлении поиска
- `ABCP_INTEGRATION_COMPLETED.md` - Интеграция ABCP API
- `HOW_TO_GET_ADMIN_CREDENTIALS.md` - Получение admin данных
- `PROJECT_STATUS_FINAL.md` - Финальный статус проекта

### Технические файлы
- `requirements.txt` - Зависимости Python
- `README.md` - Краткое описание проекта
- `docker-compose.yml` - Docker конфигурация

---

## 💾 Резервные копии

### Созданные копии
1. `shopapex_backup_2025-07-07_21-31-17` - исходное состояние
2. `shopapex_backup_search_fix_2025-07-07_23-02-27` - после исправления поиска

### Создание новой копии
```powershell
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "shopapex_backup_$timestamp"
Copy-Item -Path "shopapex" -Destination $backupName -Recurse
```

---

## 🚨 Устранение неполадок

### Проблемы с поиском
1. Очистить кэш браузера (Ctrl+Shift+Delete)
2. Попробовать в режиме инкогнито
3. Проверить консоль браузера (F12)

### Проблемы с API
1. Проверить настройки поставщика в админке
2. Включить mock-режим для тестирования
3. Запустить `diagnose_abcp_full.py`

### Проблемы с сервером
```bash
# Проверка статуса
python -c "import requests; print('OK' if requests.get('http://127.0.0.1:8000').status_code == 200 else 'ERROR')"

# Перезапуск сервера
python manage.py runserver 127.0.0.1:8000
```

---

## 📞 Контакты и поддержка

### Структура проекта готова для:
- ✅ Демонстрации клиентам
- ✅ Дальнейшей разработки  
- ✅ Добавления новых поставщиков
- ✅ Масштабирования функционала
- ✅ Развертывания в продакшен

### Следующие шаги (опционально):
1. Получить реальные admin-данные от VintTop
2. Добавить новых поставщиков API
3. Расширить каталог товаров
4. Настроить систему заказов
5. Добавить оплату и доставку

---
*Последнее обновление: 7 июля 2025 г., 23:10*
