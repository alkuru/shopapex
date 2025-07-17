"""
Web views для VIN поиска
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import VehicleInfo, VinRequest, VinSearchResult
from catalog.models import Product


def vin_search_home(request):
    """Главная страница VIN поиска"""
    context = {
        'page_title': 'Поиск по VIN коду'
    }
    return render(request, 'vin_search/home.html', context)


def vin_search_results(request):
    """Результаты поиска по VIN"""
    vin_code = request.GET.get('vin', '').strip().upper()
    products = []
    vin_info = None
    
    if vin_code:
        # Поиск VIN в базе
        try:
            vin_request = VinRequest.objects.get(vin_code=vin_code, status='completed')
            vin_info = getattr(vin_request, 'vehicle_info', None)
            products = []
            if vin_info:
                # Получаем продукты из результатов поиска
                results = vin_request.search_results.all()
                product_ids = [result.product.id for result in results if result.product and result.product.is_active]
                products = Product.objects.filter(id__in=product_ids)
        except VinRequest.DoesNotExist:
            vin_info = None
            products = []
            # Создаем запрос на поиск
            if request.user.is_authenticated:
                VinRequest.objects.create(
                    user=request.user,
                    vin_code=vin_code,
                    status='pending'
                )
                messages.info(request, 'VIN код не найден в базе. Запрос отправлен на обработку.')
            else:
                messages.warning(request, 'VIN код не найден в базе. Войдите в систему для создания запроса на поиск.')
    
    context = {
        'vin_code': vin_code,
        'vin_info': vin_info,
        'products': products,
        'page_title': f'Поиск по VIN: {vin_code}' if vin_code else 'Поиск по VIN коду'
    }
    return render(request, 'vin_search/results.html', context)


@login_required
def vin_request_detail(request, request_id):
    """Детали запроса на поиск VIN"""
    vin_request = get_object_or_404(VinRequest, id=request_id, user=request.user)
    
    context = {
        'vin_request': vin_request,
        'page_title': f'Запрос #{vin_request.id}'
    }
    return render(request, 'vin_search/request_detail.html', context)


@login_required
def my_requests(request):
    """Мои запросы на поиск VIN"""
    requests_list = VinRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(requests_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'requests': page_obj,
        'page_title': 'Мои запросы на поиск'
    }
    return render(request, 'vin_search/my_requests.html', context)
