from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, OrderDocument, OrderHistory


class OrderItemInline(admin.TabularInline):
    """Inline для товаров в заказе"""
    model = OrderItem
    extra = 0
    readonly_fields = ['cost']
    fields = ['manufacturer', 'article', 'name', 'price', 'quantity', 'cost', 'item_status', 'item_comment']


class OrderDocumentInline(admin.TabularInline):
    """Inline для документов заказа"""
    model = OrderDocument
    extra = 0
    fields = ['document_type', 'file', 'uploaded_at']


class OrderHistoryInline(admin.TabularInline):
    """Inline для истории заказа"""
    model = OrderHistory
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    fields = ['status_from', 'status_to', 'comment', 'created_at', 'created_by']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""
    list_display = [
        'order_number', 'user', 'status_display', 'total', 'items_count', 
        'payment_status', 'delivery_method', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'delivery_method', 'payment_method', 
        'created_at', 'delivered_at'
    ]
    search_fields = [
        'order_number', 'user__username', 'user__email', 
        'delivery_address', 'user_comment'
    ]
    readonly_fields = [
        'id', 'order_number', 'created_at', 'updated_at', 
        'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'order_number', 'user', 'status')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'delivery_address', 'delivery_company', 'delivery_cost')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Стоимость', {
            'fields': ('subtotal', 'discount', 'total')
        }),
        ('Комментарии', {
            'fields': ('user_comment', 'admin_comment'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline, OrderDocumentInline, OrderHistoryInline]
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def status_display(self, obj):
        """Отображение статуса с цветом"""
        status_colors = {
            'pending': '#ffc107',      # Жёлтый
            'confirmed': '#17a2b8',    # Голубой
            'in_progress': '#007bff',  # Синий
            'shipped': '#6f42c1',      # Фиолетовый
            'delivered': '#28a745',    # Зелёный
            'cancelled': '#dc3545',    # Красный
            'returned': '#fd7e14',     # Оранжевый
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.status_display
        )
    status_display.short_description = 'Статус'
    
    def items_count(self, obj):
        """Количество товаров"""
        return obj.items_count
    items_count.short_description = 'Товаров'
    
    def mark_as_confirmed(self, request, queryset):
        """Отметить как подтверждённые"""
        from django.utils import timezone
        updated = queryset.update(
            status='confirmed', 
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'Подтверждено {updated} заказов.')
    mark_as_confirmed.short_description = 'Отметить как подтверждённые'
    
    def mark_as_shipped(self, request, queryset):
        """Отметить как отправленные"""
        from django.utils import timezone
        updated = queryset.update(
            status='shipped', 
            shipped_at=timezone.now()
        )
        self.message_user(request, f'Отправлено {updated} заказов.')
    mark_as_shipped.short_description = 'Отметить как отправленные'
    
    def mark_as_delivered(self, request, queryset):
        """Отметить как доставленные"""
        from django.utils import timezone
        updated = queryset.update(
            status='delivered', 
            delivered_at=timezone.now()
        )
        self.message_user(request, f'Доставлено {updated} заказов.')
    mark_as_delivered.short_description = 'Отметить как доставленные'
    
    def mark_as_cancelled(self, request, queryset):
        """Отметить как отменённые"""
        from django.utils import timezone
        updated = queryset.update(
            status='cancelled', 
            cancelled_at=timezone.now()
        )
        self.message_user(request, f'Отменено {updated} заказов.')
    mark_as_cancelled.short_description = 'Отметить как отменённые'
    
    def save_model(self, request, obj, form, change):
        """Сохранение модели с записью в историю"""
        if change:  # Если это изменение существующего заказа
            old_obj = Order.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                OrderHistory.objects.create(
                    order=obj,
                    status_from=old_obj.status,
                    status_to=obj.status,
                    created_by=request.user
                )
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для товаров в заказах"""
    list_display = ['order', 'manufacturer', 'article', 'name', 'quantity', 'price', 'cost', 'item_status']
    list_filter = ['item_status', 'manufacturer']
    search_fields = ['order__order_number', 'manufacturer', 'article', 'name']
    readonly_fields = ['cost']
    
    fieldsets = (
        ('Заказ', {
            'fields': ('order',)
        }),
        ('Товар', {
            'fields': ('manufacturer', 'article', 'name')
        }),
        ('Цена и количество', {
            'fields': ('price', 'quantity', 'cost')
        }),
        ('Статус', {
            'fields': ('item_status', 'item_comment')
        }),
        ('Дополнительно', {
            'fields': ('supplier', 'warehouse'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderDocument)
class OrderDocumentAdmin(admin.ModelAdmin):
    """Админка для документов заказов"""
    list_display = ['order', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['order__order_number', 'document_type']
    readonly_fields = ['uploaded_at']


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    """Админка для истории заказов"""
    list_display = ['order', 'status_from', 'status_to', 'created_by', 'created_at']
    list_filter = ['status_to', 'created_at']
    search_fields = ['order__order_number', 'comment']
    readonly_fields = ['created_at', 'created_by']
    ordering = ['-created_at']
