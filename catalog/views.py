from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .smart_search_service import SmartSearchService

# ...существующий код...

# === API для умного поиска автозапчастей ===
class SmartSearchView(APIView):
    """API для умного поиска автозапчастей по артикулу и бренду с кешированием и работой с аналогами"""
    permission_classes = [AllowAny]

    def get(self, request):
        article = request.GET.get('q', '').strip()
        brand = request.GET.get('brand', '').strip()
        search_analogs = request.GET.get('analogs', 'true').lower() == 'true'
        if not article:
            return Response({'error': 'Артикул обязателен'}, status=400)
        search_service = SmartSearchService()
        results = search_service.search_products(article, brand, search_analogs)
        return Response(results)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
# === View для главной страницы (cms/home.html) ===
def home_view(request):
    """Главная страница: передача популярных товаров и категорий в контекст"""
    from .models import Product, ProductCategory
    popular_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category', 'brand')[:12]
    categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    # Дополнительные объекты для CMS (баннеры, слайдеры, новости, html-блоки)
    context = {
        'popular_products': popular_products,
        'categories': categories,
        # ...другие объекты CMS, если нужны...
    }
    return render(request, 'cms/home.html', context)
from .forms import AdvancedSearchForm, QuickSearchForm
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from .models import (
    ProductCategory, Brand, Product, Cart, CartItem,
    Supplier, SupplierProduct, SupplierSyncLog,
    SupplierStaff, SupplierDeliveryMethod, SupplierOrderStatus,
    SupplierClientGroup, SupplierClient, SupplierOrder,
    SupplierOrderItem, SupplierOrderHistory, SupplierBalanceTransaction
)
from .serializers import (
    ProductCategorySerializer, BrandSerializer, ProductSerializer,
    CartSerializer, CartItemSerializer, SupplierSerializer,
    SupplierProductSerializer, SupplierSyncLogSerializer,
    SupplierAPITestSerializer, SupplierSyncSerializer,
    SupplierStaffSerializer, SupplierDeliveryMethodSerializer,
    SupplierOrderStatusSerializer, SupplierClientGroupSerializer,
    SupplierClientSerializer, SupplierOrderSerializer,
    SupplierOrderItemSerializer, SupplierOrderHistorySerializer,
    SupplierBalanceTransactionSerializer, SupplierEntitiesSyncSerializer,
    SupplierSearchSerializer, SupplierSearchResultSerializer
)


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для категорий товаров"""
    queryset = ProductCategory.objects.filter(is_active=True).order_by('order')
    serializer_class = ProductCategorySerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для брендов"""
    queryset = Brand.objects.filter(is_active=True).order_by('name')
    serializer_class = BrandSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для товаров"""
    queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
    serializer_class = ProductSerializer
    
    
    @action(detail=True, methods=['get'])
    def analogs(self, request, pk=None):
        """Получение аналогов товара"""
        product = self.get_object()
        analogs = Product.objects.filter(
            analogs__product=product,
            is_active=True
        )
        serializer = self.get_serializer(analogs, many=True)
        return Response(serializer.data)


class ProductSearchView(generics.ListAPIView):
    """Поиск товаров"""
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        import logging
        logging.warning("🔥🔥🔥 PRODUCTSEARCHVIEW ВЫЗВАН - API VIEW 🔥🔥🔥")
        
        query = self.request.query_params.get('q', '')
        if not query:
            return Product.objects.none()

        qs = Product.objects.filter(
            Q(name__icontains=query) |
            Q(article__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).select_related('category', 'brand')

        # Фильтрация по складам согласно WarehouseSettings
        from .models import WarehouseSettings
        from django.db.models import Q
        ws = WarehouseSettings.objects.first()
        if ws:
            allowed_warehouses = []
            if ws.show_spb_north:
                allowed_warehouses.append('СПб Север')
            if ws.show_spb_south:
                allowed_warehouses.append('СПб Юг')
            if ws.show_moscow:
                allowed_warehouses.append('Москва')
            if ws.show_other:
                qs = qs.filter(
                    Q(warehouse__in=allowed_warehouses) |
                    ~Q(warehouse__in=['СПб Север', 'СПб Юг', 'Москва']) |
                    Q(warehouse='')
                )
            else:
                qs = qs.filter(warehouse__in=allowed_warehouses) if allowed_warehouses else qs.none()

        return qs


class CartView(APIView):
    """Просмотр корзины"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    """Добавление товара в корзину"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response({'error': 'Не указан ID товара'}, status=400)
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({'message': 'Товар добавлен в корзину'})


class RemoveFromCartView(APIView):
    """Удаление товара из корзины"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)
        
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': 'Не указан ID товара'}, status=400)
        
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        
        return Response({'message': 'Товар удален из корзины'})


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet для поставщиков"""
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def test_api(self, request, pk=None):
        """Тестирование API соединения с поставщиком"""
        supplier = self.get_object()
        success, message = supplier.test_api_connection()
        
        serializer = SupplierAPITestSerializer(data={
            'success': success,
            'message': message
        })
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def sync_products(self, request, pk=None):
        """Синхронизация товаров с API поставщика"""
        supplier = self.get_object()
        success, message = supplier.sync_products()
        
        response_data = {'success': success, 'message': message}
        
        if success:
            # Получаем информацию из последнего лога
            last_log = supplier.sync_logs.first()
            if last_log:
                response_data.update({
                    'products_created': last_log.products_created,
                    'products_updated': last_log.products_updated,
                    'errors_count': last_log.errors_count
                })
        
        serializer = SupplierSyncSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Получение товаров поставщика"""
        supplier = self.get_object()
        products = supplier.products.all().order_by('-updated_at')
        
        # Пагинация
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = SupplierProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SupplierProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sync_logs(self, request, pk=None):
        """Получение логов синхронизации поставщика"""
        supplier = self.get_object()
        logs = supplier.sync_logs.all().order_by('-created_at')
        
        # Пагинация
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = SupplierSyncLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SupplierSyncLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def sync_entities(self, request, pk=None):
        """Синхронизация всех сущностей с API автозапчастей"""
        supplier = self.get_object()
        
        if supplier.api_type != 'autoparts':
            return Response({
                'success': False,
                'message': 'Метод доступен только для API автозапчастей'
            }, status=400)
        
        success, message = supplier.sync_all_entities()
        
        serializer = SupplierEntitiesSyncSerializer(data={
            'success': success,
            'message': message
        })
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def search_products(self, request, pk=None):
        """Поиск товаров по артикулу через API автозапчастей"""
        supplier = self.get_object()
        
        if supplier.api_type != 'autoparts':
            return Response({
                'success': False,
                'message': 'Метод доступен только для API автозапчастей'
            }, status=400)
        
        serializer = SupplierSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        article = serializer.validated_data['article']
        success, result = supplier.search_products_by_article(article)
        
        response_serializer = SupplierSearchResultSerializer(data={
            'success': success,
            'message': result.get('message', str(result)) if isinstance(result, dict) else str(result),
            'brands': result.get('brands', []) if isinstance(result, dict) else [],
            'products': result.get('products', []) if isinstance(result, dict) else []
        })
        response_serializer.is_valid(raise_exception=True)
        
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['get'])
    def staff(self, request, pk=None):
        """Получение сотрудников поставщика"""
        supplier = self.get_object()
        staff = supplier.staff.all().order_by('name')
        
        page = self.paginate_queryset(staff)
        if page is not None:
            serializer = SupplierStaffSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SupplierStaffSerializer(staff, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def clients(self, request, pk=None):
        """Получение клиентов поставщика"""
        supplier = self.get_object()
        clients = supplier.clients.all().select_related('group', 'manager').order_by('name')
        
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = SupplierClientSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SupplierClientSerializer(clients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Получение заказов поставщика"""
        supplier = self.get_object()
        orders = supplier.orders.all().select_related(
            'client', 'status', 'delivery_method'
        ).prefetch_related('items').order_by('-created_at')
        
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = SupplierOrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SupplierOrderSerializer(orders, many=True)
        return Response(serializer.data)


class SupplierProductViewSet(viewsets.ModelViewSet):
    """ViewSet для товаров поставщиков"""
    queryset = SupplierProduct.objects.all().select_related('supplier', 'product')
    serializer_class = SupplierProductSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по наличию товара в каталоге
        has_product = self.request.query_params.get('has_product', None)
        if has_product == 'true':
            queryset = queryset.filter(product__isnull=False)
        elif has_product == 'false':
            queryset = queryset.filter(product__isnull=True)
        
        # Фильтрация по активности
        is_active = self.request.query_params.get('is_active', None)
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-updated_at')
    
    @action(detail=True, methods=['post'])
    def create_product(self, request, pk=None):
        """Создание товара в каталоге на основе товара поставщика"""
        supplier_product = self.get_object()
        
        if supplier_product.product:
            return Response({
                'error': 'Товар уже существует в каталоге',
                'product_id': supplier_product.product.id
            }, status=400)
        
        try:
            category_id = request.data.get('category_id')
            brand_id = request.data.get('brand_id')
            
            category = None
            brand = None
            
            if category_id:
                try:
                    category = ProductCategory.objects.get(id=category_id)
                except ProductCategory.DoesNotExist:
                    return Response({'error': 'Категория не найдена'}, status=400)
            
            if brand_id:
                try:
                    brand = Brand.objects.get(id=brand_id)
                except Brand.DoesNotExist:
                    return Response({'error': 'Бренд не найден'}, status=400)
            
            product, created = supplier_product.create_catalog_product(category, brand)
            
            if created:
                return Response({
                    'success': True,
                    'message': f'Товар "{product.name}" успешно создан',
                    'product_id': product.id
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Товар уже существовал',
                    'product_id': product.id
                })
                
        except Exception as e:
            return Response({
                'error': f'Ошибка создания товара: {str(e)}'
            }, status=500)


class SupplierSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для логов синхронизации"""
    queryset = SupplierSyncLog.objects.all().select_related('supplier')
    serializer_class = SupplierSyncLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по статусу
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


# === VIEWSETS ДЛЯ ИНТЕГРАЦИИ С API АВТОЗАПЧАСТЕЙ ===

class SupplierStaffViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для сотрудников поставщика"""
    queryset = SupplierStaff.objects.all().select_related('supplier')
    serializer_class = SupplierStaffSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по активности
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class SupplierDeliveryMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для способов доставки поставщика"""
    queryset = SupplierDeliveryMethod.objects.all().select_related('supplier')
    serializer_class = SupplierDeliveryMethodSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по активности
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class SupplierOrderStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для статусов заказов поставщика"""
    queryset = SupplierOrderStatus.objects.all().select_related('supplier')
    serializer_class = SupplierOrderStatusSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        return queryset.order_by('name')


class SupplierClientGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для групп клиентов поставщика"""
    queryset = SupplierClientGroup.objects.all().select_related('supplier')
    serializer_class = SupplierClientGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        return queryset.order_by('name')


class SupplierClientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для клиентов поставщика"""
    queryset = SupplierClient.objects.all().select_related('supplier', 'group', 'manager')
    serializer_class = SupplierClientSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по группе
        group = self.request.query_params.get('group', None)
        if group:
            queryset = queryset.filter(group_id=group)
        
        # Фильтрация по менеджеру
        manager = self.request.query_params.get('manager', None)
        if manager:
            queryset = queryset.filter(manager_id=manager)
        
        # Фильтрация по активности
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class SupplierOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для заказов поставщика"""
    queryset = SupplierOrder.objects.all().select_related(
        'supplier', 'client', 'status', 'delivery_method'
    ).prefetch_related('items', 'history')
    serializer_class = SupplierOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по клиенту
        client = self.request.query_params.get('client', None)
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Фильтрация по статусу
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status_id=status_filter)
        
        return queryset.order_by('-created_at')


class SupplierBalanceTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для транзакций баланса"""
    queryset = SupplierBalanceTransaction.objects.all().select_related(
        'supplier', 'client', 'staff', 'order'
    )
    serializer_class = SupplierBalanceTransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по поставщику
        supplier = self.request.query_params.get('supplier', None)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        
        # Фильтрация по клиенту
        client = self.request.query_params.get('client', None)
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Фильтрация по типу транзакции
        transaction_type = self.request.query_params.get('transaction_type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset.order_by('-created_at')


class AdvancedSearchView(ListView):
    """Представление для расширенного поиска товаров"""
    model = Product
    template_name = 'catalog/advanced_search.html'
    context_object_name = 'products'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand', 'primary_supplier')
        
        form = AdvancedSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            search_type = form.cleaned_data.get('search_type')
            category = form.cleaned_data.get('category')
            brand = form.cleaned_data.get('brand')
            supplier = form.cleaned_data.get('supplier')
            price_min = form.cleaned_data.get('price_min')
            price_max = form.cleaned_data.get('price_max')
            in_stock_only = form.cleaned_data.get('in_stock_only')
            featured_only = form.cleaned_data.get('featured_only')
            order_by = form.cleaned_data.get('order_by')
            use_supplier_api = form.cleaned_data.get('use_supplier_api')
            
            # Поиск по тексту
            if query:
                if search_type == 'article':
                    queryset = queryset.filter(article__icontains=query)
                elif search_type == 'name':
                    queryset = queryset.filter(name__icontains=query)
                elif search_type == 'description':
                    queryset = queryset.filter(description__icontains=query)
                else:  # all
                    queryset = queryset.filter(
                        Q(article__icontains=query) |
                        Q(name__icontains=query) |
                        Q(description__icontains=query)
                    )
            
            # Фильтры
            if category:
                queryset = queryset.filter(category=category)
            
            if brand:
                queryset = queryset.filter(brand=brand)
            
            if supplier:
                queryset = queryset.filter(primary_supplier=supplier)
            
            if price_min:
                queryset = queryset.filter(price__gte=price_min)
            
            if price_max:
                queryset = queryset.filter(price__lte=price_max)
            
            if in_stock_only:
                queryset = queryset.filter(stock_quantity__gt=0)
            
            if featured_only:
                queryset = queryset.filter(is_featured=True)
            
            # Сортировка
            if order_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif order_by == 'price_desc':
                queryset = queryset.order_by('-price')
            elif order_by == 'relevance':
                queryset = queryset.order_by('-is_featured', '-created_at')
            else:
                queryset = queryset.order_by('-created_at')
            
            # Поиск через API поставщиков
            if use_supplier_api and query:
                self.api_results = self._search_via_suppliers_api(query, brand)
            else:
                self.api_results = []
        
        return queryset
    
    def _search_via_suppliers_api(self, query, brand=None):
        """Поиск через API поставщиков"""
        results = []
        active_suppliers = Supplier.objects.filter(is_active=True, api_type='autoparts')
        
        for supplier in active_suppliers:
            try:
                if brand:
                    success, data = supplier.search_products_by_article(query, brand.name)
                else:
                    success, data = supplier.search_products_by_article(query)
                
                if success and data:
                    results.append({
                        'supplier': supplier,
                        'products': data,
                        'count': len(data) if isinstance(data, list) else 1
                    })
            except Exception as e:
                # Логируем ошибку, но продолжаем поиск
                pass
        
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdvancedSearchForm(self.request.GET)
        context['api_results'] = getattr(self, 'api_results', [])
        
        # Статистика поиска
        context['total_local'] = context['products'].count() if hasattr(context['products'], 'count') else 0
        context['total_api'] = sum(result['count'] for result in context['api_results'])
        
        return context


def quick_search_view(request):
    """AJAX представление для быстрого поиска"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    # Поиск в локальной базе
    products = Product.objects.filter(
        Q(article__icontains=query) |
        Q(name__icontains=query),
        is_active=True
    ).select_related('category', 'brand')[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'article': product.article,
            'name': product.name,
            'brand': product.brand.name,
            'price': str(product.final_price),
            'url': product.get_absolute_url(),
            'in_stock': product.in_stock
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def supplier_api_search_view(request):
    """AJAX поиск через API поставщиков"""
    query = request.GET.get('q', '').strip()
    supplier_id = request.GET.get('supplier_id')
    
    if not query:
        return JsonResponse({'error': 'Запрос не может быть пустым'})
    
    results = []
    
    try:
        if supplier_id:
            # Поиск через конкретного поставщика
            supplier = get_object_or_404(Supplier, id=supplier_id, is_active=True)
            success, data = supplier.search_products_by_article(query)
            
            if success and data:
                results.append({
                    'supplier': supplier.name,
                    'products': data,
                    'status': 'success'
                })
            else:
                results.append({
                    'supplier': supplier.name,
                    'products': [],
                    'status': 'error',
                    'message': data
                })
        else:
            # Поиск через всех активных поставщиков
            suppliers = Supplier.objects.filter(is_active=True, api_type='autoparts')
            
            for supplier in suppliers:
                try:
                    success, data = supplier.search_products_by_article(query)
                    
                    results.append({
                        'supplier': supplier.name,
                        'products': data if success else [],
                        'status': 'success' if success else 'error',
                        'message': '' if success else data
                    })
                except Exception as e:
                    results.append({
                        'supplier': supplier.name,
                        'products': [],
                        'status': 'error',
                        'message': str(e)
                    })
    
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
    return JsonResponse({'results': results})


class ProductAnalogsView(APIView):
    """API для получения аналогов товара по артикулу"""
    permission_classes = [AllowAny]
    
    def get(self, request, article):
        """Поиск аналогов по артикулу"""
        brand = request.query_params.get('brand', None)
        limit = int(request.query_params.get('limit', 20))
        supplier_id = request.query_params.get('supplier_id', None)
        
        # Ограничиваем максимальное количество результатов
        limit = min(limit, 100)
        
        if not article:
            return Response({
                'success': False,
                'message': 'Артикул не указан'
            }, status=400)
        
        try:
            # Определяем поставщиков для поиска
            suppliers = Supplier.objects.filter(
                is_active=True,
                api_type='autoparts'
            )
            
            # Если указан конкретный поставщик
            if supplier_id:
                suppliers = suppliers.filter(id=supplier_id)
            
            if not suppliers.exists():
                return Response({
                    'success': False,
                    'message': 'Нет доступных поставщиков для поиска аналогов'
                }, status=404)
            
            all_analogs = []
            errors = []
            
            # Ищем аналоги у всех поставщиков
            for supplier in suppliers:
                try:
                    success, result = supplier.get_product_analogs(
                        article=article,
                        brand=brand,
                        limit=limit
                    )
                    
                    if success and result:
                        # result - это словарь с ключом 'analogs'
                        if isinstance(result, dict):
                            analogs = result.get('analogs', [])
                            
                            # Добавляем информацию о поставщике к каждому аналогу
                            for analog in analogs:
                                if isinstance(analog, dict):
                                    analog['supplier_id'] = supplier.id
                                    analog['supplier_name'] = supplier.name
                            
                            all_analogs.extend(analogs)
                        else:
                            errors.append(f"{supplier.name}: неожиданный формат ответа")
                    elif not success:
                        errors.append(f"{supplier.name}: {result}")
                        
                except Exception as e:
                    errors.append(f"{supplier.name}: {str(e)}")
            
            # Убираем дубликаты по артикулу + бренд
            unique_analogs = []
            seen = set()
            
            for analog in all_analogs:
                key = f"{analog.get('article', '')}-{analog.get('brand', '')}".lower()
                if key not in seen:
                    seen.add(key)
                    unique_analogs.append(analog)
            
            # Сортируем по доступности и цене
            unique_analogs.sort(key=lambda x: (
                -int(x['availability']) if str(x['availability']).lstrip('-').isdigit() else 0,
                float(x['price']) if x['price'] else float('inf')
            ))
            
            # Ограничиваем результат
            unique_analogs = unique_analogs[:limit]
            
            response_data = {
                'success': True,
                'original_article': article,
                'original_brand': brand,
                'analogs_count': len(unique_analogs),
                'analogs': unique_analogs,
                'suppliers_checked': len(suppliers),
                'errors': errors if errors else None
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Ошибка поиска аналогов: {str(e)}'
            }, status=500)
