from collections import defaultdict

VISIBLE_LIMIT = 3

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
        # сортируем по цене (можно поменять на срок)
        offers.sort(key=lambda o: o.get('price', 0))
        visible = offers[:VISIBLE_LIMIT]
        hidden = offers[VISIBLE_LIMIT:]
        result.append({
            "articul": articul,
            "brand": brand,
            "visible": visible,
            "hidden": hidden,
            "hidden_count": len(hidden)
        })
    return result
