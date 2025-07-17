import json
import hashlib
from datetime import timedelta
from django.utils import timezone
from .smart_search_models import SearchCache, Supplier

class CacheManager:
    """Менеджер кеша для умного поиска автозапчастей"""
    def get_cache_key(self, query_type, supplier_id, params):
        param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(f"{query_type}_{supplier_id}_{param_str}".encode()).hexdigest()

    def get_cached_result(self, query_type, supplier, params):
        cache_key = self.get_cache_key(query_type, supplier.id, params)
        try:
            cache_entry = SearchCache.objects.get(
                cache_key=cache_key,
                expires_at__gt=timezone.now()
            )
            cache_entry.hit_count += 1
            cache_entry.save(update_fields=["hit_count"])
            return cache_entry.result_data
        except SearchCache.DoesNotExist:
            return None

    def set_cache(self, query_type, supplier, params, result, ttl_minutes=5):
        cache_key = self.get_cache_key(query_type, supplier.id, params)
        expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
        SearchCache.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'query_type': query_type,
                'query_params': params,
                'result_data': result,
                'supplier': supplier,
                'expires_at': expires_at,
                'hit_count': 1
            }
        )

class SmartSearchService:
    """Сервис умного поиска автозапчастей с кешированием и работой с API поставщика"""
    def __init__(self):
        self.cache_manager = CacheManager()

    def search_products(self, article, brand=None, search_analogs=True):
        results = {
            'original': [],
            'analogs': [],
            'brands': [],
            'cached': False,
            'source': 'api'
        }
        # 1. Поиск брендов для артикула
        if not brand:
            brands = self._search_brands_smart(article)
            results['brands'] = brands
            # brands может быть списком строк или списком словарей
            if brands:
                if isinstance(brands, list):
                    first = brands[0]
                    if isinstance(first, dict) and 'brand' in first:
                        brand = first['brand']
                    elif isinstance(first, str):
                        brand = first
                elif isinstance(brands, dict) and 'brand' in brands:
                    brand = brands['brand']
        # 2. Поиск основных товаров
        if brand:
            products = self._search_products_smart(article, brand)
            results['original'] = products
        # 3. Поиск аналогов (если требуется)
        if search_analogs and brand:
            analogs = self._search_analogs_smart(article, brand)
            results['analogs'] = analogs
        return results

    def _search_brands_smart(self, article):
        params = {'article': article}
        for supplier in Supplier.objects.filter(is_active=True, api_type='autoparts'):
            cached = self.cache_manager.get_cached_result('brands', supplier, params)
            if cached:
                return cached
        for supplier in Supplier.objects.filter(is_active=True, api_type='autoparts'):
            success, brands = supplier.get_abcp_brands(article)
            if success and brands:
                self.cache_manager.set_cache('brands', supplier, params, brands, 10)
                return brands
        return []

    def _normalize_article(self, article):
        """
        Нормализация артикула: убрать пробелы, дефисы, спецсимволы, привести к нижнему регистру
        """
        import re
        return re.sub(r'[^a-zA-Z0-9]', '', article).strip().lower()

    def _search_products_smart(self, article, brand):
        # Логируем исходные данные
        print(f"[SEARCH] Запрос пользователя: article='{article}', brand='{brand}'")
        params = {'article': article, 'brand': brand}
        normalized_article = self._normalize_article(article)
        # 1. Проверка кеша
        for supplier in Supplier.objects.filter(is_active=True, api_type='autoparts'):
            cached = self.cache_manager.get_cached_result('search', supplier, params)
            if cached:
                print(f"[CACHE] Найден кеш для поиска: {supplier.name} {params}")
                return cached
        # 2. Поиск по API всех поставщиков
        for supplier in Supplier.objects.filter(is_active=True, api_type='autoparts'):
            print(f"[API] Запрос к API поставщика: {supplier.name} ({supplier.api_url}) по артикулу '{article}' и бренду '{brand}'")
            try:
                # Вызов API поставщика
                success, products = supplier._search_articles_by_brand(article, brand)
                print(f"[API-RESPONSE] success={success}, type={type(products)}, count={len(products) if hasattr(products, '__len__') else 'N/A'}")
                print(f"[API-RESPONSE] Сырые данные: {products}")
                # 2.2. Обработка и нормализация артикула в ответе
                filtered_products = []
                if success and products:
                    for prod in products:
                        # Унификация структуры: поддержка вложенных списков и разных ключей
                        if isinstance(prod, dict):
                            # Проверяем наличие артикула в разных ключах
                            prod_article = prod.get('number') or prod.get('article') or prod.get('code') or prod.get('numberFix')
                            if prod_article:
                                prod_article_norm = self._normalize_article(str(prod_article))
                                # Совпадение по нормализованному артикулу или частичное совпадение
                                if (
                                    prod_article_norm == normalized_article
                                    or normalized_article in prod_article_norm
                                    or prod_article_norm in normalized_article
                                ):
                                    filtered_products.append(prod)
                            else:
                                # Если нет артикула — всё равно добавляем (например, если только по ID)
                                filtered_products.append(prod)
                        elif isinstance(prod, list):
                            # Если вложенный список — рекурсивно обрабатываем
                            for subprod in prod:
                                if isinstance(subprod, dict):
                                    prod_article = subprod.get('number') or subprod.get('article') or subprod.get('code') or subprod.get('numberFix')
                                    if prod_article:
                                        prod_article_norm = self._normalize_article(str(prod_article))
                                        if (
                                            prod_article_norm == normalized_article
                                            or normalized_article in prod_article_norm
                                            or prod_article_norm in normalized_article
                                        ):
                                            filtered_products.append(subprod)
                                    else:
                                        filtered_products.append(subprod)
                                else:
                                    filtered_products.append(subprod)
                        else:
                            filtered_products.append(prod)
                    print(f"[FILTER] После фильтрации: {len(filtered_products)} товаров")
                else:
                    print(f"[WARN] API вернул пустой или неуспешный ответ: {products}")
                # 2.3. Если после фильтрации есть товары — кешируем и возвращаем
                if filtered_products:
                    self.cache_manager.set_cache('search', supplier, params, filtered_products, 5)
                    print(f"[RESULT] Найдено товаров: {len(filtered_products)}. Кешировано.")
                    return filtered_products
                # 2.4. Если ничего не найдено — логируем подробно
                print(f"[NO-RESULT] Нет подходящих товаров у {supplier.name}. Ответ API: {products}")
            except Exception as e:
                print(f"[ERROR] Ошибка при запросе к API поставщика {supplier.name}: {e}")
        print(f"[NO-RESULT] Не найдено товаров по артикулу '{article}' и бренду '{brand}' через API всех поставщиков")
        return []

    def _search_analogs_smart(self, article, brand):
        params = {'article': article, 'brand': brand}
        for supplier in Supplier.objects.filter(is_active=True, api_type='autoparts'):
            cached = self.cache_manager.get_cached_result('analogs', supplier, params)
            if cached:
                return cached
        for supplier in Supplier.objects.filter(is_active=True, api_type='autoparts'):
            success, analogs = supplier.get_product_analogs(article, brand)
            if success and analogs:
                self.cache_manager.set_cache('analogs', supplier, params, analogs, 10)
                return analogs
        return []
