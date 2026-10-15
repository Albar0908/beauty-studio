"""Deterministic analysis of the notebook's Sheet2, with no invented dates."""
import pandas as pd

TEXT_COLUMNS = ['Product Title','URL','Brand','Seller Name','Marketplace','Seller Type','Location']
MEASURES = ['Sales Quantity','Sales Revenue']

def clean_data(raw):
    missing = set(TEXT_COLUMNS + MEASURES) - set(raw.columns)
    if missing:
        raise ValueError(f'Kolom wajib tidak ada: {sorted(missing)}')
    df = raw[TEXT_COLUMNS + MEASURES].copy()
    for col in TEXT_COLUMNS:
        df[col] = df[col].astype('string').fillna('Tidak diketahui').str.strip()
    for col in MEASURES:
        df[col] = pd.to_numeric(df[col], errors='raise')
        if df[col].isna().any() or df[col].lt(0).any():
            raise ValueError(f'{col} mengandung nilai kosong atau negatif')
    if (df['Sales Quantity'] % 1).ne(0).any():
        raise ValueError('Sales Quantity harus unit bulat, bukan pecahan')
    df['Sales Quantity'] = df['Sales Quantity'].astype('int64')
    df['Location'] = df.Location.str.title()
    # Ratio is only an exploration aid, NOT an observed selling price.
    df['Revenue per Unit'] = df['Sales Revenue'].div(df['Sales Quantity'].replace(0,float('nan')))
    return df

def filter_data(df, brands=(), locations=(), sellers=(), active=False, query='', min_units=0):
    mask = pd.Series(True,index=df.index)
    for col, selected in [('Brand',brands),('Location',locations),('Seller Name',sellers)]:
        if selected:
            mask &= df[col].isin(selected)
    if active:
        mask &= df['Sales Quantity'].gt(0)
    mask &= df['Sales Quantity'].ge(min_units)
    if query:
        mask &= df['Product Title'].str.contains(query,case=False,regex=False) | df.Brand.str.contains(query,case=False,regex=False)
    return df.loc[mask].copy()

def group_summary(df, column):
    return df.groupby(column,as_index=False).agg(
        Units=('Sales Quantity','sum'), Revenue=('Sales Revenue','sum'),
        Listings=('URL','nunique'), Rows=('URL','size'))

def product_summary(df):
    return df.groupby(['Product Title','Brand'],as_index=False).agg(
        Units=('Sales Quantity','sum'),Revenue=('Sales Revenue','sum'),
        Listings=('URL','nunique'),Sellers=('Seller Name','nunique'))

def safe_share(value,total):
    return float(value)/float(total) if total else 0.0

def audit_sheets(a,b):
    # URL deduplication here is only for auditing the two files, never analysis.
    x=a.drop_duplicates('URL').set_index('URL')
    y=b.drop_duplicates('URL').set_index('URL')
    shared=x.index.intersection(y.index)
    return dict(shared_unique_urls=len(shared),
        quantity_mismatches=int((pd.to_numeric(x.loc[shared,'Unnamed: 9'])!=pd.to_numeric(y.loc[shared,'Sales Quantity'])).sum()),
        revenue_mismatches=int((pd.to_numeric(x.loc[shared,'Unnamed: 11'])!=pd.to_numeric(y.loc[shared,'Sales Revenue'])).sum()),
        sheet2_rows=len(b),sheet2_unique_urls=b.URL.nunique(),
        sheet2_exact_duplicates=int(b.duplicated().sum()),
        duplicate_url_extra_rows=int(b.URL.duplicated().sum()),
        missing_cells=int(b.isna().sum().sum()),
        zero_unit_rows=int(b['Sales Quantity'].eq(0).sum()),
        seller_types=b['Seller Type'].value_counts().to_dict())

KEYWORDS = {
    'Niacinamide':r'niacinamide', 'Vitamin C':r'vitamin\s*c|ascorb',
    'Hyaluronic':r'hyaluronic|hyaluron', 'Retinol':r'retinol|retinoid|retinal',
    'Ceramide':r'ceramide|inoceramide', 'Acne':r'acne|jerawat',
    'Brightening':r'bright|whiten|lighten', 'Hydrating':r'hydrat|moistur',
}

def keyword_summary(df):
    rows=[]
    for label,pattern in KEYWORDS.items():
        d=df.loc[df['Product Title'].str.contains(pattern,case=False,regex=True)]
        rows.append(dict(Keyword=label,Units=int(d['Sales Quantity'].sum()),
            Revenue=float(d['Sales Revenue'].sum()),Listings=d.URL.nunique()))
    return pd.DataFrame(rows)

