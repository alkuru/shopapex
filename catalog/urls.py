from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import web_views

app_name = 'catalog'

router = DefaultRouter()
router.register(r'categories', views.ProductCategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'supplier-products', views.SupplierProductViewSet)
router.register(r'supplier-logs', views.SupplierSyncLogViewSet)

# API автозапчастей
router.register(r'supplier-staff', views.SupplierStaffViewSet)
router.register(r'supplier-delivery-methods', views.SupplierDeliveryMethodViewSet)
router.register(r'supplier-order-statuses', views.SupplierOrderStatusViewSet)
router.register(r'supplier-client-groups', views.SupplierClientGroupViewSet)
router.register(r'supplier-clients', views.SupplierClientViewSet)
router.register(r'supplier-orders', views.SupplierOrderViewSet)
router.register(r'supplier-balance-transactions', views.SupplierBalanceTransactionViewSet)
router.register(r'oem-numbers', views.OemNumberViewSet)
router.register(r'product-oems', views.ProductOemViewSet)
router.register(r'autokontinent-products', views.AutoKontinentProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', web_views.product_search, name='product_search'),
    path('advanced-search/', views.AdvancedSearchView.as_view(), name='advanced_search'),
    path('quick-search/', views.quick_search_view, name='quick_search'),
    path('supplier-api-search/', views.supplier_api_search_view, name='supplier_api_search'),
    path('product-analogs/<str:article>/', views.ProductAnalogsView.as_view(), name='product_analogs'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),

    # API умного поиска автозапчастей
    path('smart-search/', views.SmartSearchView.as_view(), name='smart_search'),
]
