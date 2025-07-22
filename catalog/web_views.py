"""
Web views для каталога товаров
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import (
    ProductCategory, Product, Brand, Cart, Supplier, SupplierProduct, SupplierSyncLog,
    SupplierStaff, SupplierDeliveryMethod, SupplierOrderStatus,
    SupplierClientGroup, SupplierClient, SupplierOrder, SupplierBalanceTransaction
)
from .forms import AdvancedSearchForm, QuickSearchForm
import requests
from django.conf import settings
from catalog.sputnik_api import search_sputnik_products


def catalog_home(request):
    """Главная страница каталога"""
    categories = ProductCategory.objects.filter(is_active=True)[:10]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    brands = Brand.objects.filter(is_active=True)[:12]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'brands': brands,
        'page_title': 'Каталог автозапчастей'
    }
    return render(request, 'catalog/home.html', context)


def categories_list(request):
    """Список всех категорий"""
    categories = ProductCategory.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'page_title': 'Категории товаров'
    }
    return render(request, 'catalog/categories.html', context)


def category_detail(request, category_id):
    """Детальная страница категории с товарами"""
    category = get_object_or_404(ProductCategory, id=category_id, is_active=True)
    
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('brand', 'category')
    
    # Пагинация
    paginator = Paginator(products, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'page_title': f'Категория: {category.name}'
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, product_id):
    """Детальная страница товара"""
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related('oem_numbers__oem_number'),
        id=product_id,
        is_active=True
    )
    
    # Похожие товары
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:6]
    
    # Получаем OEM аналоги
    oem_analogs = []
    for product_oem in product.oem_numbers.all():
        # Находим все товары с тем же OEM номером, кроме текущего
        analogs = Product.objects.filter(
            oem_numbers__oem_number=product_oem.oem_number,
            is_active=True
        ).exclude(id=product.id).select_related('brand', 'category')
        oem_analogs.extend(analogs)
    
    # Убираем дубликаты
    seen = set()
    unique_analogs = []
    for analog in oem_analogs:
        if analog.id not in seen:
            seen.add(analog.id)
            unique_analogs.append(analog)
    
    context = {
        'product': product,
        'related_products': related_products,
        'oem_analogs': unique_analogs,
        'page_title': product.name
    }
    return render(request, 'catalog/product_detail.html', context)


def product_search(request):
    from catalog.brand_country_map import brand_country_iso
    from catalog.sputnik_api import get_sputnik_brands_full, search_sputnik_products
    query = request.GET.get('q', '')
    brand = request.GET.get('brand', '').strip()
    sort = request.GET.get('sort')
    order = request.GET.get('order', 'asc')
    products = []
    error = None
    brands_list = []
    show_brand_select = False
    main_products = []  # Основной артикул
    analog_products = []  # Аналоги
    transit_products = []  # Транзитные склады
    if query:
        if not brand:
            # Получаем список брендов для выбора
            brands_list = get_sputnik_brands_full(query)
            show_brand_select = True
        else:
            sputnik_result = search_sputnik_products(query, brand)
            if sputnik_result and sputnik_result.get('data'):
                query_lower = query.strip().lower().replace(' ', '').replace('+', '')
                brand_lower = brand.strip().lower()
                for item in sputnik_result['data']:
                    product = {
                        'name': item.get('name'),
                        'article': item.get('articul'),
                        'brand': item.get('brand', {}).get('name'),
                        'description': '',
                        'stock_quantity': item.get('quantity'),
                        'delivery_time': item.get('delivery_day'),
                        'warehouse': item.get('price_name'),
                        'price': item.get('price'),
                        'supplier': 'Авто-Спутник',
                        'is_analog': str(item.get('analog', '')).lower() in ['true', '1', 'yes'],
                        'delivery_date': item.get('delivery_date'),
                        'unit': item.get('unit'),
                        'min': item.get('min'),
                        'cratnost': item.get('cratnost'),
                        'vozvrat': item.get('vozvrat'),
                        'official_diler': item.get('official_diler'),
                        'our': item.get('our', False),
                    }
                    article_lower = str(product['article']).strip().lower().replace(' ', '').replace('+', '')
                    product_brand_lower = str(product['brand']).strip().lower()
                    warehouse = str(product['warehouse']).lower()
                    # Основной артикул: точное совпадение артикул+бренд и our: true
                    if product['our'] and article_lower == query_lower and product_brand_lower == brand_lower:
                        main_products.append(product)
                    # Аналоги: analog: true и warehouse не содержит 'сторонний'/'транзит'
                    elif product['is_analog'] and not ('сторон' in warehouse or 'транзит' in warehouse):
                        analog_products.append(product)
                    # Транзитные склады: analog: true и warehouse содержит 'сторонний' или 'транзит'
                    elif product['is_analog'] and ('сторон' in warehouse or 'транзит' in warehouse):
                        transit_products.append(product)
                print(f"DEBUG: main_products count: {len(main_products)}")
                print(f"DEBUG: analog_products count: {len(analog_products)}")
                print(f"DEBUG: transit_products count: {len(transit_products)}")
                if analog_products:
                    print('DEBUG: analog_products example:', analog_products[0])
                if transit_products:
                    print('DEBUG: transit_products example:', transit_products[0])
                print('DEBUG: Все товары из Sputnik API:')
                for item in sputnik_result['data']:
                    print(f"ARTICUL: {item.get('articul')}, BRAND: {item.get('brand', {}).get('name')}, ANALOG: {item.get('analog')}, OUR: {item.get('our')}, PRICE_NAME: {item.get('price_name')}")
            elif sputnik_result and sputnik_result.get('error'):
                error = sputnik_result.get('error')

    def parse_delivery_time(val):
        import datetime, re
        if not val:
            return datetime.datetime.max
        if 'завтра' in val.lower():
            return datetime.datetime.now() + datetime.timedelta(days=1)
        m = re.search(r'(\d{2})[.](\d{2})[.](\d{4})', val)
        if m:
            try:
                return datetime.datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except Exception:
                return datetime.datetime.max
        return datetime.datetime.max

    if sort == 'delivery_time':
        products = sorted(products, key=lambda x: parse_delivery_time(x.get('delivery_time')), reverse=(order=='desc'))
    elif sort == 'price':
        def parse_price(val):
            try:
                return float(val)
            except Exception:
                return float('inf')
        products = sorted(products, key=lambda x: parse_price(x.get('price')), reverse=(order=='desc'))

    if query:
        query_lower = query.strip().lower().replace(' ', '').replace('+', '')
        main_articles = []
        other_products = []
        new_products = []
        for p in products:
            if not isinstance(p, dict):
                p = {
                    'article': getattr(p, 'article', ''),
                    'brand': getattr(p, 'brand', ''),
                    'description': getattr(p, 'description', ''),
                    'name': getattr(p, 'name', ''),
                    'stock_quantity': getattr(p, 'stock_quantity', None),
                    'delivery_time': getattr(p, 'delivery_time', ''),
                    'warehouse': getattr(p, 'warehouse', ''),
                    'price': getattr(p, 'price', ''),
                }
            article = str(p.get('article', '')).strip().lower().replace(' ', '').replace('+', '')
            if article == query_lower:
                p['is_main_article'] = True
                main_articles.append(p)
            else:
                p['is_main_article'] = False
                other_products.append(p)
        # Добавляем аналоги в конец списка
        products = main_articles + other_products

    # Приведение price к float для корректной сортировки в шаблоне
    for p in products:
        try:
            p['price'] = float(p.get('price', 1e9))
        except Exception:
            p['price'] = 1e9

    # === Автоматический отладочный вывод по товарам автоспутника ===
    sputnik_products = [p for p in products if p.get('supplier') == 'Авто-Спутник']
    print(f"DEBUG: Sputnik products count: {len(sputnik_products)}")
    if sputnik_products:
        print(f"DEBUG: Sputnik product example: {sputnik_products[0]}")
    else:
        print("DEBUG: Sputnik products not found in products list")

    main_warehouses = ['СПб Север', 'СПб Юг', 'Москва']
    offers_by_article = {}
    for p in products:
        article = p.get('article', '').strip()
        wh = (p.get('warehouse') or '').strip()
        if not article:
            continue
        if article not in offers_by_article:
            offers_by_article[article] = {'main': [], 'other': [], 'all': []}
        if wh in main_warehouses:
            offers_by_article[article]['main'].append(p)
        else:
            offers_by_article[article]['other'].append(p)
        offers_by_article[article]['all'].append(p)
    
    # Сортируем все предложения по приоритету складов и цене (как в Автоконтиненте)
    warehouse_priority = {
        'СПб Север': 1,
        'СПб Юг': 2, 
        'Москва': 3
    }
    
    for article in offers_by_article:
        # Сортируем по приоритету складов, затем по цене
        offers_by_article[article]['all'].sort(key=lambda x: (
            warehouse_priority.get(x.get('warehouse', ''), 999),  # Приоритет склада
            float(x.get('price', 1e9))  # Цена
        ))
        
        # Берем только первые 3 для отображения (как в Автоконтиненте)
        offers_by_article[article]['display'] = offers_by_article[article]['all'][:3]
        
        # Остальные для кнопки "Ещё предложения"
        offers_by_article[article]['hidden'] = offers_by_article[article]['all'][3:]

    print('DEBUG: offers_by_article keys count:', len(offers_by_article))
    print('DEBUG: first 3 articles:', list(offers_by_article.keys())[:3])
    for article, offers in offers_by_article.items():
        print(f'DEBUG: Article {article}: display={len(offers.get("display", []))}, hidden={len(offers.get("hidden", []))}, all={len(offers.get("all", []))}')
        print(f'DEBUG: Article {article} display keys: {list(offers.keys())}')

    # Отладочная информация
    print(f"DEBUG: query = '{query}'")
    print(f"DEBUG: offers_by_article keys = {list(offers_by_article.keys()) if offers_by_article else 'None'}")
    print(f"DEBUG: request.GET = {dict(request.GET)}")
    
    context = {
        'offers_by_article': offers_by_article,
        'query': query,
        'error': error,
        'page_title': 'Результаты поиска',
        'request': request,
        'brand_country_iso': brand_country_iso,
        'brands_list': brands_list,
        'show_brand_select': show_brand_select,
        'main_products': main_products,
        'analog_products': analog_products,
        'transit_products': transit_products,
    }
    return render(request, 'catalog/search.html', context)


def cart_view(request):
    """Просмотр корзины"""
    cart_items = []
    total_amount = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all().select_related('product')
            # Добавляем вычисленное поле total_price для каждого элемента
            for item in cart_items:
                item.total_price = item.quantity * item.price
                total_amount += item.total_price
        except Cart.DoesNotExist:
            pass
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'page_title': 'Корзина'
    }
    return render(request, 'catalog/cart.html', context)

# =================== ПОСТАВЩИКИ ===================

@staff_member_required
def supplier_list(request):
    """Список поставщиков"""
    suppliers = Supplier.objects.all().order_by('name')
    
    # Поиск
    search = request.GET.get('search', '')
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(contact_person__icontains=search)
        )
    
    # Фильтрация по активности
    active_filter = request.GET.get('active', '')
    if active_filter == 'true':
        suppliers = suppliers.filter(is_active=True)
    elif active_filter == 'false':
        suppliers = suppliers.filter(is_active=False)
    
    # Пагинация
    paginator = Paginator(suppliers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'active_filter': active_filter,
    }
    
    return render(request, 'catalog/suppliers/list.html', context)


@staff_member_required
def supplier_detail(request, pk):
    """Детальная информация о поставщике"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    # Последние товары
    recent_products = supplier.products.order_by('-updated_at')[:10]
    
    # Последние логи синхронизации
    recent_logs = supplier.sync_logs.order_by('-created_at')[:5]
    
    # Статистика
    stats = {
        'total_products': supplier.products.count(),
        'active_products': supplier.products.filter(is_active=True).count(),
        'linked_products': supplier.products.filter(product__isnull=False).count(),
        'total_stock_value': sum(p.price * p.stock_quantity for p in supplier.products.all()),
    }
    
    context = {
        'supplier': supplier,
        'recent_products': recent_products,
        'recent_logs': recent_logs,
        'stats': stats,
    }
    
    return render(request, 'catalog/suppliers/detail.html', context)


@staff_member_required
def supplier_test_api(request, pk):
    """Тестирование API поставщика"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        success, message = supplier.test_api_connection()
        
        if success:
            messages.success(request, f'API тест успешен: {message}')
        else:
            messages.error(request, f'API тест неудачен: {message}')
    
    return redirect('catalog_web:supplier_detail', pk=pk)


@staff_member_required
def supplier_sync(request, pk):
    """Синхронизация товаров поставщика"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        success, message = supplier.sync_products()
        
        if success:
            messages.success(request, f'Синхронизация завершена: {message}')
        else:
            messages.error(request, f'Ошибка синхронизации: {message}')
    
    return redirect('catalog_web:supplier_detail', pk=pk)


@staff_member_required
def supplier_products(request, pk):
    """Товары поставщика"""
    supplier = get_object_or_404(Supplier, pk=pk)
    products = supplier.products.select_related('product').order_by('-updated_at')
    
    # Фильтрация
    has_product = request.GET.get('has_product', '')
    if has_product == 'true':
        products = products.filter(product__isnull=False)
    elif has_product == 'false':
        products = products.filter(product__isnull=True)
    
    active_filter = request.GET.get('active', '')
    if active_filter == 'true':
        products = products.filter(is_active=True)
    elif active_filter == 'false':
        products = products.filter(is_active=False)
    
    search = request.GET.get('search', '')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(supplier_article__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(products, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'supplier': supplier,
        'page_obj': page_obj,
        'has_product': has_product,
        'active_filter': active_filter,
        'search': search,
    }
    
    return render(request, 'catalog/suppliers/products.html', context)


# === ПРЕДСТАВЛЕНИЯ ДЛЯ API АВТОЗАПЧАСТЕЙ ===

@staff_member_required
def supplier_entities(request, supplier_id):
    """Страница сущностей поставщика (сотрудники, клиенты, заказы и т.д.)"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if supplier.api_type != 'autoparts':
        messages.error(request, 'Интеграция доступна только для API автозапчастей')
        return redirect('catalog_web:suppliers_list')
    
    # Получаем статистику
    stats = {
        'staff_count': supplier.staff.count(),
        'delivery_methods_count': supplier.delivery_methods.count(),
        'order_statuses_count': supplier.order_statuses.count(),
        'client_groups_count': supplier.client_groups.count(),
        'clients_count': supplier.clients.count(),
        'orders_count': supplier.orders.count(),
        'balance_transactions_count': supplier.balance_transactions.count(),
    }
    
    context = {
        'supplier': supplier,
        'stats': stats,
    }
    
    return render(request, 'catalog/suppliers/entities.html', context)


@staff_member_required
def supplier_staff_list(request, supplier_id):
    """Список сотрудников поставщика"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    staff = supplier.staff.all()
    
    # Фильтры
    is_active = request.GET.get('active', '')
    if is_active == 'true':
        staff = staff.filter(is_active=True)
    elif is_active == 'false':
        staff = staff.filter(is_active=False)
    
    search = request.GET.get('search', '')
    if search:
        staff = staff.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(staff, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'supplier': supplier,
        'page_obj': page_obj,
        'is_active': is_active,
        'search': search,
    }
    
    return render(request, 'catalog/suppliers/staff.html', context)


@staff_member_required
def supplier_clients_list(request, supplier_id):
    """Список клиентов поставщика"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    clients = supplier.clients.all().select_related('group', 'manager')
    
    # Фильтры
    is_active = request.GET.get('active', '')
    if is_active == 'true':
        clients = clients.filter(is_active=True)
    elif is_active == 'false':
        clients = clients.filter(is_active=False)
    
    group_id = request.GET.get('group', '')
    if group_id:
        clients = clients.filter(group_id=group_id)
    
    manager_id = request.GET.get('manager', '')
    if manager_id:
        clients = clients.filter(manager_id=manager_id)
    
    search = request.GET.get('search', '')
    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(clients, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Для фильтров
    groups = supplier.client_groups.all()
    managers = supplier.staff.filter(is_active=True)
    
    context = {
        'supplier': supplier,
        'page_obj': page_obj,
        'groups': groups,
        'managers': managers,
        'is_active': is_active,
        'group_id': group_id,
        'manager_id': manager_id,
        'search': search,
    }
    
    return render(request, 'catalog/suppliers/clients.html', context)


@staff_member_required
def supplier_orders_list(request, supplier_id):
    """Список заказов поставщика"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    orders = supplier.orders.all().select_related('client', 'status', 'delivery_method')
    
    # Фильтры
    status_id = request.GET.get('status', '')
    if status_id:
        orders = orders.filter(status_id=status_id)
    
    client_id = request.GET.get('client', '')
    if client_id:
        orders = orders.filter(client_id=client_id)
    
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(number__icontains=search) |
            Q(client__name__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Для фильтров
    statuses = supplier.order_statuses.all()
    clients = supplier.clients.filter(is_active=True)[:100]  # Ограничиваем для производительности
    
    context = {
        'supplier': supplier,
        'page_obj': page_obj,
        'statuses': statuses,
        'clients': clients,
        'status_id': status_id,
        'client_id': client_id,
        'search': search,
    }
    
    return render(request, 'catalog/suppliers/orders.html', context)


@staff_member_required
def supplier_order_detail(request, supplier_id, order_id):
    """Детальная страница заказа"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    order = get_object_or_404(
        SupplierOrder,
        id=order_id,
        supplier=supplier
    )
    
    # Получаем позиции заказа
    items = order.items.all().order_by('id')
    
    # Получаем историю заказа
    history = order.history.all().select_related('status', 'staff').order_by('-created_at')
    
    context = {
        'supplier': supplier,
        'order': order,
        'items': items,
        'history': history,
    }
    
    return render(request, 'catalog/suppliers/order_detail.html', context)


@staff_member_required
def supplier_sync_entities(request, supplier_id):
    """Синхронизация сущностей с API"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if supplier.api_type != 'autoparts':
        messages.error(request, 'Синхронизация доступна только для API автозапчастей')
        return redirect('catalog_web:supplier_entities', supplier_id=supplier_id)
    
    if request.method == 'POST':
        entity_type = request.POST.get('entity_type', 'all')
        
        try:
            if entity_type == 'all':
                success, message = supplier.sync_all_entities()
            elif entity_type == 'staff':
                success, message = supplier.sync_staff()
            elif entity_type == 'delivery_methods':
                success, message = supplier.sync_delivery_methods()
            elif entity_type == 'order_statuses':
                success, message = supplier.sync_order_statuses()
            elif entity_type == 'client_groups':
                success, message = supplier.sync_client_groups()
            elif entity_type == 'clients':
                success, message = supplier.sync_clients()
            elif entity_type == 'orders':
                success, message = supplier.sync_orders()
            else:
                success, message = False, 'Неизвестный тип сущности'
            
            if success:
                messages.success(request, f'Синхронизация завершена: {message}')
            else:
                messages.error(request, f'Ошибка синхронизации: {message}')
                
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
    
    return redirect('catalog_web:supplier_entities', supplier_id=supplier_id)


@staff_member_required
def supplier_search_products(request, supplier_id):
    """Поиск товаров через API"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if supplier.api_type != 'autoparts':
        messages.error(request, 'Поиск доступен только для API автозапчастей')
        return redirect('catalog_web:supplier_products', supplier_id=supplier_id)
    
    search_results = None
    article = request.GET.get('article', '')
    
    if article:
        try:
            success, result = supplier.search_products_by_article(article)
            if success:
                search_results = result
                messages.success(request, result.get('message', 'Поиск выполнен'))
            else:
                messages.error(request, f'Ошибка поиска: {result}')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
    
    context = {
        'supplier': supplier,
        'article': article,
        'search_results': search_results,
    }
    
    return render(request, 'catalog/suppliers/search.html', context)


def advanced_search(request):
    """Расширенный поиск товаров"""
    form = AdvancedSearchForm(request.GET or None)
    products = []
    api_results = []
    total_local = 0
    total_api = 0
    
    if form.is_valid():
        # Получаем параметры поиска
        query = form.cleaned_data.get('query')
        search_type = form.cleaned_data.get('search_type')
        category = form.cleaned_data.get('category')
        brand = form.cleaned_data.get('brand')
        supplier = form.cleaned_data.get('supplier')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        in_stock_only = form.cleaned_data.get('in_stock_only')
        featured_only = form.cleaned_data.get('featured_only')
        order_by = form.cleaned_data.get('order_by')
        use_supplier_api = form.cleaned_data.get('use_supplier_api')
        
        # Поиск в локальной базе
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand', 'primary_supplier')
        
        # Поиск по тексту
        if query:
            if search_type == 'article':
                queryset = queryset.filter(article__icontains=query)
            elif search_type == 'name':
                queryset = queryset.filter(name__icontains=query)
            elif search_type == 'description':
                queryset = queryset.filter(description__icontains=query)
            elif search_type == 'oem':
                queryset = queryset.filter(oem_numbers__oem_number__number__icontains=query)
            else:  # all
                queryset = queryset.filter(
                    Q(article__icontains=query) |
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(oem_numbers__oem_number__number__icontains=query)
                )
        
        # Фильтры
        if category:
            queryset = queryset.filter(category=category)
        
        if brand:
            queryset = queryset.filter(brand=brand)
        
        if supplier:
            queryset = queryset.filter(primary_supplier=supplier)
        
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        if in_stock_only:
            queryset = queryset.filter(stock_quantity__gt=0)
        
        if featured_only:
            queryset = queryset.filter(is_featured=True)
        
        # Сортировка
        if order_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif order_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif order_by == 'relevance':
            queryset = queryset.order_by('-is_featured', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        products = queryset
        total_local = queryset.count()
        
        # Поиск через API поставщиков
        if use_supplier_api and query:
            api_results = _search_via_suppliers_api(query, brand)
            total_api = sum(result['count'] for result in api_results)
    
    # Пагинация
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'products': page_obj,
        'api_results': api_results,
        'total_local': total_local,
        'total_api': total_api,
        'page_title': 'Расширенный поиск'
    }
    return render(request, 'catalog/advanced_search.html', context)


def _search_via_suppliers_api(query, brand=None):
    """Поиск через API поставщиков"""
    results = []
    active_suppliers = Supplier.objects.filter(is_active=True, api_type='autoparts')
    
    for supplier in active_suppliers:
        try:
            if brand:
                success, data = supplier.search_products_by_article(query, brand.name)
            else:
                success, data = supplier.search_products_by_article(query)
            
            if success and data:
                results.append({
                    'supplier': supplier,
                    'products': data,
                    'count': len(data) if isinstance(data, list) else 1
                })
        except Exception as e:
            # Логируем ошибку, но продолжаем поиск
            pass
    
    return results


@require_http_methods(["GET"])
def quick_search(request):
    """AJAX представление для быстрого поиска"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    # Поиск в локальной базе
    products = Product.objects.filter(
        Q(article__icontains=query) |
        Q(name__icontains=query),
        is_active=True
    ).select_related('category', 'brand')[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'article': product.article,
            'name': product.name,
            'brand': product.brand.name,
            'price': str(product.final_price),
            'url': f'/catalog/product/{product.id}/',
            'in_stock': product.in_stock
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def supplier_api_search(request):
    """AJAX поиск через API поставщиков"""
    query = request.GET.get('q', '').strip()
    supplier_id = request.GET.get('supplier_id')
    
    if not query:
        return JsonResponse({'error': 'Запрос не может быть пустым'})
    
    results = []
    
    try:
        if supplier_id:
            # Поиск через конкретного поставщика
            supplier = get_object_or_404(Supplier, id=supplier_id, is_active=True)
            success, data = supplier.search_products_by_article(query)
            
            if success and data:
                results.append({
                    'supplier': supplier.name,
                    'products': data,
                    'status': 'success'
                })
            else:
                results.append({
                    'supplier': supplier.name,
                    'products': [],
                    'status': 'error',
                    'message': data
                })
        else:
            # Поиск через всех активных поставщиков
            suppliers = Supplier.objects.filter(is_active=True, api_type='autoparts')
            
            for supplier in suppliers:
                try:
                    success, data = supplier.search_products_by_article(query)
                    
                    results.append({
                        'supplier': supplier.name,
                        'products': data if success else [],
                        'status': 'success' if success else 'error',
                        'message': '' if success else data
                    })
                except Exception as e:
                    results.append({
                        'supplier': supplier.name,
                        'products': [],
                        'status': 'error',
                        'message': str(e)
                    })
    
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
    return JsonResponse({'results': results})


def sputnik_search_test(request):
    """Тестовый view для поиска по АвтоСпутник. Возвращает JSON-ответ."""
    articul = request.GET.get('articul', '').strip()
    brand = request.GET.get('brand', '').strip() if 'brand' in request.GET else ''
    if not articul:
        return JsonResponse({'error': 'Нужно указать articul'}, status=400)
    result = search_sputnik_products(articul)
    if result is None:
        return JsonResponse({'error': 'Ошибка поиска или получения токена'}, status=500)
    return JsonResponse(result)

# --- КОРЗИНА АВТОКОНТИНЕНТ ---
def autokont_basket_add(request):
    """Добавление товара в корзину Автоконтинент"""
    part_id = request.POST.get('part_id')
    warehouse_id = request.POST.get('warehouse_id')
    quantity = request.POST.get('quantity', 1)
    if not (part_id and warehouse_id):
        return JsonResponse({'status': 'error', 'message': 'Не указан part_id или warehouse_id'})
    url = 'http://api.autokontinent.ru/v1/basket/add.json'
    auth = (settings.AUTOKONT_LOGIN, settings.AUTOKONT_PASSWORD)
    params = {
        'part_id': part_id,
        'warehouse_id': warehouse_id,
        'quantity': quantity
    }
    try:
        resp = requests.get(url, params=params, auth=auth, timeout=10)
        data = resp.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def autokont_basket_get(request):
    """Получение содержимого корзины Автоконтинент"""
    url = 'http://api.autokontinent.ru/v1/basket/get.json'
    auth = (settings.AUTOKONT_LOGIN, settings.AUTOKONT_PASSWORD)
    try:
        resp = requests.get(url, auth=auth, timeout=10)
        data = resp.json()
        return render(request, 'catalog/basket.html', {'basket': data})
    except Exception as e:
        return render(request, 'catalog/basket.html', {'basket': [], 'error': str(e)})


def autokont_basket_del(request):
    """Удаление позиции из корзины Автоконтинент"""
    basket_id = request.POST.get('basket_id')
    version = request.POST.get('version')
    if not (basket_id and version):
        return JsonResponse({'status': 'error', 'message': 'Не указан basket_id или version'})
    url = 'http://api.autokontinent.ru/v1/basket/del.json'
    from django.conf import settings
    auth = (settings.AUTOKONT_LOGIN, settings.AUTOKONT_PASSWORD)
    params = {'basket_id': basket_id, 'version': version}
    try:
        resp = requests.get(url, params=params, auth=auth, timeout=10)
        data = resp.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def autokont_basket_clear(request):
    """Очистка корзины Автоконтинент"""
    url = 'http://api.autokontinent.ru/v1/basket/clear.json'
    from django.conf import settings
    auth = (settings.AUTOKONT_LOGIN, settings.AUTOKONT_PASSWORD)
    try:
        resp = requests.get(url, auth=auth, timeout=10)
        data = resp.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def autokont_basket_order(request):
    """Оформление заказа (отправка корзины в заказ) Автоконтинент"""
    delivery_mode_id = request.POST.get('delivery_mode_id', 1)
    url = 'http://api.autokontinent.ru/v1/basket/order.json'
    from django.conf import settings
    auth = (settings.AUTOKONT_LOGIN, settings.AUTOKONT_PASSWORD)
    params = {'delivery_mode_id': delivery_mode_id}
    try:
        resp = requests.get(url, params=params, auth=auth, timeout=10)
        data = resp.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def autokont_order_history(request):
    """История заказов пользователя из Автоконтинент"""
    from django.conf import settings
    import datetime
    url = 'http://api.autokontinent.ru/v1/order/get.json'
    auth = (settings.AUTOKONT_LOGIN, settings.AUTOKONT_PASSWORD)
    # По умолчанию за 30 дней
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if not date_from:
        date_from = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.date.today().strftime('%Y-%m-%d')
    params = {'date_from': date_from, 'date_to': date_to}
    try:
        resp = requests.get(url, params=params, auth=auth, timeout=10)
        data = resp.json()
        return render(request, 'catalog/order_history.html', {'orders': data, 'date_from': date_from, 'date_to': date_to})
    except Exception as e:
        return render(request, 'catalog/order_history.html', {'orders': [], 'error': str(e)})
