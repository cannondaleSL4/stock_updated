import json
import pandas as pd
import datetime
import logging

import pytz
from indicators_analyse import indicators_make_analyse
from database import select_from_database, select_from_database_last_record, update_last_result
from const import *
from resultanalyse import ResultAnalyse, CustomEncoder, convert_to_dict, dict_to_obj

logging.basicConfig(level=logging.INFO)


def make_analyse(instruments_for_analyse):
    unite_data = dict()
    logging.info("Process of collection from database to dataframe of was started at {}".format(datetime.datetime.now(
                                                                               pytz.timezone('Europe/Moscow')).strftime(
                                                                               '%Y-%m-%d %H:%M:%S')))

    if instruments_for_analyse[0] in currency:
        request_instrument = "currency"
    else:
        request_instrument = "stock"

    last_result = select_from_database_last_record(request_instrument)

    if not last_result:

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

        result = ResultAnalyse(indicators_make_analyse(unite_data))
        # json_result = result.to_json()
        json_result = json.dumps(result,default=convert_to_dict,indent=4, sort_keys=True)
        # json_result = json.dumps(result, indent=4, cls=CustomEncoder)
        # update_last_result(request_instrument, json_result, time.time())
    else:
        result = json.loads(last_result[1], object_hook=dict_to_obj)
        # result = json.loads(last_result[1], cls=ResultAnalyse)
    return result


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


def remove_current_period(data):
    # at weekend week and day data is closed and we can use, in workdays we should cut last day and week
    # result = dict()
    week_no = datetime.datetime.today().weekday()
    day_of_year_today = datetime.datetime.now().timetuple().tm_yday
    if week_no < 5:
        for each_data in data:
            temp_data = data.get(each_data)
            if each_data != 'week':
                if temp_data.index[-1].dayofyear == day_of_year_today:
                    temp_data = temp_data[:-1]
                    data[each_data] = temp_data
                else:
                    data[each_data] = temp_data
            else:
                temp_data = temp_data[:-1]
                data[each_data] = temp_data
        return data
    else:
        return data