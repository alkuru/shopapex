from django.contrib import admin
from django.utils.html import format_html
from .models import VinRequest, VehicleInfo, VinSearchResult, VinDatabase


class VehicleInfoInline(admin.StackedInline):
    model = VehicleInfo
    extra = 0


class VinSearchResultInline(admin.TabularInline):
    model = VinSearchResult
    extra = 1


@admin.register(VinRequest)
class VinRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_number', 'request_type', 'vin_code', 'frame_number', 
        'customer_name', 'status_colored', 'created_at'
    ]
    list_filter = ['request_type', 'status', 'created_at', 'processed_at']
    search_fields = ['request_number', 'vin_code', 'frame_number', 'customer_name', 'customer_phone']
    readonly_fields = ['request_number', 'created_at']
    inlines = [VehicleInfoInline, VinSearchResultInline]
    
    fieldsets = (
        ('Информация о запросе', {
            'fields': ('request_number', 'request_type', 'vin_code', 'frame_number')
        }),
        ('Клиент', {
            'fields': ('customer', 'customer_name', 'customer_phone', 'customer_email')
        }),
        ('Обработка', {
            'fields': ('status', 'processed_by', 'admin_comment', 'processed_at')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ['collapse']
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'new': '#ff9800',
            'processing': '#2196f3',
            'completed': '#4caf50',
            'cancelled': '#f44336'
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = "Статус"
    
    actions = ['mark_as_processing', 'mark_as_completed']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"Запросы отмечены как обрабатываемые.")
    mark_as_processing.short_description = "Отметить как обрабатываемые"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"Запросы отмечены как завершенные.")
    mark_as_completed.short_description = "Отметить как завершенные"


@admin.register(VehicleInfo)
class VehicleInfoAdmin(admin.ModelAdmin):
    list_display = ['vin_request', 'make', 'model', 'year', 'engine_type']
    list_filter = ['make', 'year', 'body_type', 'drive_type']
    search_fields = ['make', 'model', 'vin_request__vin_code']


@admin.register(VinSearchResult)
class VinSearchResultAdmin(admin.ModelAdmin):
    list_display = ['vin_request', 'product', 'is_recommended', 'created_at']
    list_filter = ['is_recommended', 'created_at', 'product__category']
    search_fields = ['vin_request__request_number', 'product__name', 'product__article']


@admin.register(VinDatabase)
class VinDatabaseAdmin(admin.ModelAdmin):
    list_display = ['vin_pattern', 'make', 'model', 'year_from', 'year_to', 'is_active']
    list_filter = ['make', 'is_active', 'year_from']
    search_fields = ['vin_pattern', 'make', 'model']
    filter_horizontal = ['products']
    
    fieldsets = (
        ('VIN информация', {
            'fields': ('vin_pattern', 'make', 'model')
        }),
        ('Годы выпуска', {
            'fields': ('year_from', 'year_to')
        }),
        ('Технические характеристики', {
            'fields': ('engine_type',)
        }),
        ('Товары', {
            'fields': ('products',)
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
    )
