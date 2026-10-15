"""python -m unittest -v. No notebook execution or network required."""
from pathlib import Path
import unittest
import pandas as pd
from analytics import clean_data,filter_data,group_summary,product_summary,keyword_summary,audit_sheets,safe_share

ROOT=Path(__file__).parent

class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=pd.read_csv(ROOT/'data/source_sheet2.csv')
        cls.df=clean_data(cls.raw)

    def test_source_totals(self):
        self.assertEqual(len(self.df),3692)
        self.assertEqual(self.df['Sales Quantity'].sum(),623125)
        self.assertEqual(self.df['Sales Revenue'].sum(),90804526236)
        self.assertEqual(self.df.URL.nunique(),3690)

    def test_no_silent_removal(self):
        self.assertEqual(self.df['Sales Quantity'].eq(0).sum(),983)
        self.assertEqual(self.df.URL.duplicated().sum(),2)
        self.assertEqual(self.df['Seller Type'].unique().tolist(),['Official Store'])

    def test_notebook_leader(self):
        top=group_summary(self.df,'Brand').sort_values('Units',ascending=False).iloc[0]
        self.assertEqual(top.Brand,'Scarlett')
        self.assertEqual(top.Units,124437)

    def test_aggregate_reconciliation(self):
        for group in ['Brand','Seller Name','Location']:
            t=group_summary(self.df,group)
            self.assertEqual(t.Units.sum(),self.df['Sales Quantity'].sum())
            self.assertEqual(t.Revenue.sum(),self.df['Sales Revenue'].sum())
        self.assertEqual(product_summary(self.df).Units.sum(),623125)

    def test_filter_combinations(self):
        d=filter_data(self.df,brands=['Scarlett'],locations=['Kota Jakarta Barat'],active=True,min_units=100)
        self.assertGreater(len(d),0)
        self.assertTrue(d.Brand.eq('Scarlett').all())
        self.assertTrue(d.Location.eq('Kota Jakarta Barat').all())
        self.assertTrue(d['Sales Quantity'].ge(100).all())
        self.assertEqual(len(filter_data(self.df)),3692)

    def test_literal_search_and_empty(self):
        self.assertEqual(len(filter_data(self.df,query='not-a-real-product-923845')),0)
        a=filter_data(self.df,query='[')
        self.assertTrue(a['Product Title'].str.contains('[',regex=False).all() if len(a) else True)

    def test_keyword_multilabel(self):
        k=keyword_summary(self.df)
        self.assertGreater(k.loc[k.Keyword.eq('Niacinamide'),'Units'].iloc[0],0)
        self.assertEqual(len(k),8)
        self.assertTrue(k.Listings.le(self.df.URL.nunique()).all())

    def test_zero_handling(self):
        self.assertEqual(safe_share(0,0),0)
        self.assertTrue(self.df.loc[self.df['Sales Quantity'].eq(0),'Revenue per Unit'].isna().all())

    def test_validation(self):
        with self.assertRaises(ValueError):clean_data(self.raw.drop(columns='Brand'))
        x=self.raw.head(1).copy();x.loc[x.index[0],'Sales Quantity']=-1
        with self.assertRaises(ValueError):clean_data(x)
        x['Sales Quantity']=1.5
        with self.assertRaises(ValueError):clean_data(x)

    def test_audit(self):
        audit=audit_sheets(pd.read_csv(ROOT/'data/source_sheet1.csv'),self.raw)
        self.assertEqual(audit['shared_unique_urls'],3690)
        self.assertEqual(audit['quantity_mismatches'],2329)
        self.assertEqual(audit['revenue_mismatches'],2700)

class AppTests(unittest.TestCase):
    def test_interactions(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.tabs),6)
        app.selectbox[0].set_value('Omzet tercatat').run()
        self.assertEqual(len(app.exception),0)
        app.multiselect[0].set_value(['Scarlett']).run()
        self.assertEqual(len(app.exception),0)
        app.toggle[0].set_value(True).run()
        self.assertEqual(len(app.exception),0)
        app.number_input[0].set_value(100).run()
        self.assertEqual(len(app.exception),0)
        app.text_input[0].set_value('not-a-real-product-923845').run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('Tidak ada data' in x.value for x in app.warning))
        app.text_input[0].set_value('[').run()
        self.assertEqual(len(app.exception),0)

    def test_zero_only_brand(self):
        from streamlit.testing.v1 import AppTest
        d=clean_data(pd.read_csv(ROOT/'data/source_sheet2.csv'))
        zero=group_summary(d,'Brand').query('Units==0').iloc[0].Brand
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()
        app.multiselect[0].set_value([zero]).run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('Belum ada penjualan' in x.value for x in app.markdown))

if __name__=='__main__':unittest.main()
