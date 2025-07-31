import pandas as pd

df = pd.read_excel('import/mikado_price_1.xlsx')
print(f'Всего строк в файле: {len(df)}')

# Уникальные brand
unique_brands = df['BrandName'].astype(str).str.strip().nunique()
print(f'Уникальных брендов: {unique_brands}')

# Уникальные article
unique_articles = df['Code'].astype(str).str.strip().nunique()
print(f'Уникальных артикулов: {unique_articles}')

# Уникальные пары (brand, article)
df['brand'] = df['BrandName'].astype(str).str.strip()
df['article'] = df['Code'].astype(str).str.strip()
unique_pairs = df.drop_duplicates(subset=['brand', 'article'])
print(f'Уникальных пар (brand, article): {len(unique_pairs)}')

# Дубликаты по (brand, article)
duplicates = df[df.duplicated(subset=['brand', 'article'], keep=False)]
if not duplicates.empty:
    print(f'Найдено дубликатов: {len(duplicates)}')
    duplicates.to_excel('mikado_duplicates.xlsx', index=False)
    print('Все дубликаты выгружены в mikado_duplicates.xlsx')
else:
    print('Дубликатов не найдено.') 