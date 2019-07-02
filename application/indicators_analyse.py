from datetime import datetime, timedelta

import numpy as np
import talib
import logging
from const import *

logging.basicConfig(level=logging.INFO)

default_dict_wma = {"week": [10, 20, 50], "day": [10, 20, 50], "4 hours": [10, 20, 50]}


def indicators_make_analyse(dict_of_dataframes):
    results = dict()
    if list(dict_of_dataframes.keys())[0] in currency:
        results['wma result'] = get_result_currency(dict_of_dataframes)
    else:
        dict_of_stock_results = get_result_stock(dict_of_dataframes)
        results['wma result'] = dict_of_stock_results.get('wma')
        results['rsi result'] = dict_of_stock_results.get('rsi')
        results['williams'] = dict_of_stock_results.get('williams')

    return results


def get_result_currency(dict_of_dataframes):
    wma_result = dict()
    for instrument in dict_of_dataframes:
        if not parameters_wma.get(instrument):
            # logging.info("for instrument {} will be used default parameters 10,20,50".format(instrument))
            result = for_three_timeframe(dict_of_dataframes.get(instrument), default_dict_wma)
        else:
            result = for_three_timeframe(dict_of_dataframes.get(instrument), parameters_wma.get(instrument))

        if result != 'undefined':
            wma_result[instrument] = result

    return wma_result


def get_result_stock(dict_of_dataframes):
    wma_result = dict()
    rsi_result = dict()
    williams_result = dict()
    local_result = dict()
    for instrument in dict_of_dataframes:
        if not parameters_wma.get(instrument):
            # logging.info("for instrument {} will be used default parameters 10,20,50".format(instrument))
            result = for_two_time_frames(dict_of_dataframes.get(instrument), default_dict_wma)
        else:
            result = for_two_time_frames(dict_of_dataframes.get(instrument), parameters_wma.get(instrument))

        if result != 'undefined':
            wma_result[instrument] = result
            local_result['wma'] = wma_result

        result = 'undefined'
        result = get_indicators_result(dict_of_dataframes.get(instrument), "rsi")

        if result != 'undefined':
            rsi_result[instrument] = result.replace("/", "", 1)
            local_result['rsi'] = rsi_result

        result = 'undefined'
        result = get_indicators_result(dict_of_dataframes.get(instrument), "williams")

        if result != 'undefined':
            williams_result[instrument] = result.replace("/", "", 1)
            local_result['williams'] = williams_result

    return local_result


def get_indicators_result(dict_of_dataframes, indicator):
    result = ""
    time_periods = ('4 hours', 'day', 'week')
    for period in time_periods:
        if period in dict_of_dataframes:
            if indicator == "rsi":
                temp_result = result_rsi(dict_of_dataframes.get(period))
            elif indicator == "williams":
                temp_result = result_willams(dict_of_dataframes.get(period))
            if temp_result != 'undefined':
                result = result + "/" + period + " : " + temp_result
    if not result:
        return 'undefined'
    return result


def for_two_time_frames(dict_of_dataframes, dict_of_wma):
    temp_result = dict()
    for frame_period in dict_of_dataframes:
        temp_result[frame_period] = result_in_wma(dict_of_dataframes.get(frame_period), dict_of_wma.get(frame_period))
        if temp_result[frame_period] == 'undefined':
            return 'undefined'

    if ("sell" in temp_result['week']) and ("sell" in temp_result['day']):
        return temp_result

    if ("buy" in temp_result['week']) and ("buy" in temp_result['day']):
        return temp_result

    return 'undefined'


def for_three_timeframe(dict_of_dataframes, dict_of_wma):
    temp_result = dict()
    for frame_period in dict_of_dataframes:
        temp_result[frame_period] = result_in_wma(dict_of_dataframes.get(frame_period), dict_of_wma.get(frame_period))
        if temp_result[frame_period] == 'undefined':
            return 'undefined'

    if ("sell" in temp_result['week']) and ("sell" in temp_result['day']) and ("sell" in temp_result['4 hours']):
        adx = adx_filter(dict_of_dataframes.get('day'), 'sell')
        if adx != 'sell':
            return 'undefined'
        return temp_result

    if ("buy" in temp_result['week']) and ("buy" in temp_result['day']) and ("buy" in temp_result['4 hours']):
        adx = adx_filter(dict_of_dataframes.get('day'), 'buy')
        if adx != 'buy':
            return 'undefined'
        return temp_result

    return 'undefined'


def result_in_wma(data, list_of_wma):
    fast_period = list_of_wma[0]
    middle_period = list_of_wma[1]
    slow_period = list_of_wma[2]
    try:
        fast = talib.WMA(data['close'].values, timeperiod=fast_period)
        middle = talib.WMA(data['close'].values, timeperiod=middle_period)
        slow = talib.WMA(data['close'].values, timeperiod=slow_period)
    except:
        logging.info("could not get wma")
        return 'undefined'

    period = get_period(data)
    if period == "undefined":
        return 'undefined'

    # if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]) and (data.close[-1] > fast[-1]):
    if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]):
        for i in range(1, 100):
            # if not ((fast[-i] > middle[-i]) and (middle[-i] > slow[-i]) and (data.close[-1] > fast[-1])):
            if not ((fast[-i] > middle[-i]) and (middle[-i] > slow[-i])):
                    return 'buy during:{} periods of({})'.format(i, period)

    # if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]) and (data.close[-1] < fast[-1]):
    if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]):
        for i in range(1, 100):
            # if not ((fast[-i] < middle[-i]) and (middle[-i] < slow[-i]) and (data.close[-1] < fast[-1])):
            if not ((fast[-i] < middle[-i]) and (middle[-i] < slow[-i])):
                return 'sell during:{} periods of({})'.format(i, period)

    return 'undefined'


def adx_filter(data, operation):
    adx = talib.ADX(data.high.values, data.low.values, data.close.values, timeperiod=14)
    minus = talib.MINUS_DI(data.high.values, data.low.values, data.close.values, timeperiod=14)
    plus = talib.PLUS_DI(data.high.values, data.low.values, data.close.values, timeperiod=14)

    if adx[-1] > adx[-2]:
        if operation == 'buy' and plus[-1] > minus[-1]:
            return operation
        if operation == 'sell' and plus[-1] < minus[-1]:
            return operation
    return 'undefined'


def result_rsi(data):
    try:
        rsi = talib.RSI(data['close'].values, timeperiod=14)
        # return around numpy
        if (rsi[-2] >= 70) and (rsi[-1] <= 70):
            return 'turn to short ' + '%.2f' % np.float32(rsi[-1])
        elif (rsi[-2] <= 30) and (rsi[-1] >= 30):
            return 'turn to long ' + '%.2f' % np.float32(rsi[-1])
    except:
        logging.info("could not get RSI")

    return 'undefined'


def result_willams(data):
    try:
        willams = talib.WILLR(data.high.values, data.low.values, data.close.values, timeperiod=14)
        if willams[-2] > -20 > willams[-1]:
            return "turn to short"
        if willams[-2] < -80 < willams[-1]:
            return "turn to long"
    except:
        logging.info("could not get williams values")
    return 'undefined'


def get_period(data):
    try:
        time_diff = data.index[-1] - data.index[-2]
        period = "undefined"
        if str(time_diff) == '1 days 00:00:00' or str(time_diff) == '2 days 00:00:00' or str(
                time_diff) == '3 days 00:00:00':
            period = "days"
        elif str(time_diff) == '7 days 00:00:00':
            period = "week"
        elif str(time_diff) == '0 days 04:00:00' or str(time_diff) == '0 days 08:00:00' or str(
                time_diff) == '0 days 12:00:00' or str(time_diff) == '0 days 16:00:00' or str(
                time_diff) == '0 days 20:00:00':
            period = "4 hours"
        return period
    except:
        logging.info("could not get period")
        return "undefined"
