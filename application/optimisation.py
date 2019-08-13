import os
from threading import Thread

import pytz
from const import all_instruments, currency
from analyse import get_dataframe_of_instrument
import talib
from datetime import datetime, timedelta
import pandas as pd
import json 
import logging
from const import *

logging.basicConfig(level=logging.INFO)


def get_best_params(dict_of_instruments=currency):
    instrument = os.getenv('INSTRUMENT')
    logging.info("Begin procedure of optimisation")
    dict_of_results = dict()
    # for instrument in dict_of_instruments:
    #     dict_of_dataframes = get_dataframe_of_instrument(instrument)
    #     dict_of_results[instrument] = williams_results(dict_of_dataframes)

    dict_of_dataframes = get_dataframe_of_instrument(instrument)
    dict_of_results[instrument] = williams_results(dict_of_dataframes)

    json_result = json.dumps(str(dict_of_results))
    logging.info(str(dict_of_results))


def williams_results(dict_of_dataframes):
    local_dict = dict()
    week_dateframe = dict_of_dataframes.get("week")
    day_dateframe = dict_of_dataframes.get("day")
    local_dict["week"] = get_list_of_willams_deals(week_dateframe)
    local_dict["day"] = get_list_of_willams_deals(day_dateframe)

    return local_dict




def get_list_of_willams_deals(test_dateframe):
    start_index = ""
    buy_or_sell = ""
    list_of_deals = list()
    for index, row in test_dateframe[14:].iterrows():
        temp_slice = test_dateframe.iloc[
                     :test_dateframe.index.searchsorted(datetime.fromtimestamp(index.timestamp())) + 1]
        willams = talib.WILLR(temp_slice.high.values, temp_slice.low.values, temp_slice.close.values, timeperiod=14)

        # if willams[-2] > -20 > willams[-1]:
        #     # "turn to short"
        #     if start_index == "":
        #         start_index = index
        #         buy_or_sell = "sell"

        if willams[-2] < -80 < willams[-1]:
            # "turn to long"
            adx = talib.ADX(temp_slice.high.values, temp_slice.low.values, temp_slice.close.values, timeperiod=14)
            if start_index == "" and adx[-2] > adx[-1]:
                start_index = index
                buy_or_sell = "buy"

        if start_index != "":
            if buy_or_sell == "buy":
                if willams[-1] > -20:
                    deal = Deal(
                        test_dateframe.iloc[
                        test_dateframe.index.searchsorted(datetime.fromtimestamp(start_index.timestamp())):
                        test_dateframe.index.searchsorted(datetime.fromtimestamp(index.timestamp())) + 1],
                        buy_or_sell)
                    list_of_deals.append(deal)
                    start_index = ""
                    buy_or_sell = ""
            if buy_or_sell == "sell":
                if willams[-1] < -80:
                    # deal = Deal(
                    #     week_dateframe.iloc[
                    #     week_dateframe.index.searchsorted(datetime.fromtimestamp(start_index.timestamp())):
                    #     week_dateframe.index.searchsorted(datetime.fromtimestamp(index.timestamp())) + 1],
                    #     buy_or_sell)
                    # list_of_deals.append(deal)
                    start_index = ""
                    buy_or_sell = ""

    return list_of_deals


def result_with_specific_parameters(dateframe, array_of_wma_parametrs):
    list_of_deals = list()
    counter = 0
    temp_fast = array_of_wma_parametrs[0]
    temp_middle = array_of_wma_parametrs[1]
    temp_slow = array_of_wma_parametrs[2]
    start_index = ""
    end_index = ""
    for index, row in dateframe[temp_slow:].iterrows():
        result = in_market(
            dateframe.iloc[counter:dateframe.index.searchsorted(datetime.fromtimestamp(index.timestamp()))],
            temp_fast, temp_middle, temp_slow
        )
        counter = counter + 1
        if result != 'undefined':
            if start_index != "":
                end_index = index
            elif start_index == "":
                buy_or_sell = result
                start_index = index
        if result == 'undefined' and end_index != "" and start_index != "":  # it's the end of deal
            deal = Deal(
                dateframe.iloc[dateframe.index.searchsorted(datetime.fromtimestamp(start_index.timestamp())):
                               dateframe.index.searchsorted(datetime.fromtimestamp(end_index.timestamp()))+1],
                buy_or_sell)
            list_of_deals.append(deal)
            start_index = ""
            end_index = ""
            buy_or_sell = ""

    return list_of_deals


def get_profit_factor(list_of_deals):
    sum_with_proffit = 0
    summ_with_loss = 0
    for c in list_of_deals:
        if c.result_of_deal > 0:
            sum_with_proffit = sum_with_proffit + c.result_of_deal
        elif c.result_of_deal < 0:
            summ_with_loss = summ_with_loss + abs(c.result_of_deal)
    if sum_with_proffit == 0:
        return 0
    if summ_with_loss == 0:
        summ_with_loss = 1
    return sum_with_proffit / summ_with_loss


# def in_market(data_slice, fast_period, middle_period, slow_period):
#     fast = talib.WMA(data_slice['close'].values, timeperiod=fast_period)
#     middle = talib.WMA(data_slice['close'].values, timeperiod=middle_period)
#     slow = talib.WMA(data_slice['close'].values, timeperiod=slow_period)
#
#     if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]):
#         return 'buy'
#     if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]):
#         return 'sell'
#     return 'undefined'


class Deal:

    result_of_deal = 0
    dataframe = pd.DataFrame()
    buy_or_sell = ""

    def __init__(self, dataframe, buy_or_sell):
        self.dataframe = dataframe
        self.buy_or_sell = buy_or_sell
        self.get_result(self.dataframe, self.buy_or_sell)

    def get_result(self, dataframe, buy_or_sell):
        if buy_or_sell == 'buy':
            self.result_of_deal = dataframe.close.values[-1] - dataframe.close.values[0]
        elif buy_or_sell == 'sell':
            self.result_of_deal = dataframe.close.values[0] - dataframe.close.values[-1]


if __name__ == "__main__":
    init()
    # t_1 = Thread(target=get_best_params, args=[stocks_instruments])
    t_1 = Thread(target=get_best_params)
    t_1.start()
