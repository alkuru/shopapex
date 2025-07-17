from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from datetime import datetime, timedelta
from .models import (
    Banner, Slider, SliderItem, News, HTMLBlock, StoreSettings, HomePage, CatalogBlock
)
from .serializers import (
    BannerSerializer, SliderListSerializer, SliderDetailSerializer,
    SliderItemSerializer, NewsListSerializer, NewsDetailSerializer,
    HtmlBlockSerializer, StoreSettingsSerializer,
    HomePageDataSerializer, CMSStatsSerializer
)


class BannerViewSet(viewsets.ModelViewSet):
    """API для баннеров"""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['banner_type', 'is_active']
    ordering = ['order', '-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по текущей дате показа
        show_active = self.request.query_params.get('show_active')
        if show_active == 'true':
            now = datetime.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def for_banner_type(self, request):
        """Получение баннеров для определенного типа"""
        banner_type = request.query_params.get('banner_type')
        if not banner_type:
            return Response(
                {'error': 'Параметр banner_type обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = datetime.now()
        banners = self.get_queryset().filter(
            banner_type=banner_type,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('order')
        
        serializer = self.get_serializer(banners, many=True)
        return Response(serializer.data)


class SliderViewSet(viewsets.ModelViewSet):
    """API для слайдеров"""
    queryset = Slider.objects.all().prefetch_related('items')
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SliderListSerializer
        return SliderDetailSerializer


class SliderItemViewSet(viewsets.ModelViewSet):
    """API для элементов слайдера"""
    queryset = SliderItem.objects.all()
    serializer_class = SliderItemSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        slider_id = self.request.query_params.get('slider')
        if slider_id:
            queryset = queryset.filter(slider_id=slider_id)
        return queryset.order_by('sort_order')


class NewsViewSet(viewsets.ModelViewSet):
    """API для новостей"""
    queryset = News.objects.all()
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_published']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NewsListSerializer
        return NewsDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Для обычных пользователей показываем только опубликованные
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)
        
        # Поиск по заголовку и контенту
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Переопределяем для увеличения счетчика просмотров"""
        instance = self.get_object()
        
        # Увеличиваем счетчик просмотров
        instance.views_count = F('views_count') + 1
        instance.save(update_fields=['views_count'])
        
        # Обновляем объект для сериализации
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Получение последних новостей"""
        limit = int(request.query_params.get('limit', 5))
        news = self.get_queryset().filter(is_published=True)[:limit]
        serializer = NewsListSerializer(news, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Получение популярных новостей"""
        limit = int(request.query_params.get('limit', 5))
        news = self.get_queryset().filter(
            is_published=True
        ).order_by('-views_count')[:limit]
        serializer = NewsListSerializer(news, many=True)
        return Response(serializer.data)


class HtmlBlockViewSet(viewsets.ModelViewSet):
    """API для HTML блоков"""
    queryset = HTMLBlock.objects.all()
    serializer_class = HtmlBlockSerializer
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'is_active']
    ordering = ['position', 'order']
    
    @action(detail=False, methods=['get'])
    def for_position(self, request):
        """Получение HTML блоков для определенной позиции"""
        position = request.query_params.get('position')
        if not position:
            return Response(
                {'error': 'Параметр position обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blocks = self.get_queryset().filter(
            position=position,
            is_active=True
        ).order_by('order')
        
        serializer = self.get_serializer(blocks, many=True)
        return Response(serializer.data)


class StoreSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """API для настроек магазина"""
    queryset = StoreSettings.objects.all()
    serializer_class = StoreSettingsSerializer
    
    @action(detail=False, methods=['get'])
    def as_dict(self, request):
        """Получение настроек в виде словаря"""
        settings = {}
        for setting in self.get_queryset():
            if hasattr(setting, 'key') and hasattr(setting, 'value'):
                settings[setting.key] = setting.value
        return Response(settings)


class CMSApiView(viewsets.ViewSet):
    """Общее API для CMS данных"""
    
    @action(detail=False, methods=['get'])
    def homepage_data(self, request):
        """Получение всех данных для главной страницы"""
        now = datetime.now()
        
        # Активные баннеры
        banners = Banner.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
            banner_type='main'
        ).order_by('order')
        
        # Активные слайдеры
        sliders = Slider.objects.filter(
            is_active=True
        ).prefetch_related('items')
        
        # Последние новости
        latest_news = News.objects.filter(
            is_published=True
        ).order_by('-created_at')[:5]
        
        # HTML блоки для главной
        html_blocks = HTMLBlock.objects.filter(
            position='home_top',
            is_active=True
        ).order_by('order')
        
        # Настройки магазина
        store_settings = {}
        for setting in StoreSettings.objects.all():
            if hasattr(setting, 'key') and hasattr(setting, 'value'):
                store_settings[setting.key] = setting.value
        
        data = {
            'banners': BannerSerializer(banners, many=True).data,
            'sliders': SliderDetailSerializer(sliders, many=True).data,
            'latest_news': NewsListSerializer(latest_news, many=True).data,
            'html_blocks': HtmlBlockSerializer(html_blocks, many=True).data,
            'store_settings': store_settings,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика CMS"""
        # Статистика за последний месяц
        last_month = datetime.now() - timedelta(days=30)
        
        # Топ новости по просмотрам
        top_news = []
        for news in News.objects.filter(
            is_published=True
        ).order_by('-views_count')[:10]:
            top_news.append({
                'id': news.id,
                'title': news.title,
                'views_count': news.views_count
            })
        
        stats = {
            'total_news': News.objects.count(),
            'published_news': News.objects.filter(is_published=True).count(),
            'total_banners': Banner.objects.count(),
            'active_banners': Banner.objects.filter(is_active=True).count(),
            'total_sliders': Slider.objects.count(),
            'active_sliders': Slider.objects.filter(is_active=True).count(),
            'total_html_blocks': HTMLBlock.objects.count(),
            'active_html_blocks': HTMLBlock.objects.filter(is_active=True).count(),
            'recent_news': News.objects.filter(created_at__gte=last_month).count(),
            'top_news': top_news,
        }
        
        return Response(stats)


# Обычные представления для веб-интерфейса
def home(request):
    """Главная страница"""
    now = datetime.now()
    
    # Активные баннеры для главной страницы
    banners = Banner.objects.filter(
        is_active=True,
        banner_type='main',
        start_date__lte=now,
        end_date__gte=now
    ).order_by('order')
    
    # Активные слайдеры
    sliders = Slider.objects.filter(
        is_active=True
    ).prefetch_related('items')
    
    # Последние новости
    latest_news = News.objects.filter(
        is_published=True
    ).order_by('-created_at')[:5]
    
    # HTML блоки
    html_blocks = HTMLBlock.objects.filter(
        position='home_top',
        is_active=True
    ).order_by('order')
    
    # Популярные товары и категории для главной страницы
    from catalog.models import Product, ProductCategory
    popular_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category', 'brand')[:12]
    categories = ProductCategory.objects.filter(is_active=True).order_by('order')

    context = {
        'banners': banners,
        'sliders': sliders,
        'latest_news': latest_news,
        'html_blocks': html_blocks,
        'popular_products': popular_products,
        'categories': categories,
    }
    return render(request, 'cms/home.html', context)


def news_list(request):
    """Список новостей"""
    news = News.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'cms/news_list.html', {'news': news})


def news_detail(request, slug):
    """Детальная страница новости"""
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    # Увеличиваем счетчик просмотров
    news.views_count = F('views_count') + 1
    news.save(update_fields=['views_count'])
    news.refresh_from_db()
    
    # Похожие новости
    related_news = News.objects.filter(
        is_published=True
    ).exclude(id=news.id).order_by('-created_at')[:5]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    
    return render(request, 'cms/news_detail.html', context)
