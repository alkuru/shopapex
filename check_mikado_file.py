import pandas as pd

df = pd.read_excel('import/mikado_price_1.xlsx')
print(f'Всего строк в файле: {len(df)}')

filtered = df[df['Code'].notnull() & df['BrandName'].notnull() & (df['Code'].astype(str).str.strip() != '') & (df['BrandName'].astype(str).str.strip() != '')]
print(f'Строк с непустыми Code и BrandName: {len(filtered)}')
print('Первые 10 строк:')
print(filtered.head(10).to_string()) 