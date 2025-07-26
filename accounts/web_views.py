from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .forms import LoginForm, RegistrationForm
from .models import UserAction, UserProfile, UserGarage


def login_page(request):
    """Страница входа пользователя"""
    if request.user.is_authenticated:
        return redirect('catalog_web:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            password = form.cleaned_data['password']

            # Пытаемся найти пользователя по email или телефону
            from django.contrib.auth.models import User
            try:
                # Сначала пробуем по email
                user = User.objects.get(email=email_or_phone)
            except User.DoesNotExist:
                # Если не найден по email, пробуем по телефону
                try:
                    profile = UserProfile.objects.get(phone=email_or_phone)
                    user = profile.user
                except UserProfile.DoesNotExist:
                    user = None

            if user and user.check_password(password):
                login(request, user)

                # Логируем действие
                UserAction.objects.create(
                    user=user,
                    action_type='login',
                    description='Вход в систему через веб-интерфейс',
                    ip_address=get_client_ip(request)
                )

                # Перенаправляем на главную страницу или на страницу, с которой пришел пользователь
                next_url = request.GET.get('next', 'catalog_web:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email/телефон или пароль.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'page_title': 'Войти'
    })


def register_page(request):
    """Страница регистрации пользователя"""
    if request.user.is_authenticated:
        return redirect('catalog_web:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Логируем действие
            UserAction.objects.create(
                user=user,
                action_type='register',
                description='Регистрация нового пользователя',
                ip_address=get_client_ip(request)
            )

            messages.success(request, f'Добро пожаловать, {user.first_name}! Регистрация прошла успешно.')
            return redirect('catalog_web:home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'page_title': 'Регистрация'
    })


@login_required
def logout_page(request):
    """Выход пользователя"""
    # Логируем действие
    UserAction.objects.create(
        user=request.user,
        action_type='logout',
        description='Выход из системы',
        ip_address=get_client_ip(request)
    )

    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('catalog_web:home')


@login_required
def profile_page(request):
    """Страница профиля пользователя"""
    return render(request, 'accounts/profile.html', {
        'page_title': 'Мой профиль'
    })


@login_required
def garage_page(request):
    """Страница гаража пользователя"""
    garage_vehicles = UserGarage.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'accounts/garage.html', {
        'page_title': 'Мой гараж',
        'garage_vehicles': garage_vehicles
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_vehicle_to_garage(request):
    """API для добавления автомобиля в гараж"""
    try:
        data = json.loads(request.body)
        vin = data.get('vin', '').strip().upper()
        comment = data.get('comment', '').strip()

        # Валидация VIN
        if not vin:
            return JsonResponse({'success': False, 'error': 'VIN номер не может быть пустым'})

        if len(vin) != 17:
            return JsonResponse({'success': False, 'error': 'VIN номер должен содержать 17 символов'})

        # Проверяем, не добавлен ли уже этот VIN
        if UserGarage.objects.filter(user=request.user, vin=vin).exists():
            return JsonResponse({'success': False, 'error': 'Этот автомобиль уже добавлен в гараж'})

        # Создаем запись в гараже
        garage_vehicle = UserGarage.objects.create(
            user=request.user,
            vin=vin,
            comment=comment
        )

        # Логируем действие
        UserAction.objects.create(
            user=request.user,
            action_type='add_to_garage',
            description=f'Добавлен автомобиль в гараж: {vin}',
            ip_address=get_client_ip(request)
        )

        return JsonResponse({
            'success': True,
            'vehicle': {
                'id': garage_vehicle.id,
                'vin': garage_vehicle.vin,
                'comment': garage_vehicle.comment,
                'created_at': garage_vehicle.created_at.strftime('%d.%m.%Y %H:%M')
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def remove_vehicle_from_garage(request, vehicle_id):
    """API для удаления автомобиля из гаража"""
    try:
        garage_vehicle = UserGarage.objects.get(id=vehicle_id, user=request.user)
        vin = garage_vehicle.vin
        garage_vehicle.delete()

        # Логируем действие
        UserAction.objects.create(
            user=request.user,
            action_type='remove_from_garage',
            description=f'Удален автомобиль из гаража: {vin}',
            ip_address=get_client_ip(request)
        )

        return JsonResponse({'success': True})

    except UserGarage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Автомобиль не найден'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip 