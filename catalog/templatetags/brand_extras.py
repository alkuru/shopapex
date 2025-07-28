from django import template
from catalog.brand_country_map import brand_country_iso
from catalog.models import Brand

register = template.Library()


@register.filter
def brand_flag(brand_name):
    """
    Возвращает ISO-код страны (например, 'pl', 'de') для бренда из базы или словаря, либо пустую строку.
    """
    if not brand_name:
        return ''
    # Если это объект с name, берём name
    if hasattr(brand_name, 'name'):
        name = brand_name.name
    else:
        name = str(brand_name)
    # Сначала ищем в базе
    from django.db.models import Q
    brand_obj = Brand.objects.filter(Q(name__iexact=name.strip())).first()
    if brand_obj and brand_obj.country_iso:
        return brand_obj.country_iso.lower()
    # Если не найдено — ищем в словаре (legacy)
    key = name.strip().lower().replace('+', '').replace('-', '').replace(' ', '')
    for k, v in brand_country_iso.items():
        k_norm = str(k).strip().lower().replace('+', '').replace('-', '').replace(' ', '')
        if key == k_norm:
            return v
    return ''


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def brand_rating_stars(rating):
    """
    Возвращает HTML для отображения рейтинга звездами
    """
    if not rating:
        return ''
    
    rating = int(rating)
    if rating < 1 or rating > 5:
        return ''
    
    # Определяем цвет и символы в зависимости от рейтинга
    if rating == 5:
        stars = '★' * 5
        color = '#FFD700'  # Золотой
        title = '5★ Премиум'
    elif rating == 4:
        stars = '★' * 4 + '☆'
        color = '#FFA500'  # Оранжевый
        title = '4★ Хорошее'
    elif rating == 3:
        stars = '★' * 3 + '☆' * 2
        color = '#FFC0CB'  # Розовый
        title = '3★ Средний'
    elif rating == 2:
        stars = '★' * 2 + '☆' * 3
        color = '#C0C0C0'  # Серебряный
        title = '2★ Низкий'
    else:  # rating == 1
        stars = '★' + '☆' * 4
        color = '#808080'  # Серый
        title = '1★ Плохой'
    
    return f'<span style="color: {color}; font-size: 14px;" title="{title}">{stars}</span>'


@register.filter
def brand_highlight(brand_name, selected_brand=None):
    """
    Возвращает CSS класс для подсветки бренда, если он совпадает с выбранным брендом (без учёта регистра и пробелов),
    либо если selected_brand пустой и бренд — MANN-FILTER
    """
    if not brand_name:
        return ''
    brand_norm = str(brand_name).lower().replace('-', '').replace(' ', '').strip()
    if selected_brand:
        selected_norm = str(selected_brand).lower().replace('-', '').replace(' ', '').strip()
        if brand_norm == selected_norm:
            return 'brand-mann'
    else:
        if brand_norm in ['mannfilter', 'knechtmahle']:
            return 'brand-mann'
    return ''


@register.filter
def brand_display(brand_name):
    """
    Приводит бренд к отображаемому виду: все варианты Mann/MANN/MANN FILTER/mann-filter -> MANN-FILTER
    """
    if not brand_name:
        return ''
    name = str(brand_name).strip().lower().replace(' ', '').replace('-', '')
    if name in ['mann', 'mannfilter']:
        return 'MANN-FILTER'
    return brand_name
