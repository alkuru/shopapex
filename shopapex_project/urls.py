"""
URL configuration for shopapex_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Настройка админки
admin.site.site_header = "ShopApex - Администрирование"
admin.site.site_title = "ShopApex Admin"
admin.site.index_title = "Панель управления магазином автозапчастей"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include('catalog.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/vin/', include('vin_search.urls')),
    path('api/cms/', include('cms.urls')),
    path('api/accounts/', include('accounts.urls')),
    
    # Web URLs
    path('catalog/', include('catalog.web_urls', namespace='catalog_web')),
    path('vin-search/', include('vin_search.web_urls', namespace='vin_search_web')),
    path('contacts/', include('cms.web_urls', namespace='cms_web')),
    path('accounts/', include('accounts.urls', namespace='accounts_web')),
    path('orders/', include('orders.web_urls', namespace='orders_web')),
    
    path('', include('cms.urls')),  # Главная страница через CMS
]

# Статические файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
