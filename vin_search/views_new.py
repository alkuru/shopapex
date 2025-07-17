from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import VinCode, VinSearchRequest, VinRequestItem, VinRequestStatus
from .serializers import (
    VinCodeSerializer, VinCodeListSerializer, VinSearchRequestListSerializer,
    VinSearchRequestDetailSerializer, VinSearchRequestCreateSerializer,
    VinSearchRequestUpdateSerializer, VinRequestItemSerializer,
    VinRequestStatusSerializer, VinSearchStatsSerializer
)


class VinCodeViewSet(viewsets.ModelViewSet):
    """API для работы с VIN кодами"""
    queryset = VinCode.objects.all().prefetch_related('compatible_products')
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['brand', 'model', 'year', 'is_active']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VinCodeListSerializer
        return VinCodeSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Поиск по VIN коду, номеру рамы или модели
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(vin_code__icontains=search) |
                Q(frame_number__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def search_by_vin(self, request):
        """Поиск по VIN коду"""
        vin_code = request.data.get('vin_code', '').strip()
        frame_number = request.data.get('frame_number', '').strip()
        
        if not vin_code and not frame_number:
            return Response(
                {'error': 'Необходимо указать VIN код или номер рамы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        
        if vin_code:
            found_vins = queryset.filter(vin_code__icontains=vin_code)
        elif frame_number:
            found_vins = queryset.filter(frame_number__icontains=frame_number)
        
        if found_vins.exists():
            serializer = self.get_serializer(found_vins, many=True)
            return Response({
                'found': True,
                'results': serializer.data
            })
        else:
            return Response({
                'found': False,
                'message': 'VIN код не найден в базе данных'
            })


class VinSearchRequestViewSet(viewsets.ModelViewSet):
    """API для работы с VIN запросами"""
    queryset = VinSearchRequest.objects.all().select_related('customer').prefetch_related('items')
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'customer']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VinSearchRequestListSerializer
        elif self.action == 'create':
            return VinSearchRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VinSearchRequestUpdateSerializer
        return VinSearchRequestDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Поиск по VIN коду или номеру рамы
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(vin_code__icontains=search) |
                Q(frame_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__phone__icontains=search)
            )
        
        # Фильтрация по дате создания
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменение статуса VIN запроса"""
        vin_request = self.get_object()
        new_status = request.data.get('status')
        comment = request.data.get('comment', '')
        
        if not new_status:
            return Response(
                {'error': 'Статус обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(VinSearchRequest.STATUS_CHOICES):
            return Response(
                {'error': 'Недопустимый статус'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = vin_request.status
        vin_request.status = new_status
        vin_request.save()
        
        # Создаем запись в истории
        VinRequestStatus.objects.create(
            request=vin_request,
            status=new_status,
            changed_by=request.user,
            comment=comment or f"Статус изменен с {old_status} на {new_status}"
        )
        
        return Response({'message': 'Статус успешно изменен'})
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        """Получение истории изменения статусов"""
        vin_request = self.get_object()
        history = vin_request.status_history.all().order_by('-changed_at')
        serializer = VinRequestStatusSerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_request(self, request, pk=None):
        """Обработка VIN запроса"""
        vin_request = self.get_object()
        
        # Попытка найти VIN в базе
        found_vin = None
        if vin_request.vin_code:
            found_vin = VinCode.objects.filter(
                vin_code__icontains=vin_request.vin_code
            ).first()
        elif vin_request.frame_number:
            found_vin = VinCode.objects.filter(
                frame_number__icontains=vin_request.frame_number
            ).first()
        
        if found_vin:
            # Обновляем элементы запроса найденными товарами
            for item in vin_request.items.all():
                # Простая логика поиска по названию
                compatible_products = found_vin.compatible_products.filter(
                    Q(name__icontains=item.name) |
                    Q(article__icontains=item.article)
                )
                if compatible_products.exists():
                    item.product = compatible_products.first()
                    item.found = True
                    item.save()
            
            vin_request.status = 'processed'
            vin_request.save()
            
            return Response({'message': 'Запрос успешно обработан'})
        else:
            return Response(
                {'message': 'VIN код не найден в базе данных'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по VIN запросам"""
        queryset = self.get_queryset()
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_requests = queryset.filter(created_at__gte=thirty_days_ago)
        
        # Топ брендов
        top_brands = []
        vin_codes = VinCode.objects.values('brand').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        for brand_data in vin_codes:
            top_brands.append({
                'brand': brand_data['brand'],
                'count': brand_data['count']
            })
        
        total_requests = queryset.count()
        processed_requests = queryset.filter(status='processed').count()
        success_rate = (processed_requests / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'total_requests': total_requests,
            'pending_requests': queryset.filter(status='pending').count(),
            'processed_requests': processed_requests,
            'total_vin_codes': VinCode.objects.count(),
            'recent_requests': recent_requests.count(),
            'success_rate': round(success_rate, 2),
            'top_brands': top_brands,
        }
        
        return Response(stats)


class VinRequestItemViewSet(viewsets.ModelViewSet):
    """API для позиций VIN запроса"""
    queryset = VinRequestItem.objects.all().select_related('request', 'product')
    serializer_class = VinRequestItemSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        request_id = self.request.query_params.get('request')
        if request_id:
            queryset = queryset.filter(request_id=request_id)
        return queryset


# Обычные представления для веб-интерфейса
def vin_search_home(request):
    """Главная страница VIN поиска"""
    return render(request, 'vin_search/vin_search.html')


def vin_request_list(request):
    """Список VIN запросов"""
    requests = VinSearchRequest.objects.all().select_related('customer').order_by('-created_at')
    return render(request, 'vin_search/request_list.html', {'requests': requests})


def vin_request_detail(request, request_id):
    """Детальная информация о VIN запросе"""
    vin_request = get_object_or_404(VinSearchRequest, id=request_id)
    return render(request, 'vin_search/request_detail.html', {'vin_request': vin_request})
