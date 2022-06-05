import json
import time

import hydralit_components as hc
import pandas as pd
import plotly.express as px
import snowflake.connector as sf
import streamlit as st
import yfinance as yf
from babel.numbers import format_currency
from openpyxl import Workbook, load_workbook
from streamlit_lottie import st_lottie
from yahooquery import Ticker

from functions import *


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


lottie_analysis = load_lottiefile("lottiefiles/analysis.json")
lottie_hello = load_lottiefile("lottiefiles/hello.json")

st.set_page_config(
    page_title="FA",
    page_icon="chart_with_upwards_trend",
    initial_sidebar_state="expanded"
)

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header{visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---Side-Bar----

with st.sidebar:
    st_lottie(lottie_hello, loop=True, key=None, height=320, width=320)
    st.write('''
    Hey 👋🏻there. I am Vidhya Varshany, a sophomore decision science student👩🏻. I enjoy working with data sets and extracting information from them, which qualifies me to be a data analyst🎯. My interests include Data Science and Data Analytics🎗️.

    To know more about me . Follow me on
    [LinkedIn](https://www.linkedin.com/in/vidhyavarshany/)

    [Twitter](https://twitter.com/vidhyavarshany)
    ''')
    st.write("---")
    st.write("#### About📍")
    st.write('''
    This Web App is based on the Beneish model, a mathematical model that uses financial ratios and eight variables to determine whether a company has manipulated earnings. Based on company financial statements, an M-Score is constructed to describe how much earnings have been manipulated.
    ''')

pd.set_option('mode.chained_assignment', None)

# Fetching the Tickers Module

symbols = ['FB', 'AAPL', 'BRK.B', 'TSLA', 'MCD', 'VZ', 'BA', 'NKE', '^GSPC', 'NQ=F', 'ALB', 'AOS', 'APPS', 'AQB', 'ASPN', 'ATHM', 'AZRE', 'BCYC', 'BGNE', 'CAT', 'CC', 'CLAR', 'CLCT', 'CMBM', 'CMT', 'CRDF', 'CYD', 'DE', 'DKNG', 'EMN', 'FBIO', 'FBRX', 'FCX', 'FLXS', 'FMC', 'FMCI', 'GME',
           'GRVY', 'HAIN', 'HBM', 'HIBB', 'IEX', 'IOR', 'GOOGL', 'MAXR', 'MPX', 'MRTX', 'NSTG', 'NVCR', 'NVO', 'OESX', 'PENN', 'PLL', 'PRTK', 'RDY', 'REGI', 'REKR', 'SBE', 'SQM', 'TCON', 'TWTR', 'TGB', 'TRIL', 'UEC', 'VCEL', 'VOXX', 'WIT', 'WKHS', 'XNCR']
# Create Ticker instance, passing symbols as first argument
# Optional asynchronous argument allows for asynchronous requests
tickers = Ticker(symbols, asynchronous=True)
dat = tickers.get_modules("summaryProfile quoteType")
symb = pd.DataFrame.from_dict(dat).T
# flatten dicts within each column, creating new dataframes
dataframes = [pd.json_normalize([x for x in symb[module] if isinstance(
    x, dict)]) for module in ['summaryProfile', 'quoteType']]
# concat dataframes from previous step
symb = pd.concat(dataframes, axis=1)
symb = symb[['shortName', 'symbol']].dropna()
symb = symb.sort_values('symbol')
symb.set_index('shortName', inplace=True, drop=True)
symb = symb.reset_index()  # reset index
symb.index = symb.index + 1  # add 1 to each index
symb.columns = ['Companies', 'Symbol']
data = symb.copy()

# !IMPORTANT
symb['Companies'] = symb['Companies'].str.replace("'", "''")

# -----Home Page-----

st.title("Analyzing the Quality of Financial Statements using Beneish Model")
with st.container():
    left_col, right_col = st.columns((2, 1))
    with left_col:
        st.dataframe(data)
    with right_col:
        st_lottie(lottie_analysis, height="300",
                  width="500", quality="high", key=None)
# -- Input----

ch = st.number_input(
    "\n\nEnter your choice from the above listed company: ", value=0)
if ch:

    comp = yf.Ticker(symb.at[ch, 'Symbol'])

    st.write(
        f" #### Company Name - {data.at[ch, 'Companies']}\n #### Symbol - {data.at[ch, 'Symbol']}")

    with hc.HyLoader('Now doing loading', hc.Loaders.standard_loaders, index=[3, 0, 5]):
        time.sleep(5)

    incomeStatement = comp.financials
    balanceSheet = comp.balancesheet
    cashFlow = comp.cashflow

    # Cleaning the data

    # Income Statement
    incomeStatement = incomeStatement[incomeStatement.columns[0:2]]
    incomeStatement.columns = ['2022', '2021']
    incomeStatement = incomeStatement.fillna(0).astype(float)

    # Balance Sheet
    balanceSheet = balanceSheet[balanceSheet.columns[0:2]]
    balanceSheet.columns = ['2022', '2021']
    balanceSheet = balanceSheet.fillna(0).astype(float)

    # Cash Flow
    cashFlow = cashFlow[cashFlow.columns[0:2]]
    cashFlow.columns = ['2022', '2021']
    cashFlow.dropna()

    # COGS = Revenue  - GrossProfit
    cogs22 = incomeStatement.at['Total Revenue', '2022'] - \
        incomeStatement.at['Gross Profit', '2022']
    cogs21 = incomeStatement.at['Total Revenue', '2021'] - \
        incomeStatement.at['Gross Profit', '2021']

    # COGS = pd.Series(data={'2022': cogs22, '2021': cogs21},
    #                  name='Cost of Goods Sold')
    incomeStatement.loc['Cost of Goods Sold'] = [cogs22, cogs21]

    # long term Debt

    if('Long Term Debt' not in balanceSheet.index):
        ld22 = balanceSheet.at['Total Liab', "2022"] - \
            balanceSheet.at['Total Current Liabilities', "2022"] - \
            balanceSheet.at['Other Liab', "2022"]
        ld21 = balanceSheet.at['Total Liab', "2021"] - \
            balanceSheet.at['Total Current Liabilities', "2021"] - \
            balanceSheet.at['Other Liab', "2021"]
        balanceSheet.loc['Long Term Debt'] = [ld22, ld21]

    if('Long Term Investments' not in balanceSheet.index):
        li22 = balanceSheet.at['Common Stock', "2022"] + \
            balanceSheet.at['Cash', "2022"]
        li21 = balanceSheet.at['Common Stock', "2021"] - \
            balanceSheet.at['Cash', "2021"]

        balanceSheet.loc['Long Term Investments'] = [li22, li21]

    # Extracting the statements

    df = incomeStatement.loc[["Total Revenue",
                              "Cost of Goods Sold", "Selling General Administrative", "Net Income From Continuing Ops"]]

    df2 = balanceSheet.loc[["Net Receivables",
                            "Total Current Assets", "Property Plant Equipment", "Long Term Investments", "Total Assets", "Total Current Liabilities", "Long Term Debt"]]
    df3 = cashFlow.loc[["Depreciation",
                        "Total Cash From Operating Activities"]]

    data = pd.concat([df, df2, df3])
    data = data.reindex(['Total Revenue', 'Cost of Goods Sold', 'Selling General Administrative', 'Depreciation', 'Net Income From Continuing Ops', 'Net Receivables', 'Total Current Assets',
                        'Property Plant Equipment', 'Long Term Investments', 'Total Assets', 'Total Current Liabilities', 'Long Term Debt', 'Total Cash From Operating Activities'])
    data.index = ["Revenue", "Cost of Goods Sold", "Selling, General & Admin.Expense", "Depreciation", "Net Income from Continuing Operations", "Accounts Receivables",
                  "Current Assets", "Property, Plant & Equipment", "Securities", "Total Assets", "Current Liabilities", "Total Long-term Debt", "Cash Flow from Operations"]

    data1 = data.copy()
    data1["2022"] = data1["2022"].apply(lambda x: format_currency(
        x, format=None, currency="USD", locale="en_US"))
    data1["2021"] = data1["2021"].apply(lambda x: format_currency(
        x, format=None, currency="USD", locale="en_US"))

    # Data Particulars

    st.subheader("Data Particulars")
    st.dataframe(data1)

    # for 1 (index=5) from the standard loader group
    with hc.HyLoader('Now doing loading', hc.Loaders.standard_loaders, index=5):
        time.sleep(5)

    data2 = {
        'Financial Ratios Indexes': [
            "Day Sales in Receivables Index(DSRI)",
            "Gross Margin Index(GMI)",
            "Asset Quality Index(AQI)",
            "Sales Growth Index(SGI)",
            "Depreciation Index(DEPI)",
            "Selling, General, & Admin. Expenses Index(SGAI)",
            "Leverage Index(LVGI)",
            "Total Accruals to Total Assets(TATA)"
        ],
        'Index': [
            DSRI(data),
            GMI(data),
            AQI(data),
            SGI(data),
            DEPI(data),
            SGAI(data),
            LVGI(data),
            TATA(data)
        ]
    }

    ratios = pd.DataFrame(data2)
    ratios.set_index('Financial Ratios Indexes', inplace=True, drop=True)

    # Financial Ratios

    st.write(" ### Financial Ratio Indexes")
    st.dataframe(ratios)
    # print(type(ratios["Index"]))
    temp_ratios = ratios.copy()
    temp_ratios.index.name = 'Ratios'
    temp_ratios['Ratios'] = temp_ratios.index
    temp_ratios = temp_ratios.reset_index(drop=True)
    temp_ratios.columns = ['Ratios', 'Index']

    # The Line Chart using Plotly
    fig = px.line(
        temp_ratios,  # Data Frame
        x="Index",  # Columns from the data frame
        y="Ratios",
        title="Financial Ratio Indexes",
    )
    fig.update_traces(line_color="blue")

    with st.container():
        st.plotly_chart(fig)

    # Beneish M Score
    m_score = BeneishMScore(DSRI(data),
                            GMI(data),
                            AQI(data),
                            SGI(data),
                            DEPI(data),
                            SGAI(data),
                            LVGI(data),
                            TATA(data))
    if(m_score < -2.22):
        res = '##### Company is not likely to manipulate their earnings'
        st.write(f"##### M- Score = {round(m_score,2)}")
        st.write(f"{res}")
        # print(res)
    else:
        res = " ##### Company is not likely to manipulate their earnings"
        st.write(f"##### M- Score = {round(m_score,2)}")
        st.write(f"{res}")

    # SnowFlake  Initialize connection.
    def init_connection():
        return sf.connect(**st.secrets["snowflake"])

    conn = init_connection()

    cur = conn.cursor()

    try:
        cur.execute(
            f"INSERT INTO FAR.PUBLIC.HISTORY(COMPANY,M_SCORE) VALUES('{symb.at[ch, 'Companies']}',{round(m_score,2)})")
        cur.execute('''DELETE FROM FAR.PUBLIC.HISTORY WHERE (COMPANY)  in 
        (SELECT COMPANY FROM FAR.PUBLIC.HISTORY GROUP BY COMPANY HAVING COUNT(COMPANY)> 1)
                    ''')
        cur.execute(
            'SELECT * FROM FAR.PUBLIC.HISTORY')
        history = cur.fetch_pandas_all()

    finally:
        cur.close()
        history.index = history.index + 1

    conn.close()

    if st.button("View History"):
        st.snow()
        st.dataframe(history)
