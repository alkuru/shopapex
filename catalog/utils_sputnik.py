from collections import defaultdict

VISIBLE_LIMIT = 3
HIDDEN_LIMIT = 10  # максимум под кнопкой

def group_offers(items):
    """
    items – это полный список из API (уже без фильтрации по our).
    Группируем по (articul, brand.name).
    Возвращаем список групп с visible/hidden.
    """
    groups = defaultdict(list)
    for it in items:
        if not isinstance(it, dict):
            print(f"[group_offers] skip non-dict: {type(it)} -> {it!r}")
            continue

        articul = (it.get('articul') or it.get('article') or '').strip()

        brand_raw = it.get('brand')
        if isinstance(brand_raw, dict):
            brand_name = (brand_raw.get('name') or '').strip()
        elif isinstance(brand_raw, str):
            brand_name = brand_raw.strip()
        else:
            brand_name = ''

        key = (articul, brand_name)
        groups[key].append(it)

    result = []
    for (articul, brand), offers in groups.items():
        offers.sort(key=lambda o: (
            0 if (
                o.get('our')
                or 'основн' in (o.get('price_name','').lower())
                or 'автоспутник' in (o.get('price_name','').lower())
            ) else 1,
            o.get('price') or 0
        ))
        visible = offers[:VISIBLE_LIMIT]
        rest    = offers[VISIBLE_LIMIT:]
        hidden  = rest[:HIDDEN_LIMIT]
        hidden_total = len(rest)
        hidden_shown = len(hidden)
        result.append({
            "articul": articul,
            "brand": brand,
            "visible": visible,
            "hidden": hidden,
            "hidden_total": hidden_total,   # всего скрытых (для инфы)
            "hidden_shown": hidden_shown,   # сколько реально покажем
        })
    return result
    return result
