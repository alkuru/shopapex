import pandas as pd

df = pd.read_excel('import/mikado_price_1.xlsx')
print(f'Всего строк в файле: {len(df)}')

# Считаем уникальные пары (brand, article)
df['brand'] = df['BrandName'].astype(str).str.strip()
df['article'] = df['Code'].astype(str).str.strip()
unique_pairs = df.drop_duplicates(subset=['brand', 'article'])
print(f'Уникальных пар (brand, article): {len(unique_pairs)}')

# Показываем примеры дубликатов
duplicates = df[df.duplicated(subset=['brand', 'article'], keep=False)]
if not duplicates.empty:
    print(f'Найдено дубликатов: {len(duplicates)}')
    print(duplicates[['brand', 'article', 'Prodname', 'PriceOut', 'QTY']].head(20).to_string())
else:
    print('Дубликатов не найдено.') 