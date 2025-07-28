
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import path
from django.http import JsonResponse
from django.contrib import messages
from django import forms
from django.core.files.uploadedfile import UploadedFile
import pandas as pd
from .models import (
    Brand, WarehouseSettings, ProductCategory, Product, ProductImage, 
    ProductAnalog, Cart, CartItem, AutoKontinentProduct
)
from .supplier_models import (
    Supplier, SupplierProduct, SupplierSyncLog, APIMonitorLog, APIHealthCheck,
    SupplierStaff, SupplierDeliveryMethod, SupplierOrderStatus, SupplierClientGroup,
    SupplierClient, SupplierOrder, SupplierOrderItem, SupplierOrderHistory, SupplierBalanceTransaction
)
from django.template.response import TemplateResponse
from django.core.cache import cache

# Форма для загрузки прайса
class PriceUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel файл прайса',
        help_text='Загрузите Excel файл с прайсом АвтоКонтинента (.xlsx, .xls)'
    )
    update_existing = forms.BooleanField(
        label='Обновить существующие товары',
        required=False,
        initial=True,
        help_text='Если отмечено, существующие товары будут обновлены'
    )
    clear_existing = forms.BooleanField(
        label='Очистить все существующие товары перед загрузкой',
        required=False,
        initial=False,
        help_text='ВНИМАНИЕ: Это удалит все существующие товары АвтоКонтинента!'
    )

# Форма для обновления брендов
class BrandUpdateForm(forms.Form):
    update_brands = forms.BooleanField(
        label='Обновить бренды',
        required=False,
        initial=True,
        help_text='Применить нормализацию брендов из brand_analysis_results.json'
    )
    manual_mappings = forms.BooleanField(
        label='Применить ручные маппинги',
        required=False,
        initial=True,
        help_text='Применить дополнительные маппинги (Victor Reinz → REINZ, MANN-FILTER → Mann и т.д.)'
    )


# Регистрация Brand
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating_display', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    list_filter = ['rating', 'is_active']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'logo', 'description', 'is_active')
        }),
        ('Рейтинг и контакты', {
            'fields': ('rating', 'website', 'online_catalog', 'country_iso')
        }),
    )
    
    def rating_display(self, obj):
        if obj.rating:
            stars = '★' * obj.rating + '☆' * (5 - obj.rating)
            rating_text = dict(Brand.RATING_CHOICES)[obj.rating]
            return format_html(
                '<span style="color: {}; font-size: 16px;" title="{}">{}</span>',
                self.get_rating_color(obj.rating),
                rating_text,
                stars
            )
        return "-"
    rating_display.short_description = "Рейтинг"
    
    def get_rating_color(self, rating):
        colors = {
            5: '#FFD700',  # Золотой для премиум
            4: '#FFA500',  # Оранжевый для хорошего
            3: '#FFC0CB',  # Розовый для среднего
            2: '#C0C0C0',  # Серебряный для низкого
            1: '#808080',  # Серый для плохого
        }
        return colors.get(rating, '#C0C0C0')



# Регистрация WarehouseSettings с корректными полями
@admin.register(WarehouseSettings)
class WarehouseSettingsAdmin(admin.ModelAdmin):
    list_display = ['show_spb_north', 'show_spb_south', 'show_moscow', 'show_other']
    
    fieldsets = (
        ('Настройки складов', {
            'fields': ('show_spb_north', 'show_spb_south', 'show_moscow', 'show_other'),
            'description': 'Выберите склады, которые должны отображаться в поиске товаров'
        }),
    )
    
    def has_add_permission(self, request):
        # Разрешаем создание только одной записи
        return not WarehouseSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False

# Регистрация Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('API настройки', {
            'fields': ('api_type', 'api_url', 'api_login', 'api_password', 'api_token', 'office_id'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('use_online_stocks', 'sync_frequency', 'contact_person', 'email', 'phone', 'website', 'default_shipment_address', 'admin_login', 'admin_password', 'data_format', 'markup_percentage', 'auto_activate_products'),
            'classes': ('collapse',)
        }),
    )

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


@admin.register(AutoKontinentProduct)
class AutoKontinentProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'brand', 'name', 'stock_spb_north', 'stock_spb', 'stock_msk', 'price', 'updated_at']
    list_filter = ['brand', 'updated_at']
    search_fields = ['article', 'brand', 'name']
    readonly_fields = ['updated_at']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-price/', self.admin_site.admin_view(self.upload_price_view), name='catalog_autokontinentproduct_upload_price'),
            path('upload-price-progress/', self.admin_site.admin_view(self.upload_price_progress_view), name='catalog_autokontinentproduct_upload_price_progress'),
            path('update-brands/', self.admin_site.admin_view(self.update_brands_view), name='catalog_autokontinentproduct_update_brands'),
            path('update-brands-progress/', self.admin_site.admin_view(self.update_brands_progress_view), name='catalog_autokontinentproduct_update_brands_progress'),
        ]
        return custom_urls + urls
    
    def update_brands_progress_view(self, request):
        """Возвращает текущий прогресс обновления брендов (0-100)"""
        progress = cache.get('update_brands_progress', 0)
        return JsonResponse({'progress': progress})

    def upload_price_progress_view(self, request):
        """Возвращает текущий прогресс загрузки прайса (0-100)"""
        # Проверяем, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        progress = cache.get('upload_price_progress', 0)
        return JsonResponse({'progress': progress})

    def upload_price_view(self, request):
        """Представление для загрузки прайса"""
        if request.method == 'POST':
            form = PriceUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    excel_file = form.cleaned_data['excel_file']
                    clear_existing = form.cleaned_data['clear_existing']
                    
                    if clear_existing:
                        deleted_count = AutoKontinentProduct.objects.count()
                        AutoKontinentProduct.objects.all().delete()
                        messages.success(request, f'Удалено {deleted_count} существующих товаров')
                    
                    # Читаем Excel файл
                    df = pd.read_excel(excel_file)
                    total_rows = len(df)
                    created_count = 0
                    updated_count = 0
                    
                    cache.set('upload_price_progress', 0)
                    
                    # Обрабатываем файл по строкам с оптимизацией
                    for index, row in df.iterrows():
                        try:
                            brand = str(row.get('Бренд', '')).strip()
                            article = str(row.get('Код товара', '')).strip()
                            name = str(row.get('Наименование товара', '')).strip()
                            stock_spb_north = int(row.get('Кол-во СЕВ_СПб', 0)) if pd.notna(row.get('Кол-во СЕВ_СПб')) else 0
                            stock_spb = int(row.get('Кол-во СПб', 0)) if pd.notna(row.get('Кол-во СПб')) else 0
                            stock_msk = int(row.get('Кол-во МСК', 0)) if pd.notna(row.get('Кол-во МСК')) else 0
                            price = float(row.get('Цена', 0)) if pd.notna(row.get('Цена')) else 0
                            multiplicity = int(row.get('Кратность', 1)) if pd.notna(row.get('Кратность')) else 1
                            unit = str(row.get('Ед. изм.', 'шт')).strip()
                            
                            if brand and article and name:
                                product, created = AutoKontinentProduct.objects.update_or_create(
                                    brand=brand,
                                    article=article,
                                    defaults={
                                        'name': name,
                                        'stock_spb_north': stock_spb_north,
                                        'stock_spb': stock_spb,
                                        'stock_msk': stock_msk,
                                        'price': price,
                                        'multiplicity': multiplicity,
                                        'unit': unit,
                                    }
                                )
                                if created:
                                    created_count += 1
                                else:
                                    updated_count += 1
                                    
                        except Exception as e:
                            messages.warning(request, f'Ошибка в строке {index + 2}: {str(e)}')
                            continue
                        
                        # Обновляем прогресс каждые 100 строк
                        if index % 100 == 0:
                            progress = int((index + 1) / total_rows * 100)
                            cache.set('upload_price_progress', progress)
                    
                    cache.set('upload_price_progress', 100)
                    messages.success(request, f'Импорт завершен! Создано: {created_count}, Обновлено: {updated_count}')
                    return redirect('admin:catalog_autokontinentproduct_changelist')
                    
                except Exception as e:
                    cache.set('upload_price_progress', 0)
                    messages.error(request, f'Ошибка при загрузке файла: {str(e)}')
        else:
            form = PriceUploadForm()
        context = {
            'title': 'Загрузка прайса АвтоКонтинента',
            'form': form,
            'opts': self.model._meta,
            'subtitle': '',
            'is_nav_sidebar_enabled': False,
            'is_popup': False,
            'has_permission': True,
            'site_url': '/admin/',
            'site_title': 'Администрирование Django',
            'site_header': 'Администрирование Django',
        }
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'admin/catalog/autokontinentproduct/upload_price.html', context)
    
    def update_brands_view(self, request):
        """Представление для обновления брендов"""
        if request.method == 'POST':
            form = BrandUpdateForm(request.POST)
            if form.is_valid():
                try:
                    update_brands = form.cleaned_data['update_brands']
                    manual_mappings = form.cleaned_data['manual_mappings']
                    updated_count = 0
                    cache.set('update_brands_progress', 0)
                    if update_brands:
                        import json
                        import os
                        from django.db.models import F
                        mapping_file = os.path.join(os.path.dirname(__file__), '..', 'brands_data', 'brand_analysis_results.json')
                        if os.path.exists(mapping_file):
                            with open(mapping_file, 'r', encoding='utf-8') as f:
                                brand_data = json.load(f)
                            def norm(s):
                                return str(s).strip().lower().replace(' ', '').replace('-', '').replace('/', '')
                            mapping = {norm(m['autokontinent']): m['autosputnik'] for m in brand_data.get('exact_matches', []) if m.get('autokontinent') and m.get('autosputnik')}
                            all_brands = list(AutoKontinentProduct.objects.values_list('brand', flat=True).distinct())
                            total = len(all_brands)
                            for idx, old_brand in enumerate(all_brands):
                                old_norm = norm(old_brand)
                                if old_norm in mapping:
                                    new_brand = mapping[old_norm]
                                    count = AutoKontinentProduct.objects.filter(brand__iexact=old_brand).update(brand=new_brand)
                                    updated_count += count
                                # Обновляем прогресс
                                cache.set('update_brands_progress', int((idx+1)/total*80))
                    if manual_mappings:
                        manual_mappings_dict = {
                            'Victor Reinz': 'REINZ',
                            'MANN-FILTER': 'Mann',
                            'Behr-Hella': 'BEHR',
                            'Autopartner': 'Autopa',
                        }
                        all_manual = list(manual_mappings_dict.items())
                        total_manual = len(all_manual)
                        for idx, (old_brand, new_brand) in enumerate(all_manual):
                            count = AutoKontinentProduct.objects.filter(brand__iexact=old_brand).update(brand=new_brand)
                            updated_count += count
                            cache.set('update_brands_progress', 80 + int((idx+1)/total_manual*20))
                    cache.set('update_brands_progress', 100)
                    messages.success(request, f'Обновлено {updated_count} записей брендов')
                    return redirect('admin:catalog_autokontinentproduct_changelist')
                except Exception as e:
                    cache.set('update_brands_progress', 0)
                    messages.error(request, f'Ошибка при обновлении брендов: {str(e)}')
        else:
            form = BrandUpdateForm()
        context = {
            'title': 'Обновление брендов',
            'form': form,
            'opts': self.model._meta,
            'subtitle': '',
            'is_nav_sidebar_enabled': False,
            'is_popup': False,
            'has_permission': True,
            'site_url': '/admin/',
            'site_title': 'Администрирование Django',
            'site_header': 'Администрирование Django',
        }
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'admin/catalog/autokontinentproduct/update_brands.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """Добавляем кнопку загрузки прайса"""
        extra_context = extra_context or {}
        extra_context['show_upload_button'] = True
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'article', 'name', 'stock_spb_north', 'stock_spb', 'stock_msk', 'price', 'multiplicity', 'unit')
        }),
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('article', 'brand', 'name')
        }),
        ('Остатки', {
            'fields': ('stock_spb', 'stock_msk')
        }),
        ('Цена и единицы', {
            'fields': ('price', 'multiplicity', 'unit')
        }),
        ('Дополнительно', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    # def has_add_permission(self, request):
    #     # Запрещаем добавление через админку (только через импорт)
    #     return False
