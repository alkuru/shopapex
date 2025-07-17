from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Order, OrderItem, OrderStatusHistory, OrderStatus
from catalog.serializers import ProductSerializer


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total_price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    old_status_name = serializers.CharField(source='old_status.name', read_only=True)
    new_status_name = serializers.CharField(source='new_status.name', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'old_status', 'old_status_name', 'new_status', 'new_status_name', 
                 'changed_by', 'changed_by_name', 'comment', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка заказов - краткая информация"""
    customer_name = serializers.CharField(read_only=True)
    customer_phone = serializers.CharField(read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    items_count = serializers.SerializerMethodField()
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'customer_phone',
            'status', 'status_name', 'total_amount', 'created_at',
            'items_count', 'delivery_type', 'delivery_type_display',
            'payment_method', 'payment_method_display', 'is_paid'
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор заказа"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    delivery_type_display = serializers.CharField(source='get_delivery_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_name',
            'customer_name', 'customer_phone', 'customer_email',
            'delivery_type', 'delivery_type_display', 'delivery_address', 'delivery_cost',
            'payment_method', 'payment_method_display', 'is_paid',
            'total_amount', 'customer_comment', 'admin_comment',
            'created_at', 'updated_at', 'completed_at',
            'items', 'status_history'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заказа"""
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'user', 'customer_name', 'customer_phone', 'customer_email',
            'delivery_type', 'delivery_address', 'payment_method',
            'customer_comment', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Получаем статус по умолчанию
        default_status = OrderStatus.objects.filter(is_active=True).first()
        if not default_status:
            raise serializers.ValidationError("Нет активных статусов заказа")
        
        validated_data['status'] = default_status
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total_amount += item.total_price
        
        order.total_amount = total_amount
        order.save()
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления заказа"""
    
    class Meta:
        model = Order
        fields = [
            'status', 'customer_name', 'customer_phone', 'customer_email',
            'delivery_type', 'delivery_address', 'delivery_cost',
            'payment_method', 'is_paid', 'admin_comment'
        ]

    def update(self, instance, validated_data):
        # Если изменился статус, создаем запись в истории
        if 'status' in validated_data and validated_data['status'] != instance.status:
            OrderStatusHistory.objects.create(
                order=instance,
                old_status=instance.status,
                new_status=validated_data['status'],
                changed_by=self.context['request'].user,
                comment=f"Статус изменен с {instance.status.name} на {validated_data['status'].name}"
            )
        
        return super().update(instance, validated_data)
