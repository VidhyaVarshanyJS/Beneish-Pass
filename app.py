from fuzzywuzzy import process, fuzz
import json
import time
import random

from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
from streamlit_lottie import st_lottie
from yfin.quote_summary import QuoteSummary
from stocksymbol import StockSymbol
import hydralit_components as hc
import plotly.express as px
import streamlit as st
import duckdb
import pandas as pd
import numpy as np
from babel.numbers import format_currency
from functions import *

# pd.set_option('mode.chained_assignment', None)


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


lottie_analysis = load_lottiefile("lottiefiles/analysis.json")
lottie_hello = load_lottiefile("lottiefiles/hello.json")

st.set_page_config(
    page_title="Beneish Pass",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"

)


def show_loading_screen(time_delay):
    with hc.HyLoader('Loading 📈', hc.Loaders.standard_loaders, index=[3, 0, 5]):
        time.sleep(time_delay)
    # with st.spinner('Loading 📈'):
    #     time.sleep(time_delay)


def error_handle(company):
    try:
        symbol = symb.loc[symb['Companies'] == company, 'Symbol'].values[0]
    except IndexError:
        st.error("Select company!")
        st.stop()
    except KeyError:
        st.error("Company data not available")
    return symbol


def get_company_info(select_by, symb):
    if select_by == "Choose from Dropdown":
        company = st.selectbox('Select a company:', [
                               'Click here!'] + symb['Companies'].values.tolist())
        symbol = error_handle(company)
        show_loading_screen(3)

    elif select_by == "Random Company":
        company = random.choice(symb['Companies'].values)
        symbol = error_handle(company)
        show_loading_screen(3)
    elif select_by == "Enter Company Name":
        company_input = st.text_input('Enter a Company Name: ', '')
        if not company_input:
            st.error("Select company!")
            st.stop()
        choices = symb['Companies'].values.tolist()
        company, score = process.extractOne(
            company_input, choices, scorer=fuzz.token_sort_ratio)
        symbol = error_handle(company)
        show_loading_screen(3)

    return company, symbol


show_loading_screen(2)

ss = StockSymbol(st.secrets["api_key"])

symbol_list_in = ss.get_symbol_list(market="IN")
symb = pd.DataFrame.from_dict(symbol_list_in)[['longName', 'symbol']].rename(columns={
    'longName': 'Companies', 'symbol': 'Symbol'}).sort_values(by='Symbol')

# Remove rows with empty company names

symb['Companies'].replace('', np.nan, inplace=True)
symb.dropna(subset=['Companies'], inplace=True)

# Reset the index and update the index labels to start from 1
symb.reset_index(drop=True, inplace=True)
symb.index = symb.index + 1

# Assign the updated dataframe to a new variable called data
data = symb.copy()

# !IMPORTANT
# Replace single quotes with two single quotes to avoid SQL syntax errors
symb['Companies'] = symb['Companies'].str.replace("'", "''")

hide_st_style = f'''
<a href = "https://github.com/VidhyaVarshanyJS/Beneish-Pass" class = "github-corner" aria-label = "View source on GitHub" > <svg width = "80" height = "80" viewBox = "0 0 250 250" style = "fill:#b276f7; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden = "true" > <path d = "M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z" > </path > <path d = "M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill = "currentColor" style = "transform-origin: 130px 106px;" class = "octo-arm" > </path > <path d = "M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill = "currentColor" class = "octo-body" > </path > </svg > </a >
'''


st.markdown(hide_st_style, unsafe_allow_html=True)
# ---Side-Bar----
with st.sidebar:
    choose = option_menu('Beneish Pass', ["Detect Manipulation", "How it Works?", "About"],
                         icons=['bar-chart-line-fill', 'book', 'kanban',
                                'house', 'person lines fill'],
                         menu_icon="app-indicator", default_index=1
                         )
    st_lottie(lottie_analysis, quality="high", key=None)

st.write("## Analyze the Quality of Financial Statements")
# -----Home Page-----
if choose == "Detect Manipulation":
    show_loading_screen(3)
    with st.container():
        left_col, right_col = st.columns((2, 2))
        with left_col:
            # Show the list of companies on the left
            st.write("#### List of Companies")
            st.dataframe(data)

        with right_col:
            st.write("#### Select Company by")

            # Define the company selection radio options
            select_by = st.radio('None', [
                "Choose from Dropdown", "Random Company", "Enter Company Name"])

            company, symbol = get_company_info(select_by, symb)
            show_loading_screen(2)

    # Display the selected company name and symbol
    if company and symbol:
        # Get the QuoteSummary object for the selected company
        st.write(f"## {company} ({symbol})")
        comp = QuoteSummary(symbols=symbol)

    # Cleaning the data
        # - Transpose the DataFrame
        # - Select the first two columns (dated years -> 2022,2021)
        # - Rename the columns from 0 and 1 to (2022,2021)
        # - Remove the first row
        # - Fill NaN values with 0
        # - Format row index names (total_revenue -> Total Revenue)
        # - Do necessary explicit calculation with kebab case"""

    # Income Statement
    incomeStatement = pd.concat(comp.income_statement_history)
    incomeStatement = incomeStatement.transpose()
    incomeStatement = incomeStatement[incomeStatement.columns[0:2]]
    incomeStatement.columns = ['2022', '2021']
    incomeStatement = incomeStatement.iloc[1:]
    incomeStatement = incomeStatement.fillna(0)
    incomeStatement.index = incomeStatement.index.str.replace(
        '_', ' ').str.title()
    # Calculate the COGS
    cogs = incomeStatement.loc['Total Revenue'] - \
        incomeStatement.loc['Gross Profit']

    incomeStatement.loc['Cost of Goods Sold'] = cogs

    # Balance Sheet

    balanceSheet = pd.concat(comp.balance_sheet_history)
    balanceSheet = balanceSheet.transpose()
    balanceSheet = balanceSheet[balanceSheet.columns[0:2]]
    balanceSheet.columns = ['2022', '2021']
    balanceSheet = balanceSheet.iloc[1:]
    balanceSheet = balanceSheet.fillna(0)
    balanceSheet.index = balanceSheet.index.str.replace(
        '_', ' ').str.title()

    # long term Debt
    if 'Long Term Debt' not in balanceSheet.index:
        try:
            ld = balanceSheet['Total Liab'] - \
                balanceSheet['Total Current Liabilities'] - \
                balanceSheet['Other Liab']
        except KeyError:
            # Handle the KeyError exception by assigning 0 to the missing keys
            total_liab = balanceSheet.get('Total Liab', 0)
            other_liab = balanceSheet.get('Other Liab', 0)
            total_curr_liab = balanceSheet.get(
                'Total Current Liabilities', 0)

            ld = total_liab - \
                total_curr_liab - \
                other_liab
        balanceSheet.loc['Long Term Debt'] = ld

    if ('Long Term Investments' not in balanceSheet.index):
        try:
            li = balanceSheet['Common Stock'] + \
                balanceSheet['Cash']
        except KeyError:
            c_stock = balanceSheet.get('Common Stock', 0)
            cash = balanceSheet.get('Cash', 0)
            li = c_stock + cash

        balanceSheet.loc['Long Term Investments'] = li

    # Cash Flow

    cashFlow = pd.concat(comp.cashflow_statement_history)
    cashFlow = cashFlow.transpose()
    cashFlow = cashFlow.iloc[:, :2]
    cashFlow.columns = ['2022', '2021']
    cashFlow = cashFlow.iloc[1:]
    cashFlow = cashFlow.fillna(0)
    cashFlow.index = cashFlow.index.str.replace('_', ' ').str.title()

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
    show_loading_screen(3)

    st.subheader("Data Particulars")
    st.dataframe(data1)

    # # for 1 (index=5) from the standard loader group
    # with hc.HyLoader('Now doing loading', hc.Loaders.standard_loaders, index=5):
    #     time.sleep(5)

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
    ratios.set_index('Financial Ratios Indexes',
                     inplace=True, drop=True)

    # Financial Ratios
    show_loading_screen(2)

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
    status = "The company can be a manipulator."
    if np.isnan(m_score):
        st.error("Insufficient Data")
        st.stop()

    if (m_score < -2.22):
        res = '##### Company is not likely to manipulate their earnings'
        st.write(f"##### M- Score = {round(m_score,2)}")
        st.write(f"{res}")
        status = "The company is not a manipulator."
    else:
        res = " ##### Company is likely to manipulate their earnings"
        st.write(f"##### M- Score = {round(m_score,2)}")
        st.write(f"{res}")

        # create a connection to your DuckDB database
    conn = duckdb.connect('m_score_history.db')

    # create the m_score_history table if it doesn't already exist
    conn.execute(
        "CREATE TABLE IF NOT EXISTS m_score_history (company VARCHAR, m_score DECIMAL(10,2), status VARCHAR)")

    # insert the data into the m_score_history table and remove any duplicates
    try:
        conn.execute("INSERT INTO m_score_history (company, m_score, status) VALUES (?, ?, ?)",
                     (company, m_score, status))
        conn.execute(
            "DELETE FROM m_score_history WHERE rowid NOT IN (SELECT MIN(rowid) FROM m_score_history GROUP BY company)")
        # get the history data from the m_score_history table
        history = conn.execute("SELECT * FROM m_score_history").fetchdf()
        # Rename the columns with first letter capitalized
        history = history.rename(columns=lambda x: x.capitalize())
        # set the index of the DataFrame to the company column
        history = history.set_index('Company')
        # add 1 to the index of the DataFrame to match the index in the original code
        # history.index = history.index + 1
    finally:
        # close the connection to the database
        conn.close()

    if st.button("View History"):
        show_loading_screen(5)
        st.dataframe(history)
        st.snow()


elif choose == "How it Works?":
    show_loading_screen(5)
    st.write('''
             
    ### Working
        - This app retrieves financial data for companies listed in the Indian stock market using the Yahoo Finance API and the StockSymbol API.
        - It uses the Beneish model to analyze the quality of financial statements and calculate the likelihood of earnings manipulation.
        - The Beneish model uses financial ratios to identify red flags for earnings manipulation.
        - The app displays financial statements (income statement, balance sheet, and cash flow statement) for the selected company, along with calculated financial ratios.)
        - Users can select a company from the list of available companies, or enter a company name in the input field.
        - If the entered company name is not found, the app prompts the user to select a random company or view the list of available companies.
        - Finally M-Score is calculated and the company's manipulation status is identified.


    ### Tech Stack Used:
    - Programming Language - Python 🐍
    - Framework - Streamlit 💗
          📂𝗰𝘂𝘀𝘁𝗼𝗺 𝗰𝗼𝗺𝗽𝗼𝗻𝗲𝗻𝘁𝘀 - hydralit_components ✨
    - Data Analysis - Pandas 🐼
    - Visualization- Plotly 📌
    - Animations - Lottie Files 📍
    - Asynchronous Automation- openpyxl (Python ->Excel) 📊

    ## Upgrades

    ### June,2022:

    Features:
    - User can enter the number of the company by looking the dataframe
    - Limited Companies (<=70)

    Supporting Tools
    - Data Source - yfinance (API), yahooquery 📉
    - DataBase - Snowflakes ❄️

    ### Dec, 2022
    
     Supporting Tools
    - DataBase - MySQL (online db)
    
    ### 18,19 March,2023
    
    Supporting Tools:
    - Data Source - yfin (beta) for the financial statements ,StockSymbol API
    - Database -  duckdb 🦆
    - Fuzzywuzzy package to match company name input 
    - GitHub corners 
    
    Features:
    - Added 3 different ways to choose for companies implemented fuzzy algo
    - Design Modification of streamlit (use streamlit-option-menu) - attach github corners
    - Loading Animations of Hydralit Components update
    - Bug fixes (Fixing the yfinance module Exception: yfinance failed to decrypt Yahoo data response )
    - Complete Code base revamped
    
    ''')

elif choose == 'About':
    show_loading_screen(3)
    st_lottie(lottie_hello, loop=True, key=None, height=290, width=290)
    st.write('''
    Hey 👋🏻there. I am Vidhya Varshany, a Junior decision science student👩🏻. I enjoy working with data sets and extracting information from them, which qualifies me to be a data analyst🎯. My interests include Data Science and Data Analytics🎗️.
    To know more about me...
    Follow me on
    
    [LinkedIn](https://www.linkedin.com/in/vidhyavarshany/)\n
    [Twitter](https://twitter.com/vidhyavarshany)
    ''')

    st.write("---")
    st.write("#### About Beneish Pass📍")
    st.write('''
    This Web App is based on the Beneish model, a mathematical model that uses financial ratios and eight variables to determine whether a company has manipulated earnings. Based on company financial statements, an M-Score is constructed to describe how much earnings have been manipulated.
    ''')

# elif choose == "Comment":
#     show_loading_screen(3)
#     st_disqus("streamlit-disqus-demo")
