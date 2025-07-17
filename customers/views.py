from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from .models import Customer, CustomerAddress, CustomerBalance, CustomerNote
from .serializers import (
    CustomerListSerializer, CustomerDetailSerializer, CustomerCreateSerializer,
    CustomerUpdateSerializer, CustomerAddressSerializer, CustomerBalanceSerializer,
    CustomerNoteSerializer, CustomerStatsSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """API для работы с клиентами"""
    queryset = Customer.objects.all().select_related('user', 'manager').prefetch_related(
        'addresses', 'balance_transactions', 'notes'
    )
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['preferred_delivery_type', 'manager']
    ordering = ['-registration_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'create':
            return CustomerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        return CustomerDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Поиск по имени, телефону, email или компании
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(phone__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Фильтрация по дате регистрации
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(registration_date__date__gte=date_from)
            except ValueError:
                pass
                
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(registration_date__date__lte=date_to)
            except ValueError:
                pass
        
        return queryset

    @action(detail=True, methods=['post'])
    def update_order_stats(self, request, pk=None):
        """Обновление статистики заказов клиента"""
        customer = self.get_object()
        customer.update_order_stats()
        return Response({'status': 'stats updated'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получение статистики по клиентам"""
        total_customers = Customer.objects.count()
        
        # Клиенты за текущий месяц
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_customers_this_month = Customer.objects.filter(
            registration_date__gte=current_month
        ).count()
        
        # Клиенты с заказами
        customers_with_orders = Customer.objects.filter(
            total_orders_count__gt=0
        ).count()
        
        # Топ клиентов по сумме покупок
        top_customers = Customer.objects.filter(
            total_spent__gt=0
        ).order_by('-total_spent')[:10]
        
        top_customers_data = [
            {
                'id': customer.id,
                'name': customer.full_name,
                'total_spent': float(customer.total_spent),
                'orders_count': customer.total_orders_count
            }
            for customer in top_customers
        ]
        
        # Регистрации по месяцам (последние 12 месяцев)
        customers_by_month = []
        for i in range(12):
            month_start = (datetime.now().replace(day=1) - timedelta(days=31*i)).replace(day=1)
            month_end = (month_start.replace(month=month_start.month % 12 + 1) if month_start.month < 12 
                        else month_start.replace(year=month_start.year + 1, month=1)) - timedelta(days=1)
            
            count = Customer.objects.filter(
                registration_date__range=[month_start, month_end]
            ).count()
            
            customers_by_month.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        customers_by_month.reverse()
        
        stats_data = {
            'total_customers': total_customers,
            'active_customers': total_customers,  # Все считаются активными пока
            'new_customers_this_month': new_customers_this_month,
            'customers_with_orders': customers_with_orders,
            'top_customers': top_customers_data,
            'customers_by_month': customers_by_month
        }
        
        serializer = CustomerStatsSerializer(stats_data)
        return Response(serializer.data)


class CustomerAddressViewSet(viewsets.ModelViewSet):
    """API для работы с адресами клиентов"""
    queryset = CustomerAddress.objects.all()
    serializer_class = CustomerAddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer', 'address_type', 'is_default']


class CustomerBalanceViewSet(viewsets.ModelViewSet):
    """API для работы с балансом клиентов"""
    queryset = CustomerBalance.objects.all().select_related('customer', 'order')
    serializer_class = CustomerBalanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer', 'transaction_type']
    ordering = ['-created_at']


class CustomerNoteViewSet(viewsets.ModelViewSet):
    """API для работы с заметками о клиентах"""
    queryset = CustomerNote.objects.all().select_related('customer', 'author')
    serializer_class = CustomerNoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer', 'author', 'is_important']
    ordering = ['-created_at']
