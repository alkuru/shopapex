from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'requests', views.VinRequestViewSet)

app_name = 'vin_search'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Search endpoints
    path('api/search/', views.VinSearchView.as_view(), name='vin_search'),
    path('api/decode/', views.VinDecodeView.as_view(), name='vin_decode'),
]
