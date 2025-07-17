from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer, CustomerAddress, CustomerBalance, CustomerNote


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = '__all__'


class CustomerBalanceSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = CustomerBalance
        fields = ['id', 'transaction_type', 'transaction_type_display', 'amount', 'description', 'created_at', 'order']


class CustomerNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = CustomerNote
        fields = ['id', 'note', 'is_important', 'created_at', 'author', 'author_name']


class CustomerListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка клиентов - краткая информация"""
    full_name = serializers.CharField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'user_username', 'user_email', 'phone', 
            'preferred_delivery_type', 'manager_name', 'registration_date',
            'total_orders_count', 'total_spent', 'last_order_date'
        ]


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор клиента"""
    full_name = serializers.CharField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    balance_transactions = CustomerBalanceSerializer(many=True, read_only=True)
    notes = CustomerNoteSerializer(many=True, read_only=True)
    
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'user_first_name', 'user_last_name', 'user_email',
            'phone', 'preferred_delivery_type', 'manager', 'manager_name', 
            'delivery_address', 'admin_comment', 'registration_date', 
            'last_order_date', 'total_orders_count', 'total_spent',
            'email_notifications', 'sms_notifications',
            'addresses', 'balance_transactions', 'notes', 'current_balance'
        ]

    def get_current_balance(self, obj):
        deposits = sum(
            t.amount for t in obj.balance_transactions.filter(transaction_type__in=['deposit', 'bonus', 'refund'])
        )
        withdrawals = sum(
            t.amount for t in obj.balance_transactions.filter(transaction_type='withdrawal')
        )
        return deposits - withdrawals


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания клиента"""
    user_id = serializers.IntegerField(write_only=True)
    addresses = CustomerAddressSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'user_id', 'phone', 'preferred_delivery_type', 'manager',
            'delivery_address', 'admin_comment', 'email_notifications',
            'sms_notifications', 'addresses'
        ]

    def create(self, validated_data):
        addresses_data = validated_data.pop('addresses', [])
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        
        customer = Customer.objects.create(user=user, **validated_data)
        
        for address_data in addresses_data:
            CustomerAddress.objects.create(customer=customer, **address_data)
        
        return customer


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления клиента"""

    class Meta:
        model = Customer
        fields = [
            'phone', 'preferred_delivery_type', 'manager', 'delivery_address',
            'admin_comment', 'email_notifications', 'sms_notifications'
        ]


class CustomerStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики клиентов"""
    total_customers = serializers.IntegerField()
    active_customers = serializers.IntegerField()
    new_customers_this_month = serializers.IntegerField()
    customers_with_orders = serializers.IntegerField()
    top_customers = serializers.ListField()
    customers_by_month = serializers.ListField()
