import talib
import sqlite3
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


select_database_by_code = "SELECT * FROM quotes WHERE code= {}"
con = sqlite3.connect("{}/PycharmProjects/stock_updated/application/quotes.db".format(str(Path.home())), check_same_thread=False)


def select_from_database(instrument_code):
    df = pd.read_sql_query(select_database_by_code.format(instrument_code), con, index_col='date', parse_dates=['date'])
    df.index = pd.to_datetime(df.index, unit='s')
    df.drop('id', axis=1, inplace=True)
    return df


def get_dataframe_of_instrument(code):

    data_hour = select_from_database(code)

    data_day = pd.DataFrame()
    data_day["code"] = data_hour.code.resample('D').first().dropna(how='any')
    data_day["open"] = data_hour.open.resample('D').first().dropna(how='any')
    data_day["high"] = data_hour.high.resample('D').max().dropna(how='any')
    data_day["low"] = data_hour.low.resample('D').min().dropna(how='any')
    data_day["close"] = data_hour.close.resample('D').last().dropna(how='any')
    data_day["vol"] = data_hour.vol.resample('D').sum().dropna(how='any')

    data_week = pd.DataFrame()
    data_week["code"] = data_hour.code.resample('W').first().dropna(how='any')
    data_week["open"] = data_hour.open.resample('W').first().dropna(how='any')
    data_week["high"] = data_hour.high.resample('W').max().dropna(how='any')
    data_week["low"] = data_hour.low.resample('W').min().dropna(how='any')
    data_week["close"] = data_hour.close.resample('W').last().dropna(how='any')
    data_week["vol"] = data_hour.vol.resample('W').sum().dropna(how='any')

    data_4_hours = pd.DataFrame()
    data_4_hours["code"] = data_hour.code.resample('4H').first().dropna(how='any')
    data_4_hours["open"] = data_hour.open.resample('4H').first().dropna(how='any')
    data_4_hours["high"] = data_hour.high.resample('4H').max().dropna(how='any')
    data_4_hours["low"] = data_hour.low.resample('4H').min().dropna(how='any')
    data_4_hours["close"] = data_hour.close.resample('4H').last().dropna(how='any')
    data_4_hours["vol"] = data_hour.vol.resample('4H').sum().dropna(how='any')

    return {'4 hours': data_4_hours, 'day': data_day, 'week': data_week}

def print_plot(fast,middle,slow, period, instrument):
    plt.figure(figsize = (20,10))
    plt.plot(slow[-200:])
    plt.plot(fast[-200:])
    plt.plot(middle[-200:])
    plt.xlabel('{} {}'.format(period, instrument),fontsize=18)
    plt.ylabel('Mid Price',fontsize=18)
    plt.show()


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
    'Aud/Nzd': {'week': (22, 29, 95), 'day': (19, 86, 122), '4 hours': (16, 26, 167)}
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

instrument = "Cad/Jpy"

wma = parameters_wma.get(instrument)
data = get_dataframe_of_instrument(currency.get(instrument))
df_4 = data.get("4 hours")
df_day = data.get("day")
df_w = data.get("week")

wma_4 = wma.get('4 hours')
wma_d = wma.get('day')
wma_w = wma.get('week')


fast_4 = talib.WMA(df_4['close'].values, timeperiod=wma_4[0])
middle_4 = talib.WMA(df_4['close'].values, timeperiod=wma_4[1])
slow_4 = talib.WMA(df_4['close'].values, timeperiod=wma_4[2])

print((fast_4[-1] < middle_4[-1]) and (middle_4[-1] < slow_4[-1]))

fast_d = talib.WMA(df_day['close'].values, timeperiod=wma_d[0])
middle_d = talib.WMA(df_day['close'].values, timeperiod=wma_d[1])
slow_d = talib.WMA(df_day['close'].values, timeperiod=wma_d[2])

fast_w = talib.WMA(df_w['close'].values, timeperiod=wma_w[0])
middle_w = talib.WMA(df_w['close'].values, timeperiod=wma_w[1])
slow_w = talib.WMA(df_w['close'].values, timeperiod=wma_w[2])

print_plot(fast_4, middle_4, slow_4, "4 hours", instrument)
print_plot(fast_d, middle_d, slow_d, "day", instrument)
print_plot(fast_w, middle_w, slow_w, "week", instrument)
