import pytz
from const import all_instruments, currency
from analyse import get_dataframe_of_instrument
import talib
from datetime import datetime, timedelta
import pandas as pd
import json 
import logging

logging.basicConfig(level=logging.INFO)


def get_best_params(dict_of_instruments=currency):
    logging.info("Begin procedure of optimisation")
    dict_of_results = dict()
    for instrument in dict_of_instruments:
        logging.info("begin optimisation parameters for {} at {}".format(instrument, datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')))
        dict_of_dataframes = get_dataframe_of_instrument(instrument)
        # dict_of_dataframes = cut_dataframes(dict_of_dataframes)
        # dict_of_results[instrument] = get_best_parameters(dict_of_dataframes)
        dict_of_results[instrument] = for_three_timeframe(dict_of_dataframes)
    json_result = json.dumps(dict_of_results)
    logging.info(str(json_result))


def cut_dataframes(dataframes):

    cut_4_hours = dataframes.get('4 hours').index.searchsorted(datetime.now() - timedelta(days=(365*1)))
    cut_day = dataframes.get('day').index.searchsorted(datetime.now() - timedelta(days=(365*2)))
    cut_week = dataframes.get('week').index.searchsorted(datetime.now() - timedelta(days=(365*3)))

    dataframes['4 hours'] = dataframes.get('4 hours').iloc[cut_4_hours:]
    dataframes['day'] = dataframes.get('day').iloc[cut_day:]
    dataframes['week'] = dataframes.get('week').iloc[cut_week:]

    return dataframes


def get_best_parameters(dict_of_dataframes):  
    dict_of_results = dict()
    
    for time_period in dict_of_dataframes:
        logging.info("begin optimisation for {} timeperiod at {}".format(time_period, datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')))
        dict_of_results[time_period] = search_in_dateframe(dict_of_dataframes.get(time_period))
    
    return dict_of_results


def for_three_timeframe(dict_of_dataframes):
    week_dateframe = dict_of_dataframes.get("week")
    day_dateframe = dict_of_dataframes.get("day")
    hours_4_dateframe = dict_of_dataframes.get("4 hours")
    list_of_periods = mix_fast_middle_slow()
    result = 0
    dect_of_result = dict()
    dect_of_result[result] = 0

    for w_period in list_of_periods:
        list_of_week_deals = result_with_specific_parameters(week_dateframe, w_period)
        for week_deal in list_of_week_deals:
            for d_period in list_of_periods:
                begin_of_deal = day_dateframe.index.searchsorted(datetime.fromtimestamp(week_deal.dataframe.index[0].timestamp()))
                end_of_deal = day_dateframe.index.searchsorted(datetime.fromtimestamp(week_deal.dataframe.index[-1].timestamp()))

                list_of_day_deals = result_with_specific_parameters(day_dateframe.iloc[begin_of_deal+1:end_of_deal+1], d_period)
    return "test"


def search_in_dateframe(dateframe):
    result = 0
    list_of_periods = mix_fast_middle_slow()
    count = len(list_of_periods)
    counter = 0
    dect_of_result = dict()
    dect_of_result[result] = 0
    logging.info("size of array with wma variants is {}". format(count))
    for period in list_of_periods:
        counter = counter + 1
        list_of_deals = result_with_specific_parameters(dateframe, period)
        temp_result = get_profit_factor(list_of_deals)
        if temp_result > 1 and result < temp_result:
            result = temp_result
            dect_of_result[result] = period
        if counter % 200 == 0:
            logging.info("percent {}% passed ".format(round((counter/count)*100)))
    return dect_of_result.get(result)


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

    # return sum(c.result_of_deal for c in list_of_deals)
    # return get_profit_factor(list_of_deals)
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


def mix_fast_middle_slow():
    fast = list(range(10, 30, 3))
    middle = list(range(20, 100, 3))
    slow = list(range(50, 200, 3))

    result = list()

    for this_fast in fast:
        for this_middle in middle:
            for this_slow in slow:
                if this_fast < this_middle < this_slow:
                    result.append((this_fast, this_middle, this_slow))
    return result


def in_market(data_slice, fast_period, middle_period, slow_period):
    fast = talib.WMA(data_slice['close'].values, timeperiod=fast_period)
    middle = talib.WMA(data_slice['close'].values, timeperiod=middle_period)
    slow = talib.WMA(data_slice['close'].values, timeperiod=slow_period)

    if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]):
        return 'buy'
    if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]):
        return 'sell'
    return 'undefined'


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
