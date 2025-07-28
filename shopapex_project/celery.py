import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')

app = Celery('shopapex_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Импортируем задачи вручную
try:
    from catalog import tasks
except ImportError:
    pass

# Для теста запуска задачи
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
