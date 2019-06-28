from pathlib import Path

"""
    link for browser: https://www.finam.ru/profile/akcii-usa-bats/3m-co/export/?market=25&em=18090&code=MMM&apply=0&df=1&mf=3&yf=2019&from=01.04.2019&dt=2&mt=3&yt=2019&to=02.04.2019&p=1&f=MMM_190401_190402&e=.csv&cn=MMM&dtf=1&tmf=1&MSOR=1&mstime=on&mstimever=1&sep=1&sep2=1&datf=6&at=1
    1 param {}.csv -  is filename
    2 param market={} - is market code
    3 param em={} - is em code it's value from instruments
    4 param df={} -  is today day of the month for data FROM
    5 param mf={} - is number of the today month -1 - for example for May the number is 4, not 5 FROM
    6 param yf={} - is year for data FROM
    7 param from={} - data FROM like 11.05.2017
    8 param dt={} - is today day of the month
    9 param mt={} - is number of the today month -1 - for example for May the number is 4, not 5
    10 param yt={} - is current year - for example 2019
    11 param is today data like 11.05.2019
    12 param p={} is time code. im my case are 8 for day period or 7 for hours period. there are not magic number - are finam req.
    13 param is filename again
"""

quotes_str = "http://export.finam.ru/{}.csv?market={}&em={}&code=&apply=0&df={}&mf={}&yf={}&from={}&dt={}&" \
             "mt={}&yt={}&to={}&p={}&f={}&e=.csv&cn=&dtf=1&tmf=4&MSOR=1&mstimever=0&sep=5&sep2=1&datf=5&at=1"

periods = {'_HOUR': 7, '_DAY': 8}

market_codes = {
    'indexes': 6,
    'stocks': 25,
    'usa industry': 27,
    'etf': 28,
    'currency': 5,
    'goods': 24
}

goods = {
    # 'brent': 19473
    # 'gold': 18953
}

# market code - 27
usa_industry = {
    'Automobiles & Parts': 18981,
    'Banks': 18992,
    'Basic Materials': 18975,
    'Chemicals': 18976,
    'Construction & Materials': 18978,
    'Consumer Goods': 18980,
    'Consumer Services': 18985,
    'Financial Services': 18994,
    'Financials': 18991,
    'Food & Beverage': 18982,
    'Health Care': 18984,
    'Industrial Goods & Services': 18979,
    'Industrials': 18977,
    'Insurance': 18993,
    'Media': 18987,
    'Oil & Gas': 18974,
    'Personal & Household Goods': 18983,
    'Retail': 18986,
    'Technology': 18995,
    'Telecommunications': 18989,
    'Travel & Leisure': 18988,
    'Utilities': 18990
}

# market code - 6
index_instruments = {
    'DJ-IND': 91
    # 'NASDAQ100': 82074,
    # 'NASDAQCOMP': 82075,
    # 'SHANGHAI': 19101,
    # 'N225JAP': 19063,
    # 'SANDP-500': 90
}

# market code - 25
stocks_instruments = {
    '3M co': 18090,
    'AMZN': 874205,
    'AT&T Inc': 19067,
    'Activision Blizzard Inc': 488996,
    'Adobe Systems Inc.': 20563,
    'Alcoa Inc': 17997,
    'Alphabet Inc.': 20590,
    'American Express': 18009,
    'American Intl Group Inc': 19070,
    'American Tower Corp. Cl A': 20568,
    'Apple Inc.': 20569,
    # 'Applied Materials Inc.': 20570,
    # 'Aqua America Inc': 489003,
    # 'Arista Networks Inc': 489023,
    'Bank of America': 18011,
    'Best Buy Co Inc': 489018,
    'Boeing Co': 18010,
    'CONSOL Energy Inc': 489015,
    'Caterpillar Inc': 18026,
    # 'Check Point Software Technolog': 488997,
    'Chevron': 18037,
    'Cisco Systems Inc.': 20580,
    'Citigroup Inc': 18023,
    'Coca-Cola co': 18076,
    # 'Corning Inc.': 20582,
    'Cummins Inc': 489019,
    # 'Dana Inc': 489014,
    # 'Direxion Daily 20 Year Plus Tr': 489033,
    # 'Discover Financial Services': 489013,
    # 'ETFMG Prime Cyber Security ETF': 489048,
    # 'ETFS Physical Palladium Shares': 489031,
    # 'ETFS Physical Platinum Shares': 489046,
    # 'Eaton Corp PLC': 489011,
    # 'Exelon Corp': 489012,
    'Exxon Mobil': 18149,
    # 'First Solar Inc.': 20586,
    'FaceBook': 874399,
    'Ford Motor Co': 489022,
    'GE': 18055,
    # 'Gilead Sciences Inc': 488994,
    # 'Global X Silver Miners ETF': 489039,
    'Goldman Sachs Group Inc': 472568,
    # 'Guggenheim China Technology ET': 489034,
    # 'HCA Healthcare Inc': 489027,
    'Hewlett-Packard': 18068,
    'Home Depot': 18063,
    'Horizon Pharma Plc': 489025,
    'IBM': 18069,
    # 'Int.Paper': 22141,
    'Intel Corp': 19069,
    'JPMorgan Chase&Co': 18074,
    # 'Jacobs Engineering Group Inc': 489009,
    'Johnson &amp; Johnson': 18073,
    # 'Juniper Networks Inc': 489021,
    # 'KKR &Co LP': 489008,
    # 'KraneShares CSI China Internet': 489035,
    # 'Lockheed Martin Corp': 489010,
    'Mastercard Inc': 489007,
    'McDonalds': 18080,
    # 'Medtronic PLC': 489017,
    # 'Merck &Co': 18094,
    # 'Micron Technology Inc': 489000,
    'Microsoft Corp': 19068,
    'NVIDIA Corp': 489001,
    # 'NextEra Energy Inc': 489006,
    # 'Norfolk Southern Corp': 489020,
    # 'Ormat Technologies Inc': 489016,
    # 'Palo Alto Networks Inc': 489024,
    # 'Pattern Energy Group Inc': 489026,
    # 'Pfizer Inc': 18106,
    # 'PowerShares Water Resources Po': 489032,
    'Procter&Gamble': 18107,
    # 'PureFunds ISE Junior Silver Sm': 489040,
    # 'ROBO Global Robotics and Autom': 489036,
    # 'Royal Caribbean Cruises Ltd': 489005,
    # 'SPDR Bloomberg Barclays Conver': 489041,
    'Starbucks Corp': 488995,
    # 'Travelers Comp.': 22139,
    # 'United Technologies': 18134,
    # 'Valero Energy Corp': 489004,
    # 'VanEck Vectors Gold Miners ETF': 489045,
    # 'VanEck Vectors Investment Grad': 489043,
    # 'Verisk Analytics Inc': 489002,
    'Verizon Communications': 18137,
    'Wal-Mart Stores': 18146,
    'Walt Disney': 18041,
    'Wells Fargo': 22138
}

# market code - 28
etf = {
    'Americas Basic Materials Index': 19513,
    'Americas Consumer Services Index': 19536,
    'Americas Utilities Index': 19561,
    'Asia Pacific - Ex. Japan Basic Materials Index': 19511,
    'Asia Pacific - Ex. Japan Consumer Goods Index': 19531,
    'Asia Pacific - Ex. Japan Consumer Services Index': 19530,
    'Asia Pacific - Ex. Japan Financials Index': 19501,
    'Asia Pacific - Ex. Japan Industrials Index': 19518,
    'Asia Pacific - Ex. Japan Technology Index': 19551,
    'Asia Pacific - Ex. Japan Telecommunications Index': 19543,
    'Asia Pacific - Ex. Japan Utilities Index': 19559,
    'Asia Pacific Basic Materials Index': 19510,
    'Asia Pacific Construction & Materials Index': 19509,
    'Asia Pacific Consumer Services Index': 19528,
    'Asia Pacific Utilities Index': 19558,
    'Australia Index': 19496,
    'Australian Dollar Trust': 19148,
    'Brazil Index': 19494,
    'British Pound Sterling Trust': 19149,
    'CBN China 600 Index': 19485,
    'CBN China Financial Services Blue-Chip Index': 19506,
    'CBN China Industrial Goods & Services Blue-Chip Index': 19523,
    'CBN China Technology Blue-Chip Index': 19555,
    'CBN China Utilities Blue-Chip Index': 19563,
    'Canada Index': 19493,
    'Canadian Dollar Trust': 19150,
    'Euro Trust': 19113,
    'Europe - Ex. U.K. Consumer Goods Index': 19535,
    'Europe - Ex. U.K. Consumer Services Index': 19534,
    'Europe - Ex. U.K. Financials Index': 19503,
    'Europe - Ex. U.K. Industrials Index': 19520,
    'Europe - Ex. U.K. Telecommunications Index': 19545,
    'Europe Basic Materials Index': 19512,
    'Europe Consumer Services Index': 19532,
    'Europe Utilities Index': 19560,
    'FTSE Xinhua China 25 I': 19122,
    'France Index': 19489,
    'Germany Index': 19490,
    'Hong Kong Index': 19483,
    'Italy Index': 19484,
    'Japan Index': 19492,
    'Japanese Yen Trust': 19114,
    'Latin America 40 Index': 19140,
    'MSCI Australia Index Fund': 19118,
    'MSCI Austria Index Fund': 19136,
    'MSCI Belgium Index Fund': 19134,
    'MSCI Brazil Index Fund': 19138,
    'MSCI France Index Fund': 19131,
    'MSCI Germany Index Fund': 19128,
    'MSCI Hong Kong Index Fund': 19124,
    'MSCI Italy Index Fund': 19133,
    'MSCI Japan Index Fund': 19121,
    'MSCI Malaysia Index Fund': 19127,
    'MSCI Mexico Index Fund': 19139,
    'MSCI Netherlands Index': 19137,
    'MSCI Pacific ex-Japan': 19119,
    'MSCI Singapore Index Fund': 19125,
    'MSCI South Korea Index': 19126,
    'MSCI Spain Index Fund': 19135,
    'MSCI Sweden Index Fund': 19130,
    'MSCI Switzerland Index': 19132,
    'MSCI Taiwan Index Fund': 19123,
    'MSCI United Kingdom Index': 19129,
    'Malaysia Index': 19487,
    'Mexico Index': 19497,
    'S&P 500 Index Fund': 19117,
    'S&P TOPIX 150 Index Fund': 19120,
    'Singapore Index': 19482,
    'South Korea Index': 19491,
    'Spain Index': 19486,
    'Swiss Franc Trust': 19153,
    'Taiwan Index': 19495,
    'U.K. Index': 19488,
    'World - Ex. U.S. Basic Materials Index': 19508,
    'World - Ex. U.S. Consumer Goods Index': 19527,
    'World - Ex. U.S. Consumer Services Index': 19525,
    'World - Ex. U.S. Financials Index': 19499,
    'World - Ex. U.S. Industrials Index': 19516,
    'World - Ex. U.S. Technology Index': 19549,
    'World - Ex. U.S. Telecommunications Index': 19541,
    'World - Ex. U.S. Utilities Index': 19557,
    'World Basic Materials Index': 19507,
    'World Consumer Services Index': 19524,
    'World Utilities Index': 19556,
    'iShares Barclays 1-3 Year Treasury Bond': 19111,
    'iShares Barclays 20+ Year Treasury Bond': 19112,
    'streetTRACKS Gold Trust': 19115
}

currency = {
    'Aud/Cad': 181410,
    'Aud/Chf': 181411,
    'Aud/Jpy': 181408,
    'Aud/Nzd': 181409,
    'Aud/Usd': 66699,
    'Cad/Chf': 181389,
    'Cad/Jpy': 181390,
    'Chf/Jpy': 21084,
    'Eur/Aud': 181414,
    'Eur/Cad': 181413,
    'Eur/Chf': 106,
    'Eur/Gbp': 88,
    'Eur/Jpy': 84,
    'Gbp/Aud': 181412,
    'Gbp/Cad': 181388,
    'Gbp/Chf': 181387,
    'Gbp/Jpy': 181386,
    'Gbp/Usd': 86,
    'Nzd/Cad': 181392,
    'Nzd/Jpy': 181391,
    'Nzd/Usd': 181425,
    'Usd/Cad': 66700,
    'Usd/Chf': 85,
    'Usd/Jpy': 87
}


parameters_wma = {
    'Usd/Jpy': {'week': (22, 95, 113), 'day': (19, 68, 80), '4 hours': (10, 38, 176)},
    'Usd/Chf': {'week': (22, 32, 98), 'day': (25, 26, 68), '4 hours': (25, 32, 128)},
    'Usd/Cad': {'week': (10, 20, 113), 'day': (28, 86, 191), '4 hours': (10, 20, 50)},
    'Nzd/Usd': {'week': (13, 68, 71), 'day': (25, 44, 53), '4 hours': (13, 41, 152)},
    'Nzd/Jpy': {'week': (13, 20, 83), 'day': (10, 23, 89), '4 hours': (10, 32, 80)},
    'Nzd/Cad': {'week': (13, 23, 92), 'day': (13, 35, 83), '4 hours': (25, 32, 161)},
    'Gbp/Usd': {'week': (10, 47, 68), 'day': (13, 74, 107), '4 hours': (25, 32, 185)},
    'Gbp/Jpy': {'week': (19, 44, 50), 'day': (28, 83, 176), '4 hours': (28, 41, 164)},
    'Gbp/Chf': {'week': (13, 47, 74), 'day': (22, 26, 191), '4 hours': (28, 41, 65)},
    'Gbp/Cad': {'week': (25, 29, 65), 'day': (28, 71, 83), '4 hours': (10, 50, 56)},
    'Gbp/Aud': {'week': (16, 26, 50), 'day': (13, 20, 80), '4 hours': (10, 77, 197)},
    'Eur/Jpy': {'week': (13, 41, 95), 'day': (13, 20, 179), '4 hours': (13, 62, 65)},
    'Eur/Aud': {'week': (19, 41, 113), 'day': (13, 20, 56), '4 hours': (25, 47, 170)},
    'Eur/Gbp': {'week': (25, 26, 125), 'day': (25, 95, 191), '4 hours': (19, 20, 92)},
    'Eur/Chf': {'week': (19, 26, 50), 'day': (10, 44, 197), '4 hours': (25, 62, 137)},
    'Eur/Cad': {'week': (16, 47, 53), 'day': (19, 23, 80), '4 hours': (10, 20, 50)},
    'Chf/Jpy': {'week': (19, 26, 110), 'day': (25, 29, 185), '4 hours': (10, 50, 191)},
    'Cad/Jpy': {'week': (10, 20, 89), 'day': (28, 77, 125), '4 hours': (25, 29, 65)},
    'Cad/Chf': {'week': (25, 47, 50), 'day': (19, 20, 59), '4 hours': (25, 83, 110)},
    'Aud/Usd': {'week': (10, 26, 92), 'day': (22, 50, 167), '4 hours': (13, 23, 149)},
    'Aud/Cad': {'week': (16, 38, 53), 'day': (13, 26, 179), '4 hours': (16, 41, 167)},
    'Aud/Chf': {'week': (13, 38, 89), 'day': (22, 65, 167), '4 hours': (25, 68, 179)},
    'Aud/Jpy': {'week': (19, 35, 62), 'day': (16, 95, 137), '4 hours': (16, 74, 176)},
    'Aud/Nzd': {'week': (22, 29, 95), 'day': (19, 86, 122), '4 hours': (16, 26, 167)},
    'Wells Fargo': {'week': (10, 23, 128), 'day': (25, 29, 86), '4 hours': (25, 98, 194),
    'Wal-Mart Stores': {'week': (10, 41, 74), 'day': (16, 98, 194), '4 hours': (19, 65, 86)},
    'Walt Disney': {'week': (13, 41, 164), 'day': (10, 44, 77), '4 hours': (25, 29, 77)},
    'McDonalds': {'week': (19, 56, 71), 'day': (19, 32, 89), '4 hours': (28, 86, 197)},
    'Citigroup Inc': {'week': (25, 56, 62), 'day': (16, 95, 110), '4 hours': (25, 71, 131)},
    'Caterpillar Inc': {'week': (28, 38, 53), 'day': (10, 77, 182), '4 hours': (25, 38, 191)},
    'American Express': {'week': (25, 47, 50), 'day': (16, 56, 80), '4 hours': (13, 65, 104)},
    'Apple Inc.': {'week': (19, 53, 71), 'day': (28, 29, 194), '4 hours': (25, 32, 176)},
    'GE': {'week': (25, 29, 65), 'day': (28, 50, 176), '4 hours': (10, 92, 155)},
    'FaceBook': {'week': (25, 98, 110), 'day': (25, 89, 92), '4 hours': (19, 20, 176)},
    'Ford Motor Co': {'week': (13, 20, 146), 'day': (22, 29, 53), '4 hours': (10, 98, 194)},
    'Goldman Sachs Group Inc': {'week': (13, 26, 143), 'day': (22, 62, 143), '4 hours': (25, 95, 143)},
    'Procter&Gamble': {'week': (16, 23, 122), 'day': (25, 71, 116), '4 hours': (22, 86, 122)},
    'Home Depot': {'week': (25, 56, 71), 'day': (28, 77, 194), '4 hours': (10, 62, 113)},
    'Intel Corp': {'week': (25, 89, 104), 'day': (25, 86, 125), '4 hours': (22, 74, 98)},
    'Cisco Systems Inc.': {'week': (22, 41, 86), 'day': (22, 32, 101), '4 hours': (10, 47, 122)},
    'IBM': {'week': (13, 47, 128), 'day': (22, 59, 68), '4 hours': (19, 59, 188)},
    'AT&T Inc': {'week': (10, 59, 71), 'day': (28, 83, 173), '4 hours': (10, 29, 170)},
    'Johnson &amp; Johnson': {'week': (28, 71, 86), 'day': (28, 35, 50), '4 hours': (19, 44, 59)},
    'JPMorgan Chase&Co': {'week': (19, 38, 56), 'day': (13, 83, 116), '4 hours': (13, 20, 50)},
    'Coca-Cola co': {'week': (25, 47, 119), 'day': (19, 20, 167), '4 hours': (13, 68, 74)},
    'Mastercard Inc': {'week': (10, 29, 50), 'day': (13, 65, 68), '4 hours': (10, 80, 158)},
    'AMZN': {'week': (28, 59, 71), 'day': (16, 53, 62), '4 hours': (19, 47, 113)},
    'Alcoa Inc': {'week': (16, 26, 98), 'day': (28, 68, 167), '4 hours': (22, 77, 197)},
    'Verizon Communications': {'week': (16, 56, 71), 'day': (28, 80, 185), '4 hours': (19, 68, 185)},
    'Boeing Co': {'week': (28, 50, 59), 'day': (10, 35, 59), '4 hours': (13, 56, 170)},
    'Bank of America': {'week': (28, 53, 95), 'day': (10, 56, 68), '4 hours': (28, 44, 89)},
    'DJ-IND': {'week': (10, 44, 53), 'day': (10, 62, 173), '4 hours': (19, 59, 113)},
    'Alphabet Inc.': {'week': (25, 44, 62), 'day': (28, 38, 194), '4 hours': (25, 83, 164)},
    'Microsoft Corp': {'week': (22, 44, 50), 'day': (28, 68, 119), '4 hours': (28, 77, 83)},
    'Hewlett-Packard': {'week': (22, 53, 59), 'day': (22, 65, 197), '4 hours': (13, 38, 62)},
    'NVIDIA Corp': {'week': (22, 38, 53), 'day': (25, 32, 143), '4 hours': (28, 35, 140)},
    'Starbucks Corp': {'week': (28, 68, 131), 'day': (28, 53, 194), '4 hours': (16, 86, 179)}}
}

UPLOAD_FOLDER = ""
if str(Path.home()) != '/root':
    UPLOAD_FOLDER = str(Path.home()) + '/dq'
else:
    UPLOAD_FOLDER = '/dq'

# here is i have added all instruments to one dict
stock_instruments = {}
stock_instruments.update(stocks_instruments)
stock_instruments.update(index_instruments)

goods_instrument = {}
# goods_instrument.update(goods)

all_instruments = {}
all_instruments.update(stock_instruments)
all_instruments.update(currency)
# all_instruments.update(goods_instrument)


def init():
    global database_uploaded
    database_uploaded = False
    global result_currency
    result_currency = list()
    global result_stocks
    result_stocks = list()
