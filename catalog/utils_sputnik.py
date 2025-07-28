from collections import defaultdict

VISIBLE_LIMIT = 3  # показываем 3 предложения для аналогов
MAIN_VISIBLE_LIMIT = 5  # показываем 5 предложений для главного артикула
HIDDEN_LIMIT = 10  # максимум под кнопкой

def group_offers(items, search_brand=None):
    """
    items – это полный список из API (уже без фильтрации по our).
    Группируем по (articul, brand.name).
    Возвращаем список групп с visible/hidden.
    Для главного артикула показываем 5 товаров, для аналогов - 3.
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

        # Группируем по артикулу и бренду (без источника)
        key = (articul, brand_name)
        groups[key].append(it)

    # Сортировка групп: искомый бренд первым, затем основной артикул (our=True), далее аналоги по алфавиту бренда
    def group_sort_key(group):
        articul, brand = group[0], group[1]
        offers = groups[(articul, brand)]
        
        # Приоритет 1: искомый бренд
        if search_brand and brand.lower() == search_brand.lower():
            return (0, 0, brand.lower())
        
        # Приоритет 2: основной артикул (our=True)
        is_main = any(o.get('our') for o in offers)
        if is_main:
            return (1, 0, brand.lower())
        
        # Приоритет 3: остальные по алфавиту
        return (2, 1, brand.lower())

    sorted_groups = sorted(groups.items(), key=lambda g: group_sort_key(g[0]))

    result = []
    for (articul, brand), offers in sorted_groups:
        offers.sort(key=lambda o: (
            # Приоритет 1: AutoKontinent товары в наличии
            0 if (o.get('source') == 'autokontinent_db' and o.get('availability', 0) > 0) else
            # Приоритет 2: AutoKontinent аналоги в наличии
            1 if (o.get('source') == 'autokontinent_analog' and o.get('availability', 0) > 0) else
            # Приоритет 3: AutoKontinent товары (не в наличии)
            2 if o.get('source') == 'autokontinent_db' else
            # Приоритет 4: AutoKontinent аналоги (не в наличии)
            3 if o.get('source') == 'autokontinent_analog' else
            # Приоритет 5: AutoSputnik товары
            4 if o.get('source') == 'autosputnik' else
            # Приоритет 6: остальные
            5,
            # Внутри каждого приоритета сортируем по цене
            o.get('price') or 0
        ))
        
        # Определяем, является ли это главным артикулом (искомым)
        is_main_article = search_brand and brand.lower() == search_brand.lower()
        
        # Выбираем лимит в зависимости от того, главный это артикул или аналог
        visible_limit = MAIN_VISIBLE_LIMIT if is_main_article else VISIBLE_LIMIT
        
        visible = offers[:visible_limit]  # показываем 5 для главного, 3 для аналогов
        rest    = offers[visible_limit:]
        hidden  = rest[:HIDDEN_LIMIT]  # показываем до 10 остальных по кнопке
        hidden_total = len(rest)
        hidden_shown = len(hidden)  # количество товаров в hidden
        result.append({
            "articul": articul,
            "brand": brand,
            "visible": visible,
            "hidden": hidden,
            "hidden_total": hidden_total,   # всего скрытых (для инфы)
            "hidden_shown": hidden_shown,   # сколько реально покажем
        })
    return result
