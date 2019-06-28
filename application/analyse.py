import glob
import pandas as pd
import datetime
import logging

import pytz
from indicators_analyse import indicators_make_analyse
from database import select_from_database
from const import *

logging.basicConfig(level=logging.INFO)


def get_dataframe_of_instrument(instrument):

    data_hour = select_from_database(all_instruments.get(instrument))

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

    if instrument in currency:
        data_4_hours = pd.DataFrame()
        data_4_hours["code"] = data_hour.code.resample('4H').first().dropna(how='any')
        data_4_hours["open"] = data_hour.open.resample('4H').first().dropna(how='any')
        data_4_hours["high"] = data_hour.high.resample('4H').max().dropna(how='any')
        data_4_hours["low"] = data_hour.low.resample('4H').min().dropna(how='any')
        data_4_hours["close"] = data_hour.close.resample('4H').last().dropna(how='any')
        data_4_hours["vol"] = data_hour.vol.resample('4H').sum().dropna(how='any')
        return {'4 hours': data_4_hours, 'day': data_day, 'week': data_week}
    else:
        return {'day': data_day, 'week': data_week}


def make_analyse(instruments_for_analyse):
    unite_data = dict()
    results = dict()
    logging.info("Process of collection from database to dataframe of was started at {}".format(datetime.datetime.now(
                                                                               pytz.timezone('Europe/Moscow')).strftime(
                                                                               '%Y-%m-%d %H:%M:%S')))
    for instrument in instruments_for_analyse:
        try:
            data = get_dataframe_of_instrument(instrument)
            data = remove_current_period(data)
            unite_data[str(instrument)] = data
        except:
            logging.info("could not read {}".format(instrument))

    logging.info("Process of collection from database to dataframe of was ended at {}".format(datetime.datetime.now(
                                                                               pytz.timezone('Europe/Moscow')).strftime(
                                                                               '%Y-%m-%d %H:%M:%S')))
    results['indicators'] = indicators_make_analyse(unite_data)
    return results


def remove_current_period(data):
    # at weekend week and day data is closed and we can use, in workdays we should cut last day and week
    result = dict()
    week_no = datetime.datetime.today().weekday()
    if week_no < 5:
        for each_data in data:
            temp_data = data.get(each_data)
            temp_data = temp_data[:-1]
            result[each_data] = temp_data
        return result
    else:
        return data


# working with global variable
def clear_lists_of_results():
    const.result_currency.clear()
    const.result_stocks.clear()


def set_currensy_result(list_of_result):
    const.result_currency = list_of_result


def set_stocks_result(list_of_result):
    const.result_stocks = list_of_result