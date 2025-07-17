from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.conf import settings
        from .supplier_models import Supplier
        def ensure_autokontinent_supplier(sender, **kwargs):
            Supplier.objects.get_or_create(
                name='Автоконтинент',
                defaults={
                    'api_type': 'autoparts',
                    'api_url': 'http://api.autokontinent.ru/v1/',
                    'api_login': getattr(settings, 'AUTOKONT_LOGIN', ''),
                    'api_password': getattr(settings, 'AUTOKONT_PASSWORD', ''),
                    'is_active': True,
                }
            )
        post_migrate.connect(ensure_autokontinent_supplier, sender=self)
