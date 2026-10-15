from pathlib import Path
import html
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from analytics import clean_data,filter_data,group_summary,product_summary,keyword_summary,safe_share

st.set_page_config(page_title='Beauty Studio · Serum Market Intelligence',page_icon='◈',layout='wide')
ROOT=Path(__file__).parent
TEAL,CORAL,LILAC,GOLD='#0F8F84','#E8A293','#A495CD','#D9B869'
COLORS=[TEAL,CORAL,LILAC,GOLD,'#7EA5CE','#8ABEB2','#C7B9A8','#C6D8E4']
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,.stApp{font-family:'DM Sans',sans-serif;}
.block-container{padding-top:2.5rem;padding-bottom:2.5rem;max-width:1600px;}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #E5EBEE;}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.04em;}
h1{font-size:2.5rem!important;font-weight:800!important;line-height:1.2!important;}
h3{font-size:1.05rem!important;}
.brand{font:800 26px 'Manrope',sans-serif;letter-spacing:-1px;color:#1B3940;}.brand span{color:#0F8F84;}
.eyebrow{font-size:10px;letter-spacing:2px;font-weight:700;color:#8D9CA5;}
.pill{display:inline-block;border-radius:40px;background:#E8F4F1;border:1px solid #CCE6DE;padding:6px 12px;color:#0B7F72;font-size:10px;letter-spacing:.8px;font-weight:700;}
.hero{padding:25px 30px;margin:17px 0 22px;background:linear-gradient(115deg,#183F42,#216761);border-radius:20px;color:#fff;position:relative;overflow:hidden;}
.hero:after{content:'◌';position:absolute;right:25px;top:-60px;font-size:225px;color:#FFFFFF12;pointer-events:none;}
.hero .eyebrow{color:#A5CFC4;}.hero-title{font:700 23px 'Manrope',sans-serif;letter-spacing:-.5px;margin:8px 0;}.hero p{color:#D0E4DD;font-size:12px;margin:0;}
.kpi{padding:21px;background:#fff;border:1px solid #E4EBEE;border-radius:16px;min-height:149px;border-top:3px solid #0F8F84;}
.kpi-label{font-size:11px;color:#718591;margin-bottom:12px;}.kpi-value{font:800 clamp(22px,2.3vw,34px) 'Manrope',sans-serif;letter-spacing:-1px;color:#1D3A44;}.kpi-note{font-size:10px;color:#8D9CA6;margin-top:12px;}
.section{font-size:9px;font-weight:700;letter-spacing:1.7px;color:#899AA6;margin-top:5px;margin-bottom:4px;}
.insight{background:#EDF6F3;border-left:3px solid #0F8F84;border-radius:0 13px 13px 0;padding:16px 18px;font-size:13px;color:#28534F;margin:9px 0;}
.mini{font-size:12px;color:#82939C;}
[data-testid="stTabs"]{margin-top:23px;}
button[data-baseweb="tab"]{font-size:12px;padding:12px 14px;}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-radius:16px!important;}
.foot{font-size:10px;color:#93A1AA;padding-top:18px;margin-top:22px;border-top:1px solid #E2E9ED;}
@media(max-width:760px){.block-container{padding:1.4rem 1rem;}h1{font-size:1.8rem!important;}.hero{padding:20px;}.kpi{min-height:130px;}}
</style>''',unsafe_allow_html=True)

def rp(x,short=True):
    x=float(x)
    if short and abs(x)>=1e9:return f'Rp{x/1e9:,.2f} M'.replace(',', '_').replace('.',',').replace('_','.')
    if short and abs(x)>=1e6:return f'Rp{x/1e6:,.1f} jt'.replace(',', '_').replace('.',',').replace('_','.')
    if short and abs(x)>=1e3:return f'Rp{x/1e3:,.1f} rb'.replace(',', '_').replace('.',',').replace('_','.')
    return 'Rp'+f'{x:,.0f}'.replace(',','.')

def num(x):return f'{int(x):,}'.replace(',','.')
def esc(x):return html.escape(str(x))

@st.cache_data
def load():
    raw=pd.read_csv(ROOT/'data/source_sheet2.csv')
    return clean_data(raw),json.loads((ROOT/'data/metadata.json').read_text())

def style(fig,height=340):
    fig.update_layout(height=height,margin=dict(l=10,r=18,t=15,b=12),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        colorway=COLORS,font=dict(family='DM Sans, sans-serif',size=11,color='#758995'),
        showlegend=False)
    fig.update_xaxes(showgrid=False,zeroline=False,title=None)
    fig.update_yaxes(gridcolor='#EEF2F4',zeroline=False,title=None)
    return fig

def chart(fig,key):
    st.plotly_chart(fig,width='stretch',theme=None,key=key,config={'displayModeBar':False,'responsive':True})

def heading(kicker,title):
    st.markdown(f'<div class="section">{esc(kicker)}</div>',unsafe_allow_html=True)
    st.subheader(title)

def bars(data,label,value,key,color=TEAL,n=10,height=350):
    d=data.nlargest(n,value).sort_values(value)
    # Use numeric y coordinates to keep distinct rows if display labels repeat.
    fig=go.Figure(go.Bar(x=d[value],y=list(range(len(d))),orientation='h',marker_color=color,
        customdata=d[label].astype(str),hovertemplate='%{customdata}<br>%{x:,.0f}<extra></extra>'))
    style(fig,height).update_yaxes(tickmode='array',tickvals=list(range(len(d))),
        ticktext=[str(x)[:37]+'…' if len(str(x))>37 else str(x) for x in d[label]],showgrid=False)
    chart(fig,key)

def export_table(df,key,filename):
    st.download_button('↓ Unduh CSV',df.to_csv(index=False).encode('utf-8-sig'),filename,'text/csv',key=key)

try:df,meta=load()
except (OSError,ValueError) as e:
    st.error(f'Data tidak dapat dimuat: {e}. Pastikan seluruh isi ZIP diekstrak.');st.stop()

with st.sidebar:
    st.markdown('<div class="brand"><span>◈</span> beauty studio</div><div class="eyebrow">SERUM MARKET INTELLIGENCE</div>',unsafe_allow_html=True)
    st.divider()
    st.caption('WORKSPACE / ABAY')
    st.markdown('### Your market, in focus.')
    st.caption('Pilihan kosong = semua. Filter berlaku pada seluruh analisis, kecuali audit sumber.')
    brands=st.multiselect('Brand',sorted(df.Brand.unique()),placeholder='Semua brand')
    locations=st.multiselect('Lokasi seller',sorted(df.Location.unique()),placeholder='Semua lokasi')
    sellers=st.multiselect('Seller',sorted(df['Seller Name'].unique()),placeholder='Semua seller')
    query=st.text_input('Cari produk / brand',placeholder='Niacinamide, Scarlett, acne…')
    active=st.toggle('Hanya baris dengan penjualan',False)
    min_units=st.number_input('Minimum unit per baris',min_value=0,max_value=int(df['Sales Quantity'].max()),value=0,step=10)
    metric_label=st.selectbox('Ukuran peringkat',['Unit terjual','Omzet tercatat'])
    top_n=st.select_slider('Jumlah peringkat',options=[5,10,15,20],value=10)
    st.divider()
    st.markdown('<span class="pill">● NOTEBOOK-BASED ANALYSIS</span>',unsafe_allow_html=True)
    st.caption('Shopee · 1–31 Agustus\n\nTahun tidak tercantum.\n\nSnapshot agregat, bukan transaksi harian.')
    st.caption('Sumber analisis: Sheet2\n\nSemua baris berlabel Official Store.')

cur=filter_data(df,brands,locations,sellers,active,query,int(min_units))
metric='Units' if metric_label=='Unit terjual' else 'Revenue'
other='Revenue' if metric=='Units' else 'Units'
total_units=int(cur['Sales Quantity'].sum());total_revenue=float(cur['Sales Revenue'].sum())
base_units=int(df['Sales Quantity'].sum())
top,badge=st.columns([4,1])
with top:
    st.markdown('<div class="eyebrow">BEAUTY COMMERCE / MARKET OVERVIEW</div>',unsafe_allow_html=True)
    st.title('The beauty of better insights.')
    st.caption('Lihat pemimpin pasar, produk unggulan, dan pola seller dari analisis serum wajah Shopee.')
with badge:st.markdown('<br><span class="pill">◈ LIGHT / INTELLIGENCE</span>',unsafe_allow_html=True)
st.caption('Snapshot 1–31 Agustus · Tahun tidak tersedia · Rupiah (IDR) · Bukan data real-time')
if cur.empty:
    st.warning('Tidak ada data untuk kombinasi filter ini. Hapus pencarian atau longgarkan filter di sidebar.');st.stop()

brand=group_summary(cur,'Brand').sort_values(metric,ascending=False)
product=product_summary(cur)
seller=group_summary(cur,'Seller Name')
location=group_summary(cur,'Location')
total_metric=brand[metric].sum()
leader=brand.iloc[0]
lead_share=safe_share(leader[metric],total_metric)
hero_title=f'{esc(leader.Brand)} memimpin {lead_share:.1%} {"unit" if metric=="Units" else "omzet"} dalam pilihan ini.' if total_metric else 'Belum ada penjualan tercatat pada pilihan ini.'
st.markdown(f'<div class="hero"><div class="eyebrow">THE MARKET AT A GLANCE</div><div class="hero-title">{hero_title}</div><p>{num(cur.Brand.nunique())} brand · {num(cur.URL.nunique())} listing unik · {num(cur["Seller Name"].nunique())} seller · {num(cur.Location.nunique())} lokasi seller</p></div>',unsafe_allow_html=True)
cards=[('Omzet tercatat',rp(total_revenue),'Penjumlahan Sales Revenue; bukan laba'),
       ('Unit terjual',num(total_units),'Jumlah unit; bukan jumlah pesanan'),
       ('Listing unik',num(cur.URL.nunique()),f'{num(len(cur))} baris; dihitung dari URL unik'),
       ('Brand teramati',num(cur.Brand.nunique()),f'{num(cur["Seller Name"].nunique())} seller pada filter aktif')]
for col,(label,value,note) in zip(st.columns(4),cards):
    col.markdown(f'<div class="kpi"><div class="kpi-label">{esc(label)}</div><div class="kpi-value">{esc(value)}</div><div class="kpi-note">{esc(note)}</div></div>',unsafe_allow_html=True)
st.caption(f'Filter mencakup {safe_share(total_units,base_units):.1%} unit dataset penuh. Semua nilai mengikuti Sheet2; ada ketidaksesuaian antar-sheet dan 2 URL konflik. Lihat Data & Metodologi sebelum menarik keputusan bisnis.')

overview,brand_tab,product_tab,seller_tab,explore,data_tab=st.tabs(['01  Ringkasan','02  Brand landscape','03  Product explorer','04  Seller & lokasi','05  Eksplorasi','06  Data & metodologi'])

with overview:
    a,b=st.columns([1.65,1])
    with a,st.container(border=True):
        heading('BRAND LEADERBOARD',f'Top {min(top_n,len(brand))} brand · {metric_label.lower()}')
        bars(brand,'Brand',metric,'overview-brand',n=top_n,height=370)
    with b,st.container(border=True):
        heading('MARKET CONCENTRATION','Seberapa terkonsentrasi pasar ini?')
        mix=brand.head(4)[['Brand',metric]].copy()
        if len(brand)>4:mix.loc[len(mix)]=['Brand lainnya',brand.iloc[4:][metric].sum()]
        if total_metric>0:
            fig=go.Figure(go.Pie(labels=mix.Brand,values=mix[metric],hole=.75,sort=False,textinfo='none',marker=dict(colors=COLORS,line=dict(color='white',width=4)),hovertemplate='%{label}<br>%{percent}<br>%{value:,.0f}<extra></extra>'))
            style(fig,315).update_layout(showlegend=True,legend=dict(orientation='h',x=.5,xanchor='center',y=-.05,font=dict(size=10)),annotations=[dict(text=f'<b>{safe_share(brand.head(3)[metric].sum(),total_metric):.0%}</b><br>Top 3 brand',x=.5,y=.5,showarrow=False,font=dict(size=20,color='#21434A'))])
            chart(fig,'market-mix')
        else:st.info('Tidak ada nilai positif untuk komposisi pada pilihan ini.')
        st.caption('Pangsa hanya dalam dataset/filter ini, bukan seluruh pasar Shopee.')
    a,b=st.columns([1.65,1])
    with a,st.container(border=True):
        heading('PRODUCT SPOTLIGHT','Produk yang paling menonjol')
        bars(product,'Product Title',metric,'overview-product',color=CORAL,n=5,height=310)
        st.caption('Agregasi judul produk + brand; bukan pemadanan SKU lintas seller.')
    with b,st.container(border=True):
        heading('PORTFOLIO HEALTH','Aktivitas dalam snapshot')
        sold=int(cur['Sales Quantity'].gt(0).sum());zero=int(cur['Sales Quantity'].eq(0).sum())
        fig=go.Figure(go.Bar(x=[sold,zero],y=['Dengan penjualan','Tanpa penjualan'],orientation='h',marker_color=[TEAL,'#DDE8E6'],text=[num(sold),num(zero)],textposition='auto'))
        chart(style(fig,215),'activity')
        st.caption(f'{safe_share(zero,len(cur)):.1%} baris memiliki 0 unit pada snapshot. Tidak berarti stok habis atau produknya gagal.')
        st.markdown(f'<div class="insight">Top 10 brand menyumbang <b>{safe_share(brand.head(10)[metric].sum(),total_metric):.1%}</b> {"unit" if metric=="Units" else "omzet"} pada filter ini.</div>',unsafe_allow_html=True)

with brand_tab:
    heading('COMPETITIVE LANDSCAPE','Volume tinggi belum tentu omzet tertinggi.')
    a,b=st.columns([1.4,1])
    with a,st.container(border=True):
        st.subheader('Unit × omzet per brand')
        positive=brand.loc[brand.Units.gt(0)&brand.Revenue.gt(0)]
        if not positive.empty:
            fig=px.scatter(positive,x='Units',y='Revenue',size='Listings',hover_name='Brand',color_discrete_sequence=[TEAL],size_max=40,opacity=.7,hover_data=['Listings'])
            style(fig,370).update_xaxes(type='log',title='Unit terjual · log')
            fig.update_yaxes(type='log',title='Omzet tercatat (Rp) · log')
            chart(fig,'brand-scatter')
        else:st.info('Tidak ada brand dengan unit dan omzet positif.')
        st.caption('Ukuran titik = listing URL unik. Sumbu log membantu membaca perbedaan skala; hubungan bukan bukti sebab-akibat.')
    with b,st.container(border=True):
        st.subheader('Peringkat volume vs omzet')
        ranks=brand.copy()
        ranks['Rank unit']=ranks.Units.rank(method='min',ascending=False).astype(int)
        ranks['Rank omzet']=ranks.Revenue.rank(method='min',ascending=False).astype(int)
        ranks['Selisih rank']=ranks['Rank unit']-ranks['Rank omzet']
        st.dataframe(ranks.head(top_n)[['Brand','Rank unit','Rank omzet','Selisih rank']],hide_index=True,width='stretch',height=370)
        st.caption('Selisih positif: posisi omzet lebih tinggi daripada posisi unit. Ranking tie menggunakan posisi minimum.')
    with st.container(border=True):
        st.subheader('Pareto kontribusi brand')
        pareto=brand.head(top_n).copy()
        pareto['Cumulative']=brand[metric].cumsum().head(top_n).div(total_metric if total_metric else 1)*100
        fig=go.Figure(go.Bar(x=pareto.Brand,y=pareto[metric],name=metric_label,marker_color=TEAL))
        fig.add_trace(go.Scatter(x=pareto.Brand,y=pareto.Cumulative,name='Kontribusi kumulatif',yaxis='y2',line=dict(color=CORAL,width=3),mode='lines+markers',hovertemplate='%{x}<br>%{y:.1f}% kumulatif<extra></extra>'))
        style(fig,330).update_layout(showlegend=True,legend=dict(orientation='h',y=1.14),yaxis2=dict(overlaying='y',side='right',range=[0,105],ticksuffix='%',showgrid=False))
        chart(fig,'pareto')
        st.caption('Persentase kumulatif memakai seluruh brand pada filter sebagai penyebut, bukan hanya bar yang ditampilkan.')
    with st.expander('Tabel seluruh brand & ekspor'):
        st.dataframe(brand,hide_index=True,width='stretch')
        export_table(brand,'export-brands','beauty-brand-summary.csv')

with product_tab:
    heading('PRODUCT DISCOVERY','Jelajahi produk, bukan sekadar peringkat.')
    st.caption('Pencarian utama ada di sidebar. Gunakan judul + brand untuk menelusuri produk, lalu bandingkan unit dan omzet.')
    bars(product,'Product Title',metric,'products-top',color=CORAL,n=top_n,height=max(330,top_n*27))
    st.dataframe(product.sort_values(metric,ascending=False),hide_index=True,width='stretch',
        column_config={'Product Title':st.column_config.TextColumn('Nama produk',width='large'),'Units':'Unit terjual','Revenue':st.column_config.NumberColumn('Omzet (Rp)',format='Rp %.0f'),'Listings':'Listing unik','Sellers':'Seller unik'})
    export_table(product.sort_values(metric,ascending=False),'export-products','beauty-product-summary.csv')
    with st.expander('Telusuri listing sumber & buka tautannya'):
        st.caption('Tautan berasal dari dataset historis; listing mungkin berubah atau tidak aktif. URL konflik tetap dipertahankan sesuai sumber.')
        st.dataframe(cur[['Product Title','Brand','Seller Name','Sales Quantity','Sales Revenue','URL']].sort_values('Sales Quantity',ascending=False),hide_index=True,width='stretch',column_config={'URL':st.column_config.LinkColumn('Sumber listing',display_text='Buka Shopee')})

with seller_tab:
    heading('CHANNEL & GEOGRAPHY','Seller mana yang mendorong penjualan?')
    st.info('Seluruh baris sumber berlabel Official Store. Perbandingan official vs non-official tidak tersedia; label toko dipakai sebagaimana tercatat, bukan verifikasi status toko saat ini.')
    a,b=st.columns([1.2,1])
    with a,st.container(border=True):
        st.subheader(f'Top {min(top_n,len(seller))} seller')
        bars(seller,'Seller Name',metric,'top-seller',n=top_n,height=360)
    with b,st.container(border=True):
        st.subheader('Lokasi seller teratas')
        bars(location,'Location',metric,'top-location',color=LILAC,n=min(8,top_n),height=360)
        st.caption('Lokasi adalah lokasi seller, bukan domisili pembeli, alamat pengiriman, atau ukuran permintaan kota.')
    with st.container(border=True):
        st.subheader('Jejak brand × lokasi seller')
        names=brand.head(min(10,top_n)).Brand
        locs=location.nlargest(8,metric).Location
        valcol='Sales Quantity' if metric=='Units' else 'Sales Revenue'
        heat=cur.loc[cur.Brand.isin(names)&cur.Location.isin(locs)].pivot_table(index='Brand',columns='Location',values=valcol,aggfunc='sum',fill_value=0).reindex(index=names,columns=locs,fill_value=0)
        fig=go.Figure(go.Heatmap(z=heat.values,x=heat.columns,y=heat.index,colorscale=[[0,'#F0F6F4'],[.4,'#8CCBBF'],[1,TEAL]],xgap=4,ygap=4,colorbar=dict(thickness=10),hovertemplate='%{y}<br>%{x}<br>%{z:,.0f}<extra></extra>'))
        style(fig,400).update_yaxes(showgrid=False,autorange='reversed')
        fig.update_xaxes(tickangle=-22)
        chart(fig,'brand-location')
    a,b=st.columns(2)
    with a:export_table(seller.sort_values(metric,ascending=False),'export-sellers','beauty-seller-summary.csv')
    with b:export_table(location.sort_values(metric,ascending=False),'export-location','beauty-location-summary.csv')

with explore:
    heading('SIGNALS, NOT CERTAINTIES','Eksplorasi untuk memulai pertanyaan yang lebih baik.')
    st.caption('Indikasi eksploratif dari judul produk; bukan penilaian efektivitas, keamanan, komposisi terverifikasi, atau rekomendasi formulasi skincare.')
    a,b=st.columns([1.2,1])
    kw=keyword_summary(cur)
    with a,st.container(border=True):
        st.subheader('Sinyal kata kunci dalam judul')
        bars(kw,'Keyword',metric,'keywords',color=LILAC,n=len(kw),height=345)
        st.caption('Satu listing bisa cocok dengan beberapa kata kunci: kategori tumpang tindih dan tidak boleh dijumlahkan sebagai total pasar.')
    with b,st.container(border=True):
        st.subheader('Kedalaman distribusi unit per baris')
        bins=pd.cut(cur['Sales Quantity'],bins=[-1,0,10,100,1000,float('inf')],labels=['0 unit','1–10','11–100','101–1.000','>1.000'])
        dist=bins.value_counts(sort=False).reset_index()
        dist.columns=['Rentang','Baris']
        fig=px.bar(dist,x='Rentang',y='Baris',color_discrete_sequence=[TEAL],text='Baris')
        chart(style(fig,345),'units-distribution')
        st.caption('Distribusi baris data, bukan pelanggan atau jumlah pesanan.')
    top_product=product.sort_values(metric,ascending=False).iloc[0]
    if total_metric:
        st.markdown(f'<div class="insight"><b>Benchmark produk:</b> {esc(top_product["Product Title"])} ({esc(top_product.Brand)}) berada di urutan pertama pada ukuran {esc(metric_label.lower())} untuk filter ini. Jadikan bahan riset pesaing, bukan bukti penyebab keberhasilannya.</div>',unsafe_allow_html=True)
    else:
        st.info('Tidak ada penjualan untuk menentukan benchmark produk pada pilihan ini.')
    a,b=st.columns(2)
    with a,st.container(border=True):
        st.subheader('Hipotesis yang bisa diuji berikutnya')
        st.markdown('1. Bandingkan penawaran, ukuran kemasan, dan promosi produk teratas menggunakan data listing yang telah diverifikasi.\n2. Tambahkan data non-official sebelum menilai perbedaan kanal.\n3. Tambahkan data tanggal, harga aktual, dan biaya iklan sebelum mengevaluasi pertumbuhan, harga, atau profit.')
    with b,st.container(border=True):
        st.subheader('Yang belum bisa dijawab dataset ini')
        st.markdown('- Tren harian/bulanan dan pertumbuhan periode.\n- Conversion rate, jumlah pembeli, repeat purchase.\n- Efektivitas skincare, margin, atau ROI iklan.\n- Pangsa seluruh Shopee atau permintaan berdasarkan kota pembeli.')
    with st.expander('Rasio omzet per unit — hanya untuk audit eksploratif'):
        st.warning('Revenue / Quantity bukan harga jual listing. Ketidaksesuaian antar-sheet dan nilai ekstrem membuat rasio ini tidak layak langsung dijadikan rekomendasi harga.')
        ratios=cur.loc[cur['Sales Quantity'].gt(0),['Product Title','Brand','Sales Quantity','Sales Revenue','Revenue per Unit']].sort_values('Revenue per Unit',ascending=False)
        st.dataframe(ratios,hide_index=True,width='stretch',column_config={'Revenue per Unit':st.column_config.NumberColumn('Rasio omzet/unit (Rp)',format='Rp %.0f')})

with data_tab:
    heading('TRUST & TRANSPARENCY','Kenali datanya sebelum mengambil keputusan.')
    st.caption('Audit di bagian ini selalu memakai sumber lengkap, tidak mengikuti filter sidebar. Tabel data dan ekspor di bawah tetap mengikuti filter.')
    st.warning('Dua sheet tidak identik pada tingkat URL. Sheet2 dipakai agar konsisten dengan notebook, bukan karena akurasinya telah terbukti. Verifikasi ke sumber awal sebelum keputusan komersial.')
    a,b,c,d=st.columns(4)
    a.metric('Baris sumber',num(meta['sheet2_rows']))
    b.metric('URL unik',num(meta['sheet2_unique_urls']))
    c.metric('Baris 0 unit',num(meta['zero_unit_rows']))
    d.metric('URL konflik',num(meta['duplicate_url_extra_rows']))
    checks=pd.DataFrame([
        ['Missing cells',num(meta['missing_cells']),'Tidak ada sel kosong di CSV sumber'],
        ['Duplikat persis',num(meta['sheet2_exact_duplicates']),'Tidak ada penghapusan baris'],
        ['URL bersama antar-sheet',num(meta['shared_unique_urls']),'Audit memakai kemunculan pertama per URL'],
        ['Kuantitas berbeda antar-sheet',num(meta['quantity_mismatches']),'Jumlah URL yang nilainya berbeda'],
        ['Omzet berbeda antar-sheet',num(meta['revenue_mismatches']),'Jumlah URL yang nilainya berbeda'],
        ['Label Seller Type','Official Store saja','Tidak ada kelompok non-official untuk dibandingkan'],
    ],columns=['Pemeriksaan','Hasil','Catatan'])
    st.dataframe(checks,hide_index=True,width='stretch')
    with st.expander('Dua URL berulang dengan brand/angka berbeda',expanded=False):
        conflicts=df.loc[df.URL.duplicated(keep=False),['Product Title','Brand','Seller Name','Sales Quantity','Sales Revenue','URL']]
        st.dataframe(conflicts,hide_index=True,width='stretch')
        st.caption('Keempat baris dipertahankan mengikuti notebook. Menjumlahkan angka belum menyelesaikan ketidakpastian identitas/duplikasi; jangan menganggap koreksi telah dilakukan.')
    with st.expander('Definisi metrik dan batas interpretasi',expanded=False):
        st.markdown('''
**Unit terjual:** jumlah Sales Quantity. Bukan invoice atau pesanan. **Omzet tercatat:** jumlah Sales Revenue, tanpa mengasumsikan biaya, pajak, retur, atau laba. **Listing unik:** jumlah URL unik. **Produk:** judul + brand; tidak mengklaim SKU sudah disatukan lintas seller.

**Filter:** brand, lokasi seller, seller, pencarian judul/brand, hanya penjualan positif, dan minimum unit per baris. Top N hanya mengubah jumlah peringkat, bukan filter data. Pilihan multiselect kosong berarti semua. Peringkat bisa berdasarkan unit atau omzet; kartu KPI tidak berubah definisinya.

**Waktu:** nama file menyebut 1–31 Agustus, tetapi tahun dan tanggal per baris tidak tersedia. Tidak membuat timeline atau angka pertumbuhan buatan.

**Transformasi:** trim teks, ubah lokasi menjadi title case, cast kuantitas menjadi integer setelah validasi. Tidak menghapus 0 unit, menyamakan brand secara spekulatif, menyatukan dua sheet, mengoreksi nilai ekstrem, atau membuang URL konflik. Toggle penjualan positif hanya memfilter tampilan.

**Sampling & status:** cakupan dan metode pengumpulan tidak dijelaskan pada notebook. Seluruh baris berlabel Official Store; tidak memverifikasi status toko/tautan saat ini. Pangsa hanya mewakili sumber/filter, bukan pasar Shopee keseluruhan.

**Kata kunci:** pencocokan regex pada judul, multi-label. Judul promosi tidak membuktikan kandungan, efek, keamanan atau sebab penjualan.
''')
    with st.expander('Sumber & reproduksibilitas'):
        st.markdown('Notebook pengguna: `Data_Analysis_Beauty_Product (1).ipynb`. Dashboard mengikuti pemilihan Sheet2 pada notebook, dengan analisis ulang dari baris sumber.')
        for i,url in enumerate(meta['source_urls'],1):st.markdown(f'[CSV sumber Sheet{i}]({url})')
        st.caption(f'Salinan sumber diambil {meta["downloaded_at"]}. Tidak ada data sintetis. {meta["license"]}')
        st.json(meta['sha256'])
    st.subheader('Data terfilter')
    st.caption(f'{num(len(cur))} baris mengikuti sidebar. File sumber lengkap ada di folder data; rasio tambahan pada tabel dihitung, bukan kolom sumber.')
    st.dataframe(cur,hide_index=True,width='stretch',height=380)
    export_table(cur,'export-filtered','beauty-filtered-data.csv')

st.markdown('<div class="foot">◈ BEAUTY STUDIO &nbsp; / &nbsp; Designed for clarity. Built for curiosity. &nbsp; · &nbsp; Shopee serum snapshot · IDR · Sheet2</div>',unsafe_allow_html=True)
