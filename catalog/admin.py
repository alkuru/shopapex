from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import path
from django.http import JsonResponse
from django.contrib import messages
from django import forms
from .models import (
    Brand, WarehouseSettings, ProductCategory, Product, ProductImage, 
    ProductAnalog, Cart, CartItem
)
from .supplier_models import (
    Supplier, SupplierProduct, SupplierSyncLog, APIMonitorLog, APIHealthCheck,
    SupplierStaff, SupplierDeliveryMethod, SupplierOrderStatus, SupplierClientGroup,
    SupplierClient, SupplierOrder, SupplierOrderItem, SupplierOrderHistory, SupplierBalanceTransaction
)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']

# Регистрация WarehouseSettings в админке
@admin.register(WarehouseSettings)
class WarehouseSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'show_spb_north', 'show_spb_south', 'show_moscow', 'show_other', 'is_active']
    search_fields = ['name']
    list_editable = ['show_spb_north', 'show_spb_south', 'show_moscow', 'show_other', 'is_active']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']

@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = [
        'article', 'name', 'supplier', 'price', 'availability', 
        'product_link', 'is_active', 'updated_at', 'action_buttons'
    ]
    list_filter = ['supplier', 'is_active', 'updated_at']
    search_fields = ['article', 'name', 'supplier__name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Информация от поставщика', {
            'fields': ('supplier', 'article', 'brand', 'name', 'price', 'availability')
        }),
        ('Связь с каталогом', {
            'fields': ('product', 'is_active')
        }),
    )
    
    readonly_fields = ['supplier', 'article', 'brand', 'updated_at', 'created_at']
    
    def product_link(self, obj):
        if obj.product:
            return format_html(
                '<a href="/admin/catalog/product/{}/change/">{}</a>',
                obj.product.pk, obj.product.article
            )
        return "-"
    product_link.short_description = "Товар в каталоге"
    
    def action_buttons(self, obj):
        buttons = []
        
        if not obj.product:
            buttons.append(
                f'<a href="/admin/catalog/supplierproduct/{obj.pk}/create-product/" '
                f'class="button">Создать товар</a>'
            )
        else:
            buttons.append(
                f'<a href="/admin/catalog/product/{obj.product.pk}/change/" '
                f'class="button">Редактировать товар</a>'
            )
        
        return format_html(''.join(buttons))
    action_buttons.short_description = "Действия"
    action_buttons.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:product_id>/create-product/', self.create_product_view, name='create_catalog_product'),
        ]
        return custom_urls + urls
    
    def create_product_view(self, request, product_id):
        try:
            supplier_product = SupplierProduct.objects.get(pk=product_id)
            
            if supplier_product.product:
                messages.warning(request, "Товар уже существует в каталоге")
            else:
                product, created = supplier_product.create_catalog_product()
                if created:
                    messages.success(request, f"Товар '{product.name}' успешно создан")
                else:
                    messages.info(request, "Товар уже существует")
                    
        except SupplierProduct.DoesNotExist:
            messages.error(request, "Товар поставщика не найден")
        except Exception as e:
            messages.error(request, f"Ошибка создания товара: {str(e)}")
        
        return redirect(f'/admin/catalog/supplierproduct/{product_id}/change/')


@admin.register(SupplierSyncLog)
class SupplierSyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'supplier', 'status', 'products_created', 'products_updated', 
        'errors_count', 'started_at', 'short_message'
    ]
    list_filter = ['status', 'supplier', 'started_at']
    search_fields = ['supplier__name', 'message']
    readonly_fields = ['supplier', 'status', 'message', 'products_created', 'products_updated', 'errors_count', 'started_at']
    
    def short_message(self, obj):
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message
    short_message.short_description = "Сообщение"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# === АДМИНКА ДЛЯ ИНТЕГРАЦИИ С API АВТОЗАПЧАСТЕЙ ===

@admin.register(SupplierStaff)
class SupplierStaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'role', 'email', 'phone', 'is_active', 'updated_at']
    list_filter = ['supplier', 'is_active', 'role']
    search_fields = ['name', 'email', 'phone', 'supplier__name']
    list_editable = ['is_active']
    readonly_fields = ['external_id', 'data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'external_id', 'name', 'email', 'phone', 'role', 'is_active')
        }),
        ('Дополнительно', {
            'fields': ('data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupplierDeliveryMethod)
class SupplierDeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'price', 'days_min', 'days_max', 'is_active', 'updated_at']
    list_filter = ['supplier', 'is_active']
    search_fields = ['name', 'description', 'supplier__name']
    list_editable = ['is_active', 'price']
    readonly_fields = ['external_id', 'data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'external_id', 'name', 'description', 'is_active')
        }),
        ('Параметры доставки', {
            'fields': ('price', 'days_min', 'days_max')
        }),
        ('Дополнительно', {
            'fields': ('data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupplierOrderStatus)
class SupplierOrderStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'color_badge', 'is_final', 'notify_client', 'is_active']
    list_filter = ['supplier', 'is_final', 'notify_client', 'is_active']
    search_fields = ['name', 'description', 'supplier__name']
    list_editable = ['is_final', 'notify_client', 'is_active']
    readonly_fields = ['external_id', 'data']
    
    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color, obj.name
        )
    color_badge.short_description = "Цвет"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'external_id', 'name', 'description')
        }),
        ('Настройки', {
            'fields': ('color', 'is_final', 'notify_client', 'is_active')
        }),
        ('Дополнительно', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupplierClientGroup)
class SupplierClientGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'discount_percentage', 'clients_count', 'is_active']
    list_filter = ['supplier', 'is_active']
    search_fields = ['name', 'description', 'supplier__name']
    readonly_fields = ['external_id', 'data', 'clients_count']
    
    def clients_count(self, obj):
        return obj.clients.count()
    clients_count.short_description = "Количество клиентов"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'external_id', 'name', 'description')
        }),
        ('Настройки', {
            'fields': ('discount_percentage', 'clients_count')
        }),
        ('Дополнительно', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupplierClient)
class SupplierClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'group', 'manager', 'balance', 'email', 'phone', 'is_active', 'updated_at']
    list_filter = ['supplier', 'group', 'manager', 'is_active']
    search_fields = ['name', 'email', 'phone', 'supplier__name']
    list_editable = ['is_active']
    readonly_fields = ['external_id', 'data', 'created_at', 'updated_at', 'orders_count', 'transactions_count']
    
    def orders_count(self, obj):
        return obj.orders.count()
    orders_count.short_description = "Количество заказов"
    
    def transactions_count(self, obj):
        return obj.balance_transactions.count()
    transactions_count.short_description = "Количество транзакций"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'external_id', 'name', 'email', 'phone', 'address', 'is_active')
        }),
        ('Связи', {
            'fields': ('group', 'manager')
        }),
        ('Финансы', {
            'fields': ('balance',)
        }),
        ('Статистика', {
            'fields': ('orders_count', 'transactions_count'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SupplierOrderItemInline(admin.TabularInline):
    model = SupplierOrderItem
    extra = 0
    readonly_fields = ['total']
    fields = ['product', 'article', 'name', 'brand', 'quantity', 'price', 'total']
    
    def total(self, obj):
        return obj.quantity * obj.price if obj.quantity and obj.price else 0
    total.short_description = "Сумма"


class SupplierOrderHistoryInline(admin.TabularInline):
    model = SupplierOrderHistory
    extra = 0
    readonly_fields = ['changed_at']
    fields = ['status', 'comment', 'changed_at']


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'supplier', 'client', 'status', 'total_amount', 'delivery_cost', 'updated_at']
    list_filter = ['supplier', 'status', 'delivery_method']
    search_fields = ['number', 'client__name', 'supplier__name', 'external_id']
    readonly_fields = ['external_id', 'data', 'created_at', 'updated_at', 'items_count']
    inlines = [SupplierOrderItemInline, SupplierOrderHistoryInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Количество позиций"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'external_id', 'number', 'client', 'status')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'delivery_cost')
        }),
        ('Финансы', {
            'fields': ('total_amount', 'items_count')
        }),
        ('Комментарии', {
            'fields': ('comment',)
        }),
        ('Дополнительно', {
            'fields': ('data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupplierOrderItem)
class SupplierOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'article', 'name', 'brand', 'quantity', 'price', 'total']
    list_filter = ['order__supplier', 'brand']
    search_fields = ['article', 'name', 'brand', 'order__number']
    readonly_fields = ['total']
    
    def total(self, obj):
        return obj.quantity * obj.price
    total.short_description = "Сумма"
    
    fieldsets = (
        ('Заказ', {
            'fields': ('order',)
        }),
        ('Товар', {
            'fields': ('product', 'article', 'name', 'brand')
        }),
        ('Количество и цены', {
            'fields': ('quantity', 'price', 'total')
        }),
    )


@admin.register(SupplierOrderHistory)
class SupplierOrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_at', 'short_comment']
    list_filter = ['order__supplier', 'status', 'changed_at']
    search_fields = ['order__number', 'comment', 'status__name']
    readonly_fields = ['changed_at']
    
    def short_comment(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = "Комментарий"
    
    fieldsets = (
        ('Заказ', {
            'fields': ('order', 'status')
        }),
        ('Комментарий', {
            'fields': ('comment',)
        }),
        ('Дополнительно', {
            'fields': ('changed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SupplierBalanceTransaction)
class SupplierBalanceTransactionAdmin(admin.ModelAdmin):
    list_display = ['client', 'transaction_type', 'amount', 'staff', 'order', 'created_at', 'short_comment']
    list_filter = ['supplier', 'transaction_type', 'staff', 'created_at']
    search_fields = ['client__name', 'comment', 'order__number']
    readonly_fields = ['created_at']
    
    def short_comment(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = "Комментарий"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('supplier', 'client', 'transaction_type', 'amount')
        }),
        ('Связи', {
            'fields': ('staff', 'order')
        }),
        ('Комментарий', {
            'fields': ('comment',)
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(APIMonitorLog)
class APIMonitorLogAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'method', 'status', 'response_time', 'checked_at']
    list_filter = ['status', 'method', 'checked_at', 'supplier']
    search_fields = ['supplier__name', 'method', 'error_message']
    readonly_fields = ['checked_at']
    date_hierarchy = 'checked_at'
    
    fieldsets = (
        (None, {
            'fields': ('supplier', 'method', 'status', 'response_time', 'checked_at')
        }),
        ('Данные запроса', {
            'fields': ('request_data',),
            'classes': ('collapse',)
        }),
        ('Данные ответа', {
            'fields': ('response_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Только для чтения


@admin.register(APIHealthCheck)
class APIHealthCheckAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'health_status', 'response_time', 'status_code', 'checked_at']
    list_filter = ['is_available', 'checked_at']
    search_fields = ['supplier__name']
    readonly_fields = ['checked_at']
    
    def health_status(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">🟢 Работает</span>')
        else:
            return format_html('<span style="color: red;">🔴 Не работает</span>')
    health_status.short_description = 'Статус'
    
    fieldsets = (
        (None, {
            'fields': ('supplier', 'is_available', 'checked_at')
        }),
        ('Статистика', {
            'fields': ('response_time', 'status_code')
        }),
        ('Ошибки', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )


