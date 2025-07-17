from django.contrib import admin
from django.utils.html import format_html
from .models import (
    StoreSettings, HomePage, Banner, HTMLBlock, 
    Slider, SliderItem, News, CatalogBlock
)


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основная информация', {
            'fields': ('store_name', 'slogan')
        }),
        ('SEO настройки', {
            'fields': ('meta_keywords', 'meta_description')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Социальные сети', {
            'fields': ('vk_group', 'telegram_group')
        }),
        ('Футер', {
            'fields': ('footer_copyright',)
        }),
    )
    
    def has_add_permission(self, request):
        # Разрешаем добавление только если нет записей
        return not StoreSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_active', 'order']
    ordering = ['order']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_type', 'is_active', 'is_active_now', 'start_date', 'end_date']
    list_filter = ['banner_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'text']
    list_editable = ['is_active']
    
    def is_active_now(self, obj):
        if obj.is_active_now:
            return format_html('<span style="color: green;">✓ Активен</span>')
        else:
            return format_html('<span style="color: red;">✗ Неактивен</span>')
    is_active_now.short_description = "Активен сейчас"


@admin.register(HTMLBlock)
class HTMLBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'order']
    list_filter = ['position', 'is_active']
    search_fields = ['title', 'html_content']
    list_editable = ['is_active', 'order']


class SliderItemInline(admin.TabularInline):
    model = SliderItem
    extra = 1


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'autoplay', 'autoplay_speed', 'loop']
    list_filter = ['is_active', 'autoplay', 'loop']
    search_fields = ['title']
    list_editable = ['is_active']
    inlines = [SliderItemInline]


@admin.register(SliderItem)
class SliderItemAdmin(admin.ModelAdmin):
    list_display = ['slider', 'title', 'is_active', 'order', 'image_preview']
    list_filter = ['slider', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: cover;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = "Превью"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'published_at', 'created_at']
    list_filter = ['is_published', 'author', 'published_at', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content', 'image')
        }),
        ('Публикация', {
            'fields': ('author', 'is_published', 'published_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(CatalogBlock)
class CatalogBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'show_products']
    list_filter = ['is_active', 'show_products']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    filter_horizontal = ['categories']
