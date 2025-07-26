from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, UserSession, UserAction, UserFavorite, UserGarage


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'company', 'created_at']
    list_filter = ['user_type', 'email_notifications', 'sms_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'user_type')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'birth_date', 'avatar')
        }),
        ('Работа', {
            'fields': ('company', 'position')
        }),
        ('Уведомления', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'session_key_short', 'created_at', 'last_activity']
    list_filter = ['created_at', 'last_activity']
    search_fields = ['user__username', 'ip_address', 'session_key']
    readonly_fields = ['created_at', 'last_activity']
    
    def session_key_short(self, obj):
        return obj.session_key[:10] + "..."
    session_key_short.short_description = "Ключ сессии"


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'action_type', 'description', 'ip_address', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['created_at']
    
    def user_display(self, obj):
        return obj.user.username if obj.user else 'Анонимный'
    user_display.short_description = "Пользователь"
    
    def has_add_permission(self, request):
        return False


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = ['user__username', 'product__name', 'product__article']
    readonly_fields = ['created_at']


@admin.register(UserGarage)
class UserGarageAdmin(admin.ModelAdmin):
    list_display = ['user', 'vin', 'comment_short', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'vin', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_short(self, obj):
        if obj.comment:
            return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
        return "—"
    comment_short.short_description = "Комментарий"
