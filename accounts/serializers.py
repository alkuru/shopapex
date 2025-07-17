from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, UserAction, UserFavorite, UserSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user', 'user_type', 'phone', 'birth_date', 'avatar', 'avatar_url', 
            'email_notifications', 'sms_notifications', 'company', 'position', 
            'notes', 'created_at', 'updated_at'
        ]

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return obj.avatar.url
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""
    first_name = serializers.CharField(source='user.first_name', max_length=30)
    last_name = serializers.CharField(source='user.last_name', max_length=30)
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'birth_date', 
            'avatar', 'email_notifications', 'sms_notifications', 
            'company', 'position', 'notes'
        ]

    def update(self, instance, validated_data):
        # Обновляем данные пользователя
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            for field, value in user_data.items():
                setattr(user, field, value)
            user.save()

        # Обновляем данные профиля
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        phone = validated_data.pop('phone', '')
        
        user = User.objects.create_user(**validated_data)
        
        # Профиль создается автоматически через сигналы
        if phone and hasattr(user, 'userprofile'):
            user.userprofile.phone = phone
            user.userprofile.save()
            
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для авторизации пользователя"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Неверное имя пользователя или пароль')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт деактивирован')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Необходимо указать имя пользователя и пароль')


class UserActionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = UserAction
        fields = [
            'id', 'user', 'user_name', 'action_type', 'action_type_display',
            'description', 'ip_address', 'user_agent', 'additional_data', 'created_at'
        ]


class UserFavoriteSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = UserFavorite
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'created_at']

    def get_product_image(self, obj):
        if obj.product.image and hasattr(obj.product.image, 'url'):
            return obj.product.image.url
        return None


class UserSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserSession
        fields = ['id', 'user', 'user_name', 'session_key', 'ip_address', 'user_agent', 'created_at', 'last_activity']


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Новые пароли не совпадают")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный старый пароль")
        return value
