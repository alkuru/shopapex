from collections import defaultdict

VISIBLE_LIMIT = 3
HIDDEN_LIMIT = 10  # максимум под кнопкой

def group_offers(items):
    """
    items – это полный список из API (уже без фильтрации по our).
    Группируем по (articul, brand.name).
    Возвращаем список групп с visible/hidden.
    Теперь visible всегда только 1 предложение (первое), остальные в hidden.
    Аналоги сортируются по алфавиту бренда.
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

    # Сортировка групп: основной артикул (our=True) первым, далее аналоги по алфавиту бренда
    def group_sort_key(group):
        articul, brand = group[0], group[1]
        offers = groups[(articul, brand)]
        # Если есть хотя бы один our=True — это основной
        is_main = any(o.get('our') for o in offers)
        return (0 if is_main else 1, brand.lower())

    sorted_groups = sorted(groups.items(), key=lambda g: group_sort_key(g[0]))

    result = []
    for (articul, brand), offers in sorted_groups:
        offers.sort(key=lambda o: (
            0 if (
                o.get('our')
                or 'основн' in (o.get('price_name','').lower())
                or 'автоспутник' in (o.get('price_name','').lower())
            ) else 1,
            o.get('price') or 0
        ))
        visible = offers[:1]  # только первое предложение
        rest    = offers[1:]
        hidden  = rest  # показываем все остальные по кнопке
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
