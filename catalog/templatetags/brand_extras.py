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
