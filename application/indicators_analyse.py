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

    return results


def get_result_stock(dict_of_dataframes):
    wma_result = dict()
    rsi_result = dict()
    local_result = dict()
    for instrument in dict_of_dataframes:
        if not parameters_wma.get(instrument):
            logging.info("for instrument {} will be used default parameters 10,20,50".format(instrument))
            result = for_two_time_frames(dict_of_dataframes.get(instrument), default_dict_wma)
        else:
            result = for_two_time_frames(dict_of_dataframes.get(instrument), parameters_wma.get(instrument))

        if result != 'undefined':
            wma_result[instrument] = result
            local_result['wma'] = wma_result

        result = 'undefined'
        result = get_rsi_result(dict_of_dataframes.get(instrument))

        if result != 'undefined':
            rsi_result[instrument] = result.replace("/", "", 1)
            local_result['rsi'] = rsi_result

    return local_result


def get_rsi_divergence(dict_of_dataframes):
    result = ""
    time_periods = ('4 hours', 'day', 'week')
    for period in time_periods:
        if period in dict_of_dataframes:
            dataframe = dict_of_dataframes.get(period)
            rsi = talib.RSI(dataframe['close'].values, timeperiod=14)
            if ((sum(dataframe['close'].values[-30:])/30) > dataframe['close'].values[-1]) and (sum(rsi[-30:])/30 < rsi[-1]):
                result = result + "/" + period + " : " + 'buy'
            if ((sum(dataframe['close'].values[-30:]) / 30) < dataframe['close'].values[-1]) and (sum(rsi[-30:])/30 > rsi[-1]):
                result = result + "/" + period + " : " + 'sell'

    if not result:
        return 'undefined'
    return result


def get_rsi_result(dict_of_dataframes):
    result = ""
    time_periods = ('4 hours', 'day', 'week')
    for period in time_periods:
        if period in dict_of_dataframes:
            temp_result_rsi = result_rsi(dict_of_dataframes.get(period))
            if temp_result_rsi != 'undefined':
                result = result + "/" + period + " : " + temp_result_rsi
    if not result:
        return 'undefined'
    return result


def get_result_currency(dict_of_dataframes):
    wma_result = dict()
    for instrument in dict_of_dataframes:
        if not parameters_wma.get(instrument):
            logging.info("for instrument {} will be used default parameters 10,20,50".format(instrument))
            result = for_three_timeframe(dict_of_dataframes.get(instrument), default_dict_wma)
        else:
            result = for_three_timeframe(dict_of_dataframes.get(instrument), parameters_wma.get(instrument))

        if result != 'undefined':
            wma_result[instrument] = result

    return wma_result


def for_two_time_frames(dict_of_dataframes, dict_of_wma):
    temp_result = dict()
    for frame_period in dict_of_dataframes:
        temp_result[frame_period] = result_in_wma(dict_of_dataframes.get(frame_period), dict_of_wma.get(frame_period))
        if temp_result[frame_period] == 'undefined':
            return 'undefined'

    if ("sell" in temp_result['week']) and ("sell" in temp_result['day']):
        adx = adx_filter(dict_of_dataframes.get('week'), 'sell')
        if adx != 'sell':
            return 'undefined'
        return temp_result

    if ("buy" in temp_result['week']) and ("buy" in temp_result['day']):
        adx = adx_filter(dict_of_dataframes.get('week'), 'buy')
        if adx != 'buy':
            return 'undefined'
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

    if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]) and (data.close[-1] > fast[-1]):
        for i in range(1, 100):
            if not ((fast[-i] > middle[-i]) and (middle[-i] > slow[-i]) and (data.close[-1] > fast[-1])):
                    return 'buy during:{} periods of({})'.format(i, period)

    if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]) and (data.close[-1] < fast[-1]):
        for i in range(1, 100):
            if not ((fast[-i] < middle[-i]) and (middle[-i] < slow[-i]) and (data.close[-1] < fast[-1])):
                return 'sell during:{} periods of({})'.format(i, period)

    return 'undefined'


def adx_filter(data, operation):
    adx = talib.ADX(data.high.values, data.low.values, data.close.values, timeperiod=14)
    if adx[-1] > adx[-2]:
        return operation
    return 'undefined'


def macd_result(data):
    macd = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    result = 'undefined'
    first_before = macd[0][-4]
    second_before = macd[0][-2]
    max_min = macd[0][-3]
    first_after = macd[0][-2]
    second_after = macd[0][-1]
    if ((first_before > second_before) and (second_before > max_min) and (max_min < first_after) and (
            first_after < second_after)):
        result = 'buy'
    if ((first_before < second_before) and (second_before < max_min) and (max_min > first_after) and (
                first_after > second_after)):
        result = 'sell'
    return result


def result_rsi(data):
    try:
        rsi = talib.RSI(data['close'].values, timeperiod=14)
        # return around numpy
        if (rsi[-2] >= 70) and (rsi[-1] <= 70):
            return 'turn to short ' + '%.2f' % np.float32(rsi[-1])
        elif (rsi[-2] <= 30) and (rsi[-1] >= 30):
            return 'turn to long ' + '%.2f' % np.float32(rsi[-1])
    except:
        logging.log("could not get RSI")

    return 'undefined'



def result_mfi(data):
    mfi = talib.MFI(data['High'].values, data['Low'].values, data['Close'].values,
                    np.array(list(map(float, data['Vol']))), timeperiod=14)
    # return around numpy
    if (mfi[-2] >= 80) and (mfi[-1] <= 80):
        return 'turn to short ' + '%.2f' % np.float32(mfi[-1])
    elif (mfi[-2] <= 20) and (mfi[-1] >= 20):
        return 'turn to long ' + '%.2f' % np.float32(mfi[-1])
    return 'undefined'


def result_stochastic(data):
    slowk, slowd = talib.STOCH(data['High'].values, data['Low'].values, data['Close'].values, fastk_period=10,
                               slowk_period=6, slowd_period=6)
    if (slowd[-2] >= 80 and slowk[-2] >= 80) and (slowk[-1] < 80):
        return "sell"

    if (slowd[-2] <= 20 and slowk[-2] <= 80) and (slowk[-1] > 20):
        return "buy"

    return 'undefined'


def get_period(data):
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


def result_bbands(data):
    upperband, middleband, lowerband = talib.BBANDS(np.array(data['Close']),
                                                    timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    last = data['Close'].values[-1]
    pre_last = data['Close'].values[-2]
    if (pre_last > upperband[-2]) and (last < upperband[-1]):
        return 'turn to short'
    if (pre_last < lowerband[-2]) and (last > lowerband[-1]):
        return 'turn to long'
    return 'undefined'


def merge_bbands_stochastic(data):

    upperband, middleband, lowerband = talib.BBANDS(np.array(data['Close']),
                                               timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    bbands_result = 'undefined'
    for i in range(-10, 0):
        last = data['Close'].values[i]
        pre_last = data['Close'].values[i-1]
        if (pre_last > upperband[i-1]) and (last < upperband[i]):
            bbands_result = 'turn to short'
        if (pre_last < lowerband[i-1]) and (last > lowerband[i]):
            bbands_result = 'turn to long'

    if bbands_result != 'undefined':
        return result_stochastic(data)
    return 'undefined'


def model(dataframes):
    dict_of_result = dict()
    for time_period in dataframes:
        # поглощение
        dataframe = dataframes.get(time_period)

        try:
            three_white_solders = talib.CDL3WHITESOLDIERS(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        except:
            logging.info("could not execute analyse for three white solders")

        if three_white_solders.T[-1] != 0:
            dict_of_result[str(time_period) + " three white solders"] = "buy"

        #it's up
        try:
            morning_star = talib.CDLMORNINGSTAR(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        except:
            logging.info("could not execute analyse for morning star")

        if morning_star.T[-1] != 0:
            dict_of_result[str(time_period) + " morning star"] = "buy"

        #it's up
        try:
            three_star_south = talib.CDL3STARSINSOUTH(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        except:
            logging.info("could not execute analyse for three star south")


        if three_star_south.T[-1] != 0:
            dict_of_result[str(time_period) + " three star south"] = "buy"


        #it's down
        try:
            shooting_star = talib.CDLSHOOTINGSTAR(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        except:
            logging.info("could not execute analyse for three shooting star")


        if shooting_star.T[-1] != 0:
            dict_of_result[str(time_period) + " shooting star"] = "sell"

        #it's down
        try:
            evening_star = talib.CDLEVENINGSTAR(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        except:
            logging.info("could not execute analyse for three evening star")

        if evening_star.T[-1] != 0:
            dict_of_result[str(time_period) + " evening star"] = "sell"

        #lt's down
        try:
            three_black_crows = talib.CDL3BLACKCROWS(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        except:
            logging.info("could not execute analyse for three three black crows")

        if three_black_crows.T[-1] != 0:
            dict_of_result[str(time_period) + " three black crows"] = "sell"

        # #it's down
        # handing_man = talib.CDLHANGINGMAN(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        # if handing_man.T[-1] != 0:
        #     dict_of_result[str(time_period) + " handing man"] = "sell"

    if not bool(dict_of_result):
        return 'undefined'

    return dict_of_result

