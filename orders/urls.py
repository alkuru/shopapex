from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)

app_name = 'orders'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
]
