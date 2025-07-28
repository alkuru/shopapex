# Документация проекта ShopApex

## Обзор системы

**ShopApex** - это веб-приложение для поиска автозапчастей, объединяющее данные из двух источников:
- **AutoKontinent** - локальная база данных PostgreSQL
- **AutoSputnik** - внешний API через FastAPI

## Архитектура системы

### 1. Docker-контейнеры
```
shopapex/
├── docker-compose.yml          # Оркестрация контейнеров
├── Dockerfile                  # Образ Django приложения
├── nginx.conf                  # Конфигурация Nginx
└── shopapex/                   # Основное Django приложение
    ├── fastapi_test/           # FastAPI сервис
    │   └── main.py            # API для работы с AutoSputnik
    └── shopapex_project/       # Django проект
```

**Контейнеры:**
- `web` (Django + Gunicorn) - основной веб-сервер
- `fastapi` (FastAPI) - прокси для AutoSputnik API
- `db` (PostgreSQL) - основная база данных
- `redis` - кэш и брокер сообщений
- `nginx` - обратный прокси

### 2. Работа с AutoKontinent
- **База данных:** PostgreSQL в контейнере `db`
- **Модель:** `AutoKontinentProduct` в `catalog/models.py`
- **Поля складов:** `stock_spb_north`, `stock_spb`, `stock_msk`
- **Прямой доступ:** через Django ORM

### 3. Работа с AutoSputnik
- **API прокси:** FastAPI сервис (`fastapi_test/main.py`)
- **Эндпоинт:** `/unified_search`
- **Функция:** `search_autosputnik_api()`
- **Таймаут:** 7 секунд на запрос

## Логика поиска

### 1. Объединенный поиск (`unified_search_endpoint`)
```python
# 1. Поиск в базе AutoKontinent
autokontinent_results = search_autokontinent_db(article, brand)

# 2. Поиск в AutoSputnik API
autosputnik_results = search_autosputnik_api(article, brand)

# 3. НОВАЯ ЛОГИКА: Поиск аналогов из AutoSputnik в базе AutoKontinent
analog_articles = set()
for sputnik_item in autosputnik_results:
    analog_article = sputnik_item.get("article", "")
    analog_brand = sputnik_item.get("brand", "")
    if analog_article and analog_article != article:
        analog_articles.add((analog_article, analog_brand))

# Ищем каждый аналог в базе AutoKontinent
autokontinent_analog_results = []
for analog_article, analog_brand in analog_articles:
    analog_results = search_autokontinent_db(analog_article, analog_brand)
    for analog_item in analog_results:
        analog_item["source"] = "autokontinent_analog"
        autokontinent_analog_results.append(analog_item)

# 4. Объединение результатов с приоритетом
combined_results = []
combined_results.extend(autokontinent_results)           # Основные товары
combined_results.extend(autokontinent_analog_results)    # Аналоги из AutoKontinent
combined_results.extend(autosputnik_results)             # Товары AutoSputnik
```

### 2. Приоритеты источников (в `utils_sputnik.py`)
```python
offers.sort(key=lambda o: (
    # Приоритет 1: AutoKontinent товары в наличии
    0 if (o.get('source') == 'autokontinent_db' and o.get('availability', 0) > 0) else
    # Приоритет 2: AutoKontinent аналоги в наличии
    1 if (o.get('source') == 'autokontinent_analog' and o.get('availability', 0) > 0) else
    # Приоритет 3: AutoKontinent товары (не в наличии)
    2 if o.get('source') == 'autokontinent_db' else
    # Приоритет 4: AutoKontinent аналоги (не в наличии)
    3 if o.get('source') == 'autokontinent_analog' else
    # Приоритет 5: AutoSputnik товары
    4 if o.get('source') == 'autosputnik' else
    # Приоритет 6: остальные
    5,
    o.get('price') or 0
))
```

## Нормализация брендов

### 1. Маппинг к формату AutoSputnik
- **Файл:** `brand_analysis_results.json`
- **Создание:** `create_perfect_brand_mapping.py`
- **Применение:** через API `/update-brands/`

### 2. Примеры нормализации
```json
{
  "Mahle": "Knecht/Mahle",
  "Mann": "MANN-FILTER",
  "Mahle kolben": "Knecht/Mahle"
}
```

### 3. Подсветка брендов
- **Фильтр:** `brand_highlight` в `templatetags/brand_extras.py`
- **CSS:** зеленый цвет для MANN-FILTER и Knecht/Mahle

## Отдельные инструменты

### 1. Загрузчик прайса (`price_uploader_standalone.py`)
- **GUI:** Tkinter интерфейс
- **Функции:** загрузка Excel + обновление брендов
- **API:** `/api/upload-price/` и `/api/update-brands/`
- **Прогресс:** полоса прогресса с кэшированием

### 2. Обновление брендов
- **Скрипт:** `create_perfect_brand_mapping.py`
- **API:** `/api/update-brands/`
- **Результат:** обновление поля `brand` в базе

## Ключевые особенности

### 1. Множественные склады
- **AutoKontinent:** СЕВ_СПб, ЦС АК, ЦС АКМСК
- **Отображение:** отдельные записи для каждого склада
- **Логика:** если товар есть на нескольких складах, показываем все

### 2. Аналоги из обеих баз
- **Логика:** аналоги из AutoSputnik ищутся в базе AutoKontinent
- **Источник:** `autokontinent_analog`
- **Приоритет:** выше AutoSputnik, ниже основного AutoKontinent

### 3. Неблокирующие операции
- **Загрузка прайса:** отдельное приложение
- **Обновление брендов:** фоновые задачи
- **Прогресс:** Redis кэш для отслеживания

### 4. Docker окружение
- **Изоляция:** все сервисы в контейнерах
- **Сеть:** внутренняя коммуникация через Docker network
- **Персистентность:** volumes для базы и статических файлов

## Важные файлы

### Django
- `shopapex/catalog/web_views.py` - основные веб-представления
- `shopapex/catalog/utils_sputnik.py` - логика группировки и сортировки
- `shopapex/catalog/models.py` - модели данных
- `shopapex/catalog/admin.py` - админ-панель
- `shopapex/catalog/api_views.py` - API для загрузчика прайса

### FastAPI
- `fastapi_test/main.py` - основной API сервис

### Шаблоны
- `shopapex/templates/catalog/search.html` - страница поиска
- `shopapex/templates/admin/catalog/autokontinentproduct/` - админ-шаблоны

### Отдельные инструменты
- `price_uploader_standalone.py` - GUI загрузчик прайса
- `create_perfect_brand_mapping.py` - создание маппинга брендов
- `brand_analysis_results.json` - маппинг брендов

## Команды Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f web
docker-compose logs -f fastapi

# Пересборка после изменений
docker-compose down
docker-compose up -d --build
```

## API эндпоинты

- `GET /unified_search` - объединенный поиск (FastAPI)
- `POST /api/upload-price/` - загрузка прайса (Django)
- `GET /api/upload-progress/` - прогресс загрузки (Django)
- `POST /api/update-brands/` - обновление брендов (Django)
- `GET /api/update-brands-progress/` - прогресс обновления брендов (Django) 