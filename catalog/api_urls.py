from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'catalog_api'

router = DefaultRouter()
router.register(r'categories', views.ProductCategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'supplier-products', views.SupplierProductViewSet)
router.register(r'supplier-logs', views.SupplierSyncLogViewSet)

urlpatterns = router.urls
