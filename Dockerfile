FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8000

# Команда по умолчанию
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "1800", "--workers", "1", "--max-requests", "1000", "--max-requests-jitter", "100", "shopapex_project.wsgi:application"]
