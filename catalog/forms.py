from django import forms
from django.contrib import admin
from .models import Supplier
from .widgets import SecurePasswordWidget


class SupplierAdminForm(forms.ModelForm):
    """
    Кастомная форма для модели Supplier в админке с улучшенным интерфейсом.
    """
    
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'api_password': SecurePasswordWidget(),
            'admin_password': SecurePasswordWidget(),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }
        help_texts = {
            'api_type': 'Выберите тип API для интеграции с поставщиком',
            'api_url': 'URL эндпоинта API поставщика (например, https://api.vinttop.ru/v1/)',
            'api_login': 'Логин для клиентского доступа к API (поиск товаров)',
            'api_password': 'Пароль для клиентского доступа к API (будет зашифрован)',
            'admin_login': 'Логин для административного доступа к API (управление заказами)',
            'admin_password': 'Пароль для административного доступа к API (будет зашифрован)',
            'price_markup': 'Наценка в процентах (например, 10.5 для 10.5%)',
            'is_active': 'Отметьте, если поставщик активен и доступен для синхронизации',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Настройка полей
        if 'api_type' in self.fields:
            self.fields['api_type'].widget.attrs.update({
                'class': 'form-select',
                'onchange': 'toggleAPIFields(this.value)'
            })
        
        if 'api_url' in self.fields:
            self.fields['api_url'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'https://api.example.com/v1/'
            })
        
        if 'api_login' in self.fields:
            self.fields['api_login'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Введите логин API...',
                'autocomplete': 'username'
            })
        
        if 'admin_login' in self.fields:
            self.fields['admin_login'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Введите логин API-администратора...',
                'autocomplete': 'username'
            })
        
        if 'price_markup' in self.fields:
            self.fields['price_markup'].widget.attrs.update({
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
    
    def clean_api_password(self):
        """
        Валидация пароля API.
        Если поле пустое при редактировании, сохраняем старый пароль.
        """
        password = self.cleaned_data.get('api_password')
        
        # Если это редактирование существующего объекта и пароль пустой,
        # сохраняем старый пароль
        if self.instance.pk and not password:
            return self.instance.api_password
        
        return password
    
    def clean_admin_password(self):
        """
        Валидация пароля API администратора.
        Если поле пустое при редактировании, сохраняем старый пароль.
        """
        password = self.cleaned_data.get('admin_password')
        
        # Если это редактирование существующего объекта и пароль пустой,
        # сохраняем старый пароль
        if self.instance.pk and not password:
            return self.instance.admin_password
        
        return password
    
    def clean(self):
        """
        Общая валидация формы.
        """
        cleaned_data = super().clean()
        api_type = cleaned_data.get('api_type')
        api_url = cleaned_data.get('api_url')
        api_login = cleaned_data.get('api_login')
        api_password = cleaned_data.get('api_password')
        
        # Если выбран тип API "autoparts", проверяем обязательные поля
        if api_type == 'autoparts':
            if not api_url:
                self.add_error('api_url', 'URL API обязателен для типа "autoparts"')
            
            if not api_login:
                self.add_error('api_login', 'Логин API обязателен для типа "autoparts"')
            
            if not api_password and not self.instance.pk:
                self.add_error('api_password', 'Пароль API обязателен для нового поставщика')
        
        return cleaned_data
    
    # class Media:
    #     css = {
    #         'all': ('admin/css/supplier_admin.css',)
    #     }
    #     js = ('admin/js/supplier_admin.js',)


class AdvancedSearchForm(forms.Form):
    """Расширенная форма поиска товаров"""
    
    SEARCH_TYPE_CHOICES = [
        ('article', 'По артикулу'),
        ('name', 'По названию'),
        ('description', 'По описанию'),
        ('oem', 'По OEM номеру'),
        ('all', 'По всем полям'),
    ]
    
    PRICE_ORDER_CHOICES = [
        ('', 'Без сортировки'),
        ('price_asc', 'По возрастанию цены'),
        ('price_desc', 'По убыванию цены'),
        ('relevance', 'По релевантности'),
    ]
    
    # Основные поля поиска
    query = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Введите артикул или название товара...',
            'autocomplete': 'off'
        }),
        label='Поисковый запрос'
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        initial='article',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Тип поиска'
    )
    
    # Фильтры
    category = forms.ModelChoiceField(
        queryset=None,  # Будет установлен в __init__
        required=False,
        empty_label='Все категории',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Категория'
    )
    
    brand = forms.ModelChoiceField(
        queryset=None,  # Будет установлен в __init__
        required=False,
        empty_label='Все бренды',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Бренд'
    )
    
    supplier = forms.ModelChoiceField(
        queryset=None,  # Будет установлен в __init__
        required=False,
        empty_label='Все поставщики',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Поставщик'
    )
    
    # Фильтры по цене
    price_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'От',
            'min': '0',
            'step': '0.01'
        }),
        label='Цена от'
    )
    
    price_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'До',
            'min': '0',
            'step': '0.01'
        }),
        label='Цена до'
    )
    
    # Дополнительные опции
    in_stock_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Только в наличии'
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Только популярные'
    )
    
    # Сортировка
    order_by = forms.ChoiceField(
        choices=PRICE_ORDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Сортировка'
    )
    
    # Поиск через API поставщиков
    use_supplier_api = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Искать через API поставщиков'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Импортируем здесь чтобы избежать циклических импортов
        from .models import ProductCategory, Brand, Supplier
        
        # Устанавливаем querysets для полей выбора
        self.fields['category'].queryset = ProductCategory.objects.filter(is_active=True)
        self.fields['brand'].queryset = Brand.objects.filter(is_active=True)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        price_min = cleaned_data.get('price_min')
        price_max = cleaned_data.get('price_max')
        
        # Проверяем логику цен
        if price_min and price_max and price_min > price_max:
            raise forms.ValidationError('Минимальная цена не может быть больше максимальной')
        
        return cleaned_data


class QuickSearchForm(forms.Form):
    """Быстрая форма поиска для хедера"""
    
    q = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск товаров...',
            'autocomplete': 'off'
        }),
        label=''
    )
