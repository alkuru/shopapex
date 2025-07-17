from rest_framework import serializers
from .models import VinCode, VinSearchRequest, VinRequestItem, VinRequestStatus
from catalog.serializers import ProductSerializer


class VinCodeSerializer(serializers.ModelSerializer):
    compatible_products = ProductSerializer(many=True, read_only=True)
    compatible_products_count = serializers.SerializerMethodField()

    class Meta:
        model = VinCode
        fields = [
            'id', 'vin_code', 'frame_number', 'brand', 'model', 'year',
            'engine', 'body_type', 'is_active', 'created_at',
            'compatible_products', 'compatible_products_count'
        ]

    def get_compatible_products_count(self, obj):
        return obj.compatible_products.count()


class VinCodeListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка VIN кодов"""
    compatible_products_count = serializers.SerializerMethodField()

    class Meta:
        model = VinCode
        fields = [
            'id', 'vin_code', 'frame_number', 'brand', 'model', 'year',
            'engine', 'body_type', 'is_active', 'created_at',
            'compatible_products_count'
        ]

    def get_compatible_products_count(self, obj):
        return obj.compatible_products.count()


class VinRequestItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = VinRequestItem
        fields = [
            'id', 'name', 'article', 'description', 'quantity',
            'estimated_price', 'found', 'product', 'product_id'
        ]


class VinSearchRequestListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка VIN запросов"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = VinSearchRequest
        fields = [
            'id', 'vin_code', 'frame_number', 'customer', 'customer_name',
            'customer_phone', 'status', 'status_display', 'created_at',
            'items_count'
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class VinSearchRequestDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор VIN запроса"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = VinRequestItemSerializer(many=True, read_only=True)
    found_vin = VinCodeSerializer(read_only=True)

    class Meta:
        model = VinSearchRequest
        fields = [
            'id', 'vin_code', 'frame_number', 'customer', 'customer_name',
            'customer_phone', 'customer_email', 'status', 'status_display',
            'notes', 'created_at', 'updated_at', 'items', 'found_vin'
        ]


class VinSearchRequestCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания VIN запроса"""
    items = VinRequestItemSerializer(many=True)

    class Meta:
        model = VinSearchRequest
        fields = [
            'vin_code', 'frame_number', 'customer', 'notes', 'items'
        ]

    def validate(self, data):
        # Проверяем, что указан хотя бы VIN код или номер рамы
        if not data.get('vin_code') and not data.get('frame_number'):
            raise serializers.ValidationError(
                "Необходимо указать VIN код или номер рамы"
            )
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = VinSearchRequest.objects.create(**validated_data)
        
        for item_data in items_data:
            VinRequestItem.objects.create(request=request, **item_data)
        
        return request


class VinSearchRequestUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления VIN запроса"""

    class Meta:
        model = VinSearchRequest
        fields = ['status', 'notes']

    def update(self, instance, validated_data):
        # Если изменился статус, создаем запись в истории
        if 'status' in validated_data and validated_data['status'] != instance.status:
            VinRequestStatus.objects.create(
                request=instance,
                status=validated_data['status'],
                changed_by=self.context['request'].user,
                comment=f"Статус изменен на {instance.get_status_display()}"
            )
        
        return super().update(instance, validated_data)


class VinRequestStatusSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = VinRequestStatus
        fields = ['id', 'status', 'changed_at', 'changed_by', 'changed_by_name', 'comment']


class VinSearchStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики VIN поиска"""
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    processed_requests = serializers.IntegerField()
    total_vin_codes = serializers.IntegerField()
    recent_requests = serializers.IntegerField()
    success_rate = serializers.FloatField()
    top_brands = serializers.ListField()
    requests_by_month = serializers.ListField()
