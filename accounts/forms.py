from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class LoginForm(forms.Form):
    """Форма входа пользователя"""
    email_or_phone = forms.CharField(
        label='Телефон или эл. почта',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email или телефон'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class RegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    first_name = forms.CharField(
        label='Имя',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        })
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 123-45-67'
        })
    )
    address = forms.CharField(
        label='Адрес',
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Введите адрес доставки'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Простая валидация телефона
        phone_clean = ''.join(filter(str.isdigit, phone))
        if len(phone_clean) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Используем email как username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем профиль пользователя
            profile = user.userprofile
            profile.phone = self.cleaned_data['phone']
            profile.save()
            
        return user 