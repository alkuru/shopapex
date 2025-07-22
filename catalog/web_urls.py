    # Корзина и заказы Автоконтинент
"""
Web URLs для каталога товаров
"""
from django.urls import path
from . import web_views

app_name = 'catalog_web'

urlpatterns = [
    path('', web_views.catalog_home, name='home'),
    path('categories/', web_views.categories_list, name='categories'),
    path('category/<int:category_id>/', web_views.category_detail, name='category_detail'),
    path('product/<int:product_id>/', web_views.product_detail, name='product_detail'),
    path('search/', web_views.product_search, name='search'),
    path('advanced-search/', web_views.advanced_search, name='advanced_search'),
    path('quick-search/', web_views.quick_search, name='quick_search'),
    path('supplier-api-search/', web_views.supplier_api_search, name='supplier_api_search'),
    path('cart/', web_views.autokont_basket_get, name='cart'),
    path('cart/add/', web_views.autokont_basket_add, name='cart_add'),
    
    # Поставщики
    path('suppliers/', web_views.supplier_list, name='supplier_list'),
    path('supplier/<int:pk>/', web_views.supplier_detail, name='supplier_detail'),
    path('supplier/<int:pk>/test-api/', web_views.supplier_test_api, name='supplier_test_api'),
    path('supplier/<int:pk>/sync/', web_views.supplier_sync, name='supplier_sync'),
    path('supplier/<int:pk>/products/', web_views.supplier_products, name='supplier_products'),
    
    # API автозапчастей - интеграция
    path('supplier/<int:supplier_id>/entities/', web_views.supplier_entities, name='supplier_entities'),
    path('supplier/<int:supplier_id>/staff/', web_views.supplier_staff_list, name='supplier_staff'),
    path('supplier/<int:supplier_id>/clients/', web_views.supplier_clients_list, name='supplier_clients'),
    path('supplier/<int:supplier_id>/orders/', web_views.supplier_orders_list, name='supplier_orders'),
    path('supplier/<int:supplier_id>/order/<int:order_id>/', web_views.supplier_order_detail, name='supplier_order_detail'),
    path('supplier/<int:supplier_id>/sync-entities/', web_views.supplier_sync_entities, name='supplier_sync_entities'),
    path('supplier/<int:supplier_id>/search/', web_views.supplier_search_products, name='supplier_search'),

    # Тестовый поиск АвтоСпутник
    path('sputnik-search-test/', web_views.sputnik_search_test, name='sputnik_search_test'),
]
