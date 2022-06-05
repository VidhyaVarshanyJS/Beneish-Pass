def DSRI(df):
    return (df.at["Accounts Receivables", "2022"] / df.at["Revenue", "2022"]) / (df.at["Accounts Receivables", "2021"] / df.at["Revenue", "2021"])


def GMI(df):
    return ((df.at["Revenue", "2021"] - df.at["Cost of Goods Sold", "2021"])/df.at["Revenue", "2021"]) / ((df.at["Revenue", "2022"] - df.at["Cost of Goods Sold", "2022"])/df.at["Revenue", "2022"])


def AQI(df):
    AQI_t1 = (1 - (df.at["Current Assets", "2022"] +
              df.at["Property, Plant & Equipment", "2022"]+df.at["Securities", "2022"])) / df.at["Total Assets", "2022"]
    AQI_t2 = (1 - (df.at["Current Assets", "2021"] +
              df.at["Property, Plant & Equipment", "2021"]+df.at["Securities", "2021"])) / df.at["Total Assets", "2021"]
    return AQI_t1 / AQI_t2


def SGI(df):
    return (df.at["Revenue", "2022"] / df.at["Revenue", "2021"])


def DEPI(df):
    DEPI_t1 = (df.at["Depreciation", "2021"] / (df.at["Depreciation",
               "2021"] + df.at["Property, Plant & Equipment", "2021"]))
    DEPI_t2 = (df.at["Depreciation", "2022"] / (df.at["Depreciation",
               "2022"] + df.at["Property, Plant & Equipment", "2022"]))
    return DEPI_t1 / DEPI_t2


def SGAI(df):
    return (df.at["Selling, General & Admin.Expense", "2022"] / df.at["Revenue", "2022"]) / (df.at["Selling, General & Admin.Expense", "2021"] / df.at["Revenue", "2021"])


def LVGI(df):
    return ((df.at["Current Liabilities", "2022"] + df.at["Total Long-term Debt", "2022"]) / df.at["Total Assets", "2022"]) / ((df.at["Current Liabilities", "2021"] + df.at["Total Long-term Debt", "2021"]) / df.at["Total Assets", "2021"])


def TATA(df):
    return (df.at["Net Income from Continuing Operations", "2022"] - df.at["Cash Flow from Operations", "2022"]) / df.at["Total Assets", "2022"]


def BeneishMScore(dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata):
    return -4.84+0.92*dsri+0.528*gmi+0.404*aqi+0.892*sgi+0.115*depi-0.172*sgai+4.679*tata-0.327*lvgi
