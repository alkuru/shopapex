from rest_framework import serializers
from .models import (
    Banner, Slider, SliderItem, News, HTMLBlock, 
    StoreSettings, HomePage, CatalogBlock
)


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

    def validate(self, data):
        # Проверяем даты показа
        if data.get('show_from') and data.get('show_to'):
            if data['show_from'] >= data['show_to']:
                raise serializers.ValidationError(
                    "Дата начала показа должна быть раньше даты окончания"
                )
        return data


class SliderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderItem
        fields = '__all__'


class SliderListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка слайдеров"""
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Slider
        fields = ['id', 'title', 'is_active', 'autoplay', 'items_count']

    def get_items_count(self, obj):
        return obj.items.count()


class SliderDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор слайдера"""
    items = SliderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Slider
        fields = '__all__'


class NewsListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка новостей"""
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'excerpt', 'image', 'is_published',
            'created_at', 'updated_at', 'views_count'
        ]

    def get_excerpt(self, obj):
        # Возвращаем первые 200 символов контента
        if obj.content:
            return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content
        return ''


class NewsDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор новости"""
    previous_news = serializers.SerializerMethodField()
    next_news = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = '__all__'

    def get_previous_news(self, obj):
        previous = News.objects.filter(
            created_at__lt=obj.created_at,
            is_published=True
        ).order_by('-created_at').first()
        
        if previous:
            return {
                'id': previous.id,
                'title': previous.title,
                'slug': previous.slug
            }
        return None

    def get_next_news(self, obj):
        next_news = News.objects.filter(
            created_at__gt=obj.created_at,
            is_published=True
        ).order_by('created_at').first()
        
        if next_news:
            return {
                'id': next_news.id,
                'title': next_news.title,
                'slug': next_news.slug
            }
        return None


class HtmlBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HTMLBlock
        fields = '__all__'


class StoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = '__all__'


class HomePageDataSerializer(serializers.Serializer):
    """Сериализатор для данных главной страницы"""
    banners = BannerSerializer(many=True)
    sliders = SliderDetailSerializer(many=True)
    latest_news = NewsListSerializer(many=True)
    html_blocks = HtmlBlockSerializer(many=True)
    store_settings = serializers.DictField()


class CMSStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики CMS"""
    total_news = serializers.IntegerField()
    published_news = serializers.IntegerField()
    total_banners = serializers.IntegerField()
    active_banners = serializers.IntegerField()
    total_sliders = serializers.IntegerField()
    active_sliders = serializers.IntegerField()
    total_html_blocks = serializers.IntegerField()
    active_html_blocks = serializers.IntegerField()
    recent_news = serializers.IntegerField()
    top_news = serializers.ListField()
