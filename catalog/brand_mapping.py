# Маппинг брендов для нормализации
# Формат: 'Бренд из Mikado': 'Бренд в AutoSputnik'

BRAND_MAPPING = {
    'ZIMMERMANN': 'Otto Zimmermann',
    'VICTOR REINZ': 'REINZ',
    'MANN': 'MANN-FILTER',
    'KNECHT': 'Knecht/Mahle',
    'MAHLE ORIGINAL': 'Knecht/Mahle',
    'FEBI BILSTEIN': 'FEBI',
    'CITROËN': 'CITROEN/PEUGEOT',
    'PEUGEOT': 'CITROEN/PEUGEOT',
    'FIAT': 'Fiat/Alfa/Lancia',
    'KIA HYUNDAI': 'HYUNDAI/KIA',
    'HYUNDAI': 'HYUNDAI/KIA',
    'KIA': 'HYUNDAI/KIA',
    'ZF PARTS': 'ZF PARTS',
    'ZF Parts': 'ZF PARTS',
    'ZF RUSSIA': 'ZF PARTS',
    '1-56 MARUICHI': '1-56',
    'ACDelco': 'AC Delco',
    'AVA QUALITY COOLING': 'AVA',
    'BASBUG': 'BSG',
    'CHINASPARE': 'CHINA',
    'DELTA': 'DELTA AUTOTECHNIK',
    'DOCTORWAX': 'DOCTOR WAX',
    'DPGroup': 'DP GROUP',
    'HALLA': 'HCC',
    'HANON': 'HANON SYSTEMS',
    'JAPANPARTS': 'JAPAN PARTS',
    'KYB': 'KAYABA',
    'LEMFÖRDER': 'LEMFORDER',
    'LESJÖFORS': 'LESJOFORS',
    'MAGTECHNIC': 'MAG',
    'MALÒ': 'MALO',
    'MEAT & DORIA': 'MEAT DORIA',
    'MENSAN': 'ASP',
    'MERCEDES-BENZ': 'MERCEDES',
    'MK Kashiyama': 'KASHIYAMA',
    'NEVSKY FILTER': 'НЕВСКИЙ ФИЛЬТР',
    'PHC Valeo': 'VALEO PHC',
    'PRO PARTS SWEDEN AB': 'PROPARTS',
    'R&A': 'HWASEUNG R&A',
    'REACH Cooling': 'REACH',
    'Rheinol': 'SWD RHEINOL',
    'ROADHOUSE': 'ROAD HOUSE',
    'S.H': 'SH AUTO PARTS',
    'SANGSIN BRAKE': 'SANGSIN',
    'SCT Germany': 'SCT',
    'STARTVOLT': 'СТАРТВОЛЬТ',
    'Teikoku Piston Ring': 'TP',
    'VMP': 'VMPAUTO'
}

def normalize_brand(brand_name: str) -> str:
    """
    Нормализует бренд к формату AutoSputnik
    """
    return BRAND_MAPPING.get(brand_name, brand_name)

def get_all_brand_variants() -> dict:
    """
    Возвращает все варианты брендов для поиска
    """
    return BRAND_MAPPING 