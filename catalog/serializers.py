from rest_framework import serializers
from .models import (
    ProductCategory, Brand, Product, ProductImage, 
    ProductAnalog, Cart, CartItem, Supplier, 
    SupplierProduct, SupplierSyncLog,
    SupplierStaff, SupplierDeliveryMethod, SupplierOrderStatus,
    SupplierClientGroup, SupplierClient, SupplierOrder,
    SupplierOrderItem, SupplierOrderHistory, SupplierBalanceTransaction
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'image', 'order']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo', 'description', 'website']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'order']


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'article', 'category', 'brand', 'description',
            'price', 'discount_price', 'final_price', 'stock_quantity',
            'in_stock', 'is_featured', 'images', 'created_at',
            'delivery_time', 'warehouse'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount', 'total_items', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    last_sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'description', 'contact_person', 'email', 'phone', 'website',
            'api_url', 'data_format', 'sync_frequency', 'markup_percentage', 
            'auto_activate_products', 'is_active', 'created_at', 'updated_at', 
            'last_sync_at', 'products_count', 'last_sync_status'
        ]
        read_only_fields = ['last_sync_at']
    
    def get_products_count(self, obj):
        return obj.products.count()
    
    def get_last_sync_status(self, obj):
        last_log = obj.sync_logs.first()
        return last_log.status if last_log else None


class SupplierProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    product_article = serializers.CharField(source='product.article', read_only=True)
    
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'supplier', 'supplier_name', 'supplier_article', 'name', 
            'price', 'stock_quantity', 'product', 'product_article', 
            'is_active', 'created_at', 'updated_at', 'data'
        ]


class SupplierSyncLogSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierSyncLog
        fields = [
            'id', 'supplier', 'supplier_name', 'status', 'message',
            'products_created', 'products_updated', 'errors_count', 'created_at'
        ]


class SupplierAPITestSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class SupplierSyncSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    products_created = serializers.IntegerField(required=False)
    products_updated = serializers.IntegerField(required=False)
    errors_count = serializers.IntegerField(required=False)


# === СЕРИАЛИЗАТОРЫ ДЛЯ ИНТЕГРАЦИИ С API АВТОЗАПЧАСТЕЙ ===

class SupplierStaffSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierStaff
        fields = [
            'id', 'supplier', 'supplier_name', 'external_id', 'name', 
            'email', 'phone', 'role', 'is_active', 'created_at', 'updated_at'
        ]


class SupplierDeliveryMethodSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierDeliveryMethod
        fields = [
            'id', 'supplier', 'supplier_name', 'external_id', 'name', 
            'description', 'price', 'days_min', 'days_max', 'is_active',
            'created_at', 'updated_at'
        ]


class SupplierOrderStatusSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierOrderStatus
        fields = [
            'id', 'supplier', 'supplier_name', 'external_id', 'name', 
            'description', 'color', 'is_final', 'notify_client',
            'created_at', 'updated_at'
        ]


class SupplierClientGroupSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    clients_count = serializers.IntegerField(source='clients.count', read_only=True)
    
    class Meta:
        model = SupplierClientGroup
        fields = [
            'id', 'supplier', 'supplier_name', 'external_id', 'name', 
            'description', 'discount_percentage', 'clients_count',
            'created_at', 'updated_at'
        ]


class SupplierClientSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True)
    orders_count = serializers.IntegerField(source='orders.count', read_only=True)
    transactions_count = serializers.IntegerField(source='balance_transactions.count', read_only=True)
    
    class Meta:
        model = SupplierClient
        fields = [
            'id', 'supplier', 'supplier_name', 'external_id', 'name', 
            'email', 'phone', 'address', 'group', 'group_name',
            'manager', 'manager_name', 'balance', 'is_active',
            'orders_count', 'transactions_count', 'created_at', 'updated_at'
        ]


class SupplierOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SupplierOrderItem
        fields = [
            'id', 'product', 'product_name', 'article', 'name', 
            'brand', 'quantity', 'price', 'total'
        ]


class SupplierOrderHistorySerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    
    class Meta:
        model = SupplierOrderHistory
        fields = [
            'id', 'status', 'status_name', 'staff', 'staff_name',
            'comment', 'created_at'
        ]


class SupplierOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    delivery_method_name = serializers.CharField(source='delivery_method.name', read_only=True)
    items = SupplierOrderItemSerializer(many=True, read_only=True)
    history = SupplierOrderHistorySerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = SupplierOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'external_id', 'number',
            'client', 'client_name', 'status', 'status_name',
            'delivery_method', 'delivery_method_name', 'total_amount',
            'delivery_cost', 'comment', 'items_count', 'items', 'history',
            'created_at', 'updated_at'
        ]


class SupplierBalanceTransactionSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    staff_name = serializers.CharField(source='staff.name', read_only=True)
    order_number = serializers.CharField(source='order.number', read_only=True)
    
    class Meta:
        model = SupplierBalanceTransaction
        fields = [
            'id', 'supplier', 'supplier_name', 'client', 'client_name',
            'transaction_type', 'amount', 'description', 'staff', 'staff_name',
            'order', 'order_number', 'created_at'
        ]


# === СЕРИАЛИЗАТОРЫ ДЛЯ API ОПЕРАЦИЙ ===

class SupplierEntitiesSyncSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class SupplierSearchSerializer(serializers.Serializer):
    article = serializers.CharField(max_length=100)
    brand = serializers.CharField(max_length=100, required=False)


class SupplierSearchResultSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    brands = serializers.ListField(required=False)
    products = serializers.ListField(required=False)
