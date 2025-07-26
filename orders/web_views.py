from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Order, OrderStatus
from django.http import JsonResponse


@login_required
def orders_page(request):
    """Страница заказов пользователя"""
    
    # Получаем параметры фильтрации
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    period = request.GET.get('period', 'month')
    delivery_method = request.GET.get('delivery_method', 'all')
    
    # Базовый queryset заказов пользователя
    orders = Order.objects.filter(user=request.user)
    
    # Фильтрация по статусу
    if status_filter == 'current':
        orders = orders.filter(status__in=['pending', 'confirmed', 'in_progress', 'shipped'])
    elif status_filter == 'completed':
        orders = orders.filter(status='delivered')
    elif status_filter == 'cancelled':
        orders = orders.filter(status='cancelled')
    elif status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Фильтрация по периоду
    today = timezone.now().date()
    if period == 'month':
        start_date = today - timedelta(days=30)
    elif period == '3months':
        start_date = today - timedelta(days=90)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = None
    
    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    
    # Фильтрация по способу доставки
    if delivery_method != 'all':
        orders = orders.filter(delivery_method=delivery_method)
    
    # Поиск
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(items__manufacturer__icontains=search_query) |
            Q(items__article__icontains=search_query) |
            Q(items__name__icontains=search_query)
        ).distinct()
    
    # Сортировка по дате создания (новые сначала)
    orders = orders.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(orders, 10)  # 10 заказов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Статистика
    total_orders = orders.count()
    total_items = sum(order.items_count for order in orders)
    total_amount = orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Статистика по статусам
    status_stats = {
        'current': orders.filter(status__in=['pending', 'confirmed', 'in_progress', 'shipped']).count(),
        'completed': orders.filter(status='delivered').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }
    
    context = {
        'page_title': 'Мои заказы',
        'page_obj': page_obj,
        'orders': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'period': period,
        'delivery_method': delivery_method,
        'total_orders': total_orders,
        'total_items': total_items,
        'total_amount': total_amount,
        'status_stats': status_stats,
        'status_choices': OrderStatus.choices,
    }
    
    return render(request, 'orders/orders.html', context)


@login_required
def order_detail(request, order_id):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'page_title': f'Заказ {order.order_number}',
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)


def get_orders_data(request):
    """AJAX-представление для получения данных заказов"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # Получаем параметры
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Базовый queryset
    orders = Order.objects.filter(user=request.user)
    
    # Фильтрация по статусу
    if status_filter == 'current':
        orders = orders.filter(status__in=['pending', 'confirmed', 'in_progress', 'shipped'])
    elif status_filter == 'completed':
        orders = orders.filter(status='delivered')
    elif status_filter == 'cancelled':
        orders = orders.filter(status='cancelled')
    elif status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Поиск
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(items__manufacturer__icontains=search_query) |
            Q(items__article__icontains=search_query)
        ).distinct()
    
    # Подготавливаем данные для JSON
    orders_data = []
    for order in orders[:50]:  # Ограничиваем 50 заказами
        order_data = {
            'id': str(order.id),
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.status_display,
            'total': float(order.total),
            'items_count': order.items_count,
            'created_at': order.created_at.strftime('%d.%m.%Y'),
            'delivery_method': order.get_delivery_method_display(),
            'payment_status': order.payment_status,
            'items': []
        }
        
        for item in order.items.all():
            item_data = {
                'manufacturer': item.manufacturer,
                'article': item.article,
                'name': item.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'cost': float(item.cost),
                'item_status': item.item_status,
            }
            order_data['items'].append(item_data)
        
        orders_data.append(order_data)
    
    return JsonResponse({
        'orders': orders_data,
        'total': len(orders_data)
    }) 