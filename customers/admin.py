from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, CustomerAddress, CustomerBalance, CustomerNote


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 1


class CustomerBalanceInline(admin.TabularInline):
    model = CustomerBalance
    extra = 0
    readonly_fields = ['created_at']


class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'phone', 'preferred_delivery_type', 'manager', 
        'total_orders_count', 'total_spent', 'registration_date'
    ]
    list_filter = [
        'preferred_delivery_type', 'manager', 'registration_date', 
        'email_notifications', 'sms_notifications'
    ]
    search_fields = ['user__username', 'user__email', 'phone', 'user__first_name', 'user__last_name']
    readonly_fields = ['registration_date', 'last_order_date', 'total_orders_count', 'total_spent']
    inlines = [CustomerAddressInline, CustomerBalanceInline, CustomerNoteInline]
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'phone')
        }),
        ('Доставка', {
            'fields': ('preferred_delivery_type', 'delivery_address')
        }),
        ('Менеджмент', {
            'fields': ('manager', 'admin_comment')
        }),
        ('Статистика', {
            'fields': ('total_orders_count', 'total_spent', 'last_order_date'),
            'classes': ['collapse']
        }),
        ('Уведомления', {
            'fields': ('email_notifications', 'sms_notifications'),
            'classes': ['collapse']
        }),
        ('Даты', {
            'fields': ('registration_date',),
            'classes': ['collapse']
        }),
    )
    
    actions = ['update_order_stats']
    
    def update_order_stats(self, request, queryset):
        for customer in queryset:
            customer.update_order_stats()
        self.message_user(request, f"Статистика заказов обновлена для {queryset.count()} клиентов.")
    update_order_stats.short_description = "Обновить статистику заказов"


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'title', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default']
    search_fields = ['customer__user__username', 'title', 'address']


@admin.register(CustomerBalance)
class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ['customer', 'transaction_type', 'amount', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['customer__user__username', 'description']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer__user')


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'author', 'note_preview', 'is_important', 'created_at']
    list_filter = ['is_important', 'created_at', 'author']
    search_fields = ['customer__user__username', 'note']
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + "..." if len(obj.note) > 50 else obj.note
    note_preview.short_description = "Заметка"
