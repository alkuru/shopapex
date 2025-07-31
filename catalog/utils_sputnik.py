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

        # Нормализуем бренд для группировки
        normalized_brand = brand_name.lower()
        if normalized_brand in ['zimmermann', 'otto zimmermann']:
            normalized_brand = 'zimmermann'
        elif normalized_brand in ['victor reinz', 'reinz']:
            normalized_brand = 'victor reinz'
        elif normalized_brand in ['mann', 'mann-filter']:
            normalized_brand = 'mann'
        elif normalized_brand in ['mahle', 'knecht/mahle', 'knecht', 'mahle original']:
            normalized_brand = 'mahle'
        elif normalized_brand in ['febi', 'febi bilstein']:
            normalized_brand = 'febi'
        elif normalized_brand in ['citroen/peugeot', 'citroën']:
            normalized_brand = 'citroen/peugeot'
        elif normalized_brand in ['hyundai/kia', 'hyundai', 'kia']:
            normalized_brand = 'hyundai'
        elif normalized_brand == 'kia hyundai':
            normalized_brand = 'kia hyundai'

        # Группируем по артикулу и нормализованному бренду
        key = (articul, normalized_brand)
        groups[key].append(it)

    # Сортировка групп: искомый бренд первым, затем основной артикул (our=True), далее аналоги по алфавиту бренда
    def group_sort_key(group):
        articul, brand = group[0], group[1]
        offers = groups[(articul, brand)]
        
        # Нормализуем искомый бренд для сравнения
        search_brand_normalized = search_brand.lower() if search_brand else ''
        if search_brand_normalized in ['zimmermann', 'otto zimmermann']:
            search_brand_normalized = 'zimmermann'
        elif search_brand_normalized in ['victor reinz', 'reinz']:
            search_brand_normalized = 'victor reinz'
        elif search_brand_normalized in ['mann', 'mann-filter']:
            search_brand_normalized = 'mann'
        elif search_brand_normalized in ['mahle', 'knecht/mahle', 'knecht', 'mahle original']:
            search_brand_normalized = 'mahle'
        elif search_brand_normalized in ['febi', 'febi bilstein']:
            search_brand_normalized = 'febi'
        elif search_brand_normalized in ['fiat/alfa/lancia', 'fiat']:
            search_brand_normalized = 'fiat'
        
        # Приоритет 1: искомый бренд
        if search_brand and brand.lower() == search_brand_normalized:
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
            # ГЛОБАЛЬНОЕ ПРАВИЛО: ВСЕ товары "В наличии" (availability > 0) - ПРИОРИТЕТ 1
            0 if o.get('availability', 0) > 0 else
            # Приоритет 2: Все товары "не в наличии" по источнику
            1 if o.get('source') == 'autokontinent_db' else
            2 if o.get('source') == 'mikado_db' else
            3 if o.get('source') == 'autokontinent_analog' else
            4 if o.get('source') == 'mikado_analog' else
            5 if o.get('source') == 'autosputnik' else
            6,  # остальные
            # Внутри каждого приоритета сортируем по цене
            o.get('price') or 0
        ))
        
        # Определяем, является ли это главным артикулом (искомым)
        search_brand_normalized = search_brand.lower() if search_brand else ''
        if search_brand_normalized in ['zimmermann', 'otto zimmermann']:
            search_brand_normalized = 'zimmermann'
        elif search_brand_normalized in ['victor reinz', 'reinz']:
            search_brand_normalized = 'victor reinz'
        elif search_brand_normalized in ['mann', 'mann-filter']:
            search_brand_normalized = 'mann'
        elif search_brand_normalized in ['mahle', 'knecht/mahle', 'knecht']:
            search_brand_normalized = 'mahle'
        elif search_brand_normalized in ['fiat/alfa/lancia', 'fiat']:
            search_brand_normalized = 'fiat'
            
        is_main_article = search_brand and brand.lower() == search_brand_normalized
        
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
