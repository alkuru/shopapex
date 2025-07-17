from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, OrderItemSerializer, OrderStatusHistorySerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """API для работы с заказами"""
    queryset = Order.objects.all().select_related('user', 'status').prefetch_related('items__product', 'status_history')
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'is_paid', 'user']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по дате создания
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Поиск по номеру заказа или имени клиента
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменение статуса заказа"""
        order = self.get_object()
        new_status = request.data.get('status')
        comment = request.data.get('comment', '')
        
        if not new_status:
            return Response(
                {'error': 'Статус обязателен'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Недопустимый статус'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Создаем запись в истории
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            changed_by=request.user,
            comment=comment or f"Статус изменен с {old_status} на {new_status}"
        )
        
        return Response({'message': 'Статус успешно изменен'})
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Получение истории изменения статусов заказа"""
        order = self.get_object()
        history = order.status_history.all().order_by('-changed_at')
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по заказам"""
        queryset = self.get_queryset()
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_orders = queryset.filter(created_at__gte=thirty_days_ago)
        
        stats = {
            'total_orders': queryset.count(),
            'recent_orders': recent_orders.count(),
            'pending_orders': queryset.filter(status='pending').count(),
            'processing_orders': queryset.filter(status='processing').count(),
            'shipped_orders': queryset.filter(status='shipped').count(),
            'delivered_orders': queryset.filter(status='delivered').count(),
            'cancelled_orders': queryset.filter(status='cancelled').count(),
            'total_revenue': sum(order.total_amount for order in queryset),
            'recent_revenue': sum(order.total_amount for order in recent_orders),
        }
        
        return Response(stats)


class OrderItemViewSet(viewsets.ModelViewSet):
    """API для позиций заказа"""
    queryset = OrderItem.objects.all().select_related('order', 'product')
    serializer_class = OrderItemSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset


# Обычные представления для веб-интерфейса
def order_list(request):
    """Список заказов"""
    orders = Order.objects.all().select_related('customer').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


def order_detail(request, order_id):
    """Детальная информация о заказе"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})
