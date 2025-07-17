from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'banners', views.BannerViewSet)
router.register(r'sliders', views.SliderViewSet)
router.register(r'slider-items', views.SliderItemViewSet)
router.register(r'news', views.NewsViewSet)
router.register(r'html-blocks', views.HtmlBlockViewSet)
router.register(r'store-settings', views.StoreSettingsViewSet)

app_name = 'cms'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Web URLs
    path('', views.home, name='home'),
]
