from django import forms
from django.utils.safestring import mark_safe


class SecurePasswordWidget(forms.PasswordInput):
    """
    Кастомный виджет для безопасного ввода пароля API в админке.
    Показывает звездочки вместо пароля и позволяет изменить пароль.
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'placeholder': 'Введите пароль API...',
            'autocomplete': 'new-password',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        if value:
            return '********'  # Показываем звездочки вместо реального пароля
        return value
    
    def render(self, name, value, attrs=None, renderer=None):
        # Основное поле для ввода пароля
        password_input = super().render(name, value, attrs, renderer)
        
        # Дополнительная информация и кнопка для показа/скрытия пароля
        extra_html = '''
        <div class="password-field-wrapper" style="margin-top: 5px;">
            <small class="form-text text-muted">
                Пароль будет зашифрован при сохранении. Оставьте поле пустым, чтобы не изменять существующий пароль.
            </small>
            <div class="mt-2">
                <button type="button" class="btn btn-sm btn-outline-secondary toggle-password" 
                        onclick="togglePasswordVisibility(this)" data-target="id_{name}">
                    <i class="fas fa-eye"></i> Показать пароль
                </button>
            </div>
        </div>
        <script>
        function togglePasswordVisibility(button) {{
            const targetId = button.getAttribute('data-target');
            const passwordField = document.getElementById(targetId);
            const icon = button.querySelector('i');
            
            if (passwordField.type === 'password') {{
                passwordField.type = 'text';
                icon.className = 'fas fa-eye-slash';
                button.innerHTML = '<i class="fas fa-eye-slash"></i> Скрыть пароль';
            }} else {{
                passwordField.type = 'password';
                icon.className = 'fas fa-eye';
                button.innerHTML = '<i class="fas fa-eye"></i> Показать пароль';
            }}
        }}
        </script>
        '''.format(name=name)
        
        return mark_safe(password_input + extra_html)


class APICredentialsWidget(forms.Widget):
    """
    Составной виджет для ввода логина и пароля API.
    """
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.widgets = {
            'login': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин API'}),
            'password': SecurePasswordWidget(attrs={'class': 'form-control'})
        }
    
    def format_value(self, value):
        if isinstance(value, dict):
            return value
        return {'login': '', 'password': ''}
    
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = {}
        
        login_value = value.get('login', '')
        password_value = value.get('password', '')
        
        html = f'''
        <div class="api-credentials-widget">
            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">Логин API:</label>
                    <input type="text" name="{name}_login" value="{login_value}" 
                           class="form-control" placeholder="Введите логин API...">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Пароль API:</label>
                    {self.widgets['password'].render(f'{name}_password', password_value)}
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(html)
    
    def value_from_datadict(self, data, files, name):
        return {
            'login': data.get(f'{name}_login', ''),
            'password': data.get(f'{name}_password', '')
        }