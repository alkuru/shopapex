from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import UserProfile, UserAction, UserFavorite, UserSession
from .serializers import (
    UserProfileSerializer, UserProfileUpdateSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserActionSerializer, UserFavoriteSerializer,
    UserSessionSerializer, ChangePasswordSerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    """API для работы с профилями пользователей"""
    queryset = UserProfile.objects.all().select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение профиля текущего пользователя"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Обновление профиля текущего пользователя"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        # Логируем действие
        UserAction.objects.create(
            user=user,
            action_type='login',
            description='Регистрация пользователя',
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Авторизация пользователя"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        
        # Создаем сессию
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key or '',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Логируем действие
        UserAction.objects.create(
            user=user,
            action_type='login',
            description='Вход в систему',
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'token': token.key
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Выход из системы"""
    # Удаляем токен
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    # Логируем действие
    UserAction.objects.create(
        user=request.user,
        action_type='logout',
        description='Выход из системы',
        ip_address=get_client_ip(request)
    )
    
    logout(request)
    return Response({'message': 'Успешный выход из системы'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Смена пароля"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Удаляем старый токен и создаем новый
        try:
            user.auth_token.delete()
        except:
            pass
        token = Token.objects.create(user=user)
        
        # Логируем действие
        UserAction.objects.create(
            user=user,
            action_type='login',
            description='Смена пароля',
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'message': 'Пароль успешно изменен',
            'token': token.key
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра действий пользователей"""
    queryset = UserAction.objects.all().select_related('user')
    serializer_class = UserActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action_type']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Обычные пользователи видят только свои действия
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=['get'])
    def my_actions(self, request):
        """Получение действий текущего пользователя"""
        actions = UserAction.objects.filter(user=request.user).order_by('-created_at')[:50]
        serializer = self.get_serializer(actions, many=True)
        return Response(serializer.data)


class UserFavoriteViewSet(viewsets.ModelViewSet):
    """API для работы с избранными товарами"""
    queryset = UserFavorite.objects.all().select_related('user', 'product')
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Добавить/удалить товар из избранного"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = UserFavorite.objects.get(user=request.user, product_id=product_id)
            favorite.delete()
            return Response({'message': 'Товар удален из избранного', 'action': 'removed'})
        except UserFavorite.DoesNotExist:
            UserFavorite.objects.create(user=request.user, product_id=product_id)
            return Response({'message': 'Товар добавлен в избранное', 'action': 'added'})


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра сессий пользователей"""
    queryset = UserSession.objects.all().select_related('user')
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-last_activity']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Обычные пользователи видят только свои сессии
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_action(user, action_type, description, request=None, additional_data=None):
    """Утилита для логирования действий пользователя"""
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    UserAction.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        additional_data=additional_data
    )
