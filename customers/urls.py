from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'customer-addresses', views.CustomerAddressViewSet)
router.register(r'customer-balances', views.CustomerBalanceViewSet)
router.register(r'customer-notes', views.CustomerNoteViewSet)

app_name = 'customers'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
]
