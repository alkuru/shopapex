import requests

API_URL = 'https://newapi.auto-sputnik.ru'
LOGIN = '89219520754'
PASSWORD = '89219520754'

def get_sputnik_token():
    """Получить токен для API АвтоСпутник. Возвращает строку токена или None."""
    url = f'{API_URL}/users/login'
    data = {'login': LOGIN, 'password': PASSWORD}
    try:
        resp = requests.post(url, json=data, timeout=10)
        resp.raise_for_status()
        token = resp.json().get('token')
        return token
    except Exception as e:
        print(f'Ошибка получения токена АвтоСпутник: {e}')
        return None

def get_sputnik_brands(articul):
    """Получить список брендов по артикулу через API АвтоСпутник."""
    token = get_sputnik_token()
    if not token:
        print('Не удалось получить токен для поиска брендов АвтоСпутник')
        return []
    url = f'{API_URL}/products/getbrands'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    params = {'articul': articul}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('data'):
            return [b['brand']['name'] for b in data['data'] if b.get('brand') and b['brand'].get('name')]
        return []
    except Exception as e:
        print(f'Ошибка получения брендов АвтоСпутник: {e}')
        return []

def get_sputnik_brands_full(articul):
    """Получить список брендов по артикулу с полями: бренд, артикул, наименование через API АвтоСпутник."""
    token = get_sputnik_token()
    if not token:
        print('Не удалось получить токен для поиска брендов АвтоСпутник')
        return []
    url = f'{API_URL}/products/getbrands'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    params = {'articul': articul}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('data'):
            return [
                {
                    'brand': b['brand']['name'] if b.get('brand') and b['brand'].get('name') else '',
                    'articul': b.get('articul', ''),
                    'name': b.get('name', '')
                }
                for b in data['data']
            ]
        return []
    except Exception as e:
        print(f'Ошибка получения брендов АвтоСпутник: {e}')
        return []

def search_sputnik_products(articul, brand):
    """Поиск товаров через API АвтоСпутник. Возвращает JSON или None."""
    token = get_sputnik_token()
    if not token:
        print('Не удалось получить токен для поиска АвтоСпутник')
        return None
    url = f'{API_URL}/products/getproducts'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {'articul': articul, 'brand': brand, 'analogi': True, 'tranzit': True}
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        j = resp.json()
        # Возвращаем сразу список товаров, чтобы дальше не городили огород
        return j.get('data', [])
    except Exception as e:
        print(f'Ошибка поиска АвтоСпутник: {e}')
        return []