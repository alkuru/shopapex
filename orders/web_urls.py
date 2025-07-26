from django.urls import path
from . import web_views

app_name = 'orders_web'

urlpatterns = [
    path('', web_views.orders_page, name='orders_page'),
    path('<int:order_id>/', web_views.order_detail, name='order_detail'),
    path('api/data/', web_views.get_orders_data, name='get_orders_data'),
] 