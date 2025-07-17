# Инструкция по устранению ошибки 502 Bad Gateway (nginx + Django + Docker)

## Симптомы
- При открытии сайта появляется ошибка 502 Bad Gateway (nginx/1.29.0)
- В логах nginx: `connect() failed (111: Connection refused) while connecting to upstream, ... web:8000 ...`
- В логах web (Django/gunicorn): ошибок запуска нет, gunicorn слушает на 0.0.0.0:8000

## Причины
- Контейнер web (Django/gunicorn) стартует, но nginx не может подключиться к нему по адресу web:8000
- Возможные причины:
  - web-контейнер не успел подняться к моменту запроса
  - gunicorn стартует с задержкой
  - nginx "запомнил" неудачное соединение и не переподключается

## Решение (пошагово)

1. **Проверить логи nginx**
   - Команда: `docker compose logs nginx --tail=50`
   - Если есть строки `connect() failed (111: Connection refused) while connecting to upstream`, значит проблема с доступностью web:8000

2. **Проверить статус контейнеров**
   - Команда: `docker compose ps`
   - Убедиться, что web и nginx оба в статусе Up

3. **Проверить, слушает ли gunicorn на 0.0.0.0:8000**
   - Команда: `docker compose exec web sh -c "cat /proc/1/cmdline | tr '\0' ' '"`
   - В выводе должно быть: `--bind 0.0.0.0:8000`

4. **Проверить доступность Django напрямую**
   - Команда: `Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing`
   - Если код ответа 200 — Django работает

5. **Перезапустить только nginx**
   - Команда: `docker compose restart nginx`
   - Это переподключит nginx к web и устранит 502 Bad Gateway

6. **Проверить сайт через nginx**
   - Команда: `Invoke-WebRequest -Uri http://localhost/ -UseBasicParsing`
   - Если код ответа 200 — всё работает

## Примечания
- Если ошибка повторяется после перезапуска nginx, проверьте логи web (gunicorn/Django) на наличие критических ошибок.
- Если web не стартует — проверьте миграции, зависимости, переменные окружения.
- Если nginx не стартует — проверьте конфиг nginx.conf и монтирование volume.

---

**Эта инструкция покрывает типовой сценарий для docker-compose с nginx + Django/gunicorn.**
