from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import OrderStatus, Order, OrderItem, OrderStatusHistory


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'send_sms', 'send_email', 'show_in_balance', 'is_active']
    list_filter = ['send_sms', 'send_email', 'show_in_balance', 'is_active']
    search_fields = ['name', 'action_description']
    list_editable = ['send_sms', 'send_email', 'show_in_balance', 'is_active']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = "Цвет"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'created_at']
    fields = ['old_status', 'new_status', 'changed_by', 'comment', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer_name', 'customer_phone', 'status_colored', 
        'total_amount', 'delivery_type', 'is_paid', 'created_at'
    ]
    list_filter = ['status', 'delivery_type', 'payment_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Контактная информация', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Доставка', {
            'fields': ('delivery_type', 'delivery_address', 'delivery_cost')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid')
        }),
        ('Комментарии', {
            'fields': ('customer_comment', 'admin_comment')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ['collapse']
        }),
    )
    
    def status_colored(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.status.color,
            obj.status.name
        )
    status_colored.short_description = "Статус"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'status')
    
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
        self.message_user(request, f"Заказы отмечены как оплаченные.")
    mark_as_paid.short_description = "Отметить как оплаченные"
    
    def mark_as_unpaid(self, request, queryset):
        queryset.update(is_paid=False)
        self.message_user(request, f"Заказы отмечены как неоплаченные.")
    mark_as_unpaid.short_description = "Отметить как неоплаченные"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__created_at', 'product__category']
    search_fields = ['order__order_number', 'product__name', 'product__article']
    readonly_fields = ['total_price']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['order__order_number', 'comment']
    readonly_fields = ['created_at']
