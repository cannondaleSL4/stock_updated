import numpy as np
import talib
import logging
from const import parameters_wma

logging.basicConfig(level=logging.INFO)

default_dict_wma = {"week": [10, 20, 50], "day": [10, 20, 50], "4 hours": [10, 20, 50]}


def indicators_make_analyse(dict_of_dataframes):
    results = dict()
    wma_4_result = dict()
    pattern_result_dict = dict()

    for instrument in dict_of_dataframes:
        if not parameters_wma.get(instrument):
            logging.info("for instrument {} will be used default parameters 10,20,50".format(instrument))
            result = for_three_timeframe(dict_of_dataframes.get(instrument), default_dict_wma)
        else:
            result = for_three_timeframe(dict_of_dataframes.get(instrument), parameters_wma.get(instrument))

        if result != 'undefined':
            wma_4_result[instrument] = result

        pattern_result = model(dict_of_dataframes.get(instrument))

        if pattern_result != 'undefined':
            pattern_result_dict[instrument] = pattern_result

    results['wma 4 result'] = wma_4_result
    results['pattern'] = pattern_result_dict

    return results


def for_three_timeframe(dict_of_dataframes, dict_of_wma):
    temp_result = dict()
    for frame_period in dict_of_dataframes:
        temp_result[frame_period] = result_in_wma(dict_of_dataframes.get(frame_period), dict_of_wma.get(frame_period))
        if temp_result[frame_period] == 'undefined':
            return 'undefined'

    if ("sell" in temp_result['week']) and ("sell" in temp_result['day']) and ("sell" in temp_result['4 hours']):
        return temp_result

    if ("buy" in temp_result['week']) and ("buy" in temp_result['day']) and ("buy" in temp_result['4 hours']):
        return temp_result

    return 'undefined'


def result_in_wma(data, list_of_wma):
    fast_period = list_of_wma[0]
    middle_period = list_of_wma[1]
    slow_period = list_of_wma[2]
    fast = talib.WMA(data['close'].values, timeperiod=fast_period)
    middle = talib.WMA(data['close'].values, timeperiod=middle_period)
    slow = talib.WMA(data['close'].values, timeperiod=slow_period)

    time_diff = data.index[-1] - data.index[-2]

    period = "undefined"
    if str(time_diff) == '1 days 00:00:00' or str(time_diff) == '2 days 00:00:00' or str(time_diff) == '3 days 00:00:00':
        period = "days"
    elif str(time_diff) == '7 days 00:00:00':
        period = "week"
    elif str(time_diff) == '0 days 04:00:00' or str(time_diff) == '0 days 08:00:00' or str(time_diff) == '0 days 12:00:00' or str(time_diff) == '0 days 16:00:00' or str(time_diff) == '0 days 20:00:00':
        period = "4 hours"

    if period == "4 hours":
        if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]) and (data.close[-1] > fast[-1]):
            for i in range(1, 100):
                if not ((fast[-i] > middle[-i]) and (middle[-i] > slow[-i]) and (data.close[-1] > fast[-1])):
                    return 'buy during:{} periods of({})'.format(i, period)

        if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]) and (data.close[-1] < fast[-1]):
            for i in range(1, 100):
                if not ((fast[-i] < middle[-i]) and (middle[-i] < slow[-i]) and (data.close[-1] < fast[-1])):
                    return 'sell during:{} periods of({})'.format(i, period)
    else:
        if (fast[-1] > middle[-1]) and (middle[-1] > slow[-1]):
            return 'buy'
        if (fast[-1] < middle[-1]) and (middle[-1] < slow[-1]):
            return 'sell'

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
    rsi = talib.RSI(data['Close'].values, timeperiod=14)
    # return around numpy
    if (rsi[-2] >= 70) and (rsi[-1] <= 70):
        return 'turn to short ' + '%.2f' % np.float32(rsi[-1])
    elif (rsi[-2] <= 30) and (rsi[-1] >= 30):
        return 'turn to long ' + '%.2f' % np.float32(rsi[-1])
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
        engulfing = talib.CDLENGULFING(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        if engulfing.T[-1] == -100:
            dict_of_result[str(time_period) + " engulfing"] = "sell"
        if engulfing.T[-1] == 100:
            dict_of_result[str(time_period) + " engulfing"] = "buy"

        # # it's up
        # hammer = talib.CDLHAMMER(dataframe.open, dataframe.high, dataframe.low, dataframe.close)
        #
        # if hammer.T[-1] != 0:
        #     dict_of_result[str(time_period) + " hummer"] = "buy"

        # # it's up
        # inverted_hammer = talib.CDLINVERTEDHAMMER(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        # if inverted_hammer.T[-1] != 0:
        #     dict_of_result[str(time_period) + " inverted hummer"] = "buy"

        #it's up
        three_white_solders = talib.CDL3WHITESOLDIERS(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        if three_white_solders.T[-1] != 0:
            dict_of_result[str(time_period) + " three white solders"] = "buy"

        #it's up
        morning_star = talib.CDLMORNINGSTAR(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        if morning_star.T[-1] != 0:
            dict_of_result[str(time_period) + " morning star"] = "buy"

        #it's up
        three_star_south = talib.CDL3STARSINSOUTH(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        if three_star_south.T[-1] != 0:
            dict_of_result[str(time_period) + " three star south"] = "buy"


        #it's down
        shooting_star = talib.CDLSHOOTINGSTAR(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        if shooting_star.T[-1] != 0:
            dict_of_result[str(time_period) + " shooting star"] = "sell"

        #it's down
        evening_star = talib.CDLEVENINGSTAR(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        if evening_star.T[-1] != 0:
            dict_of_result[str(time_period) + " evening star"] = "sell"

        #lt's down
        three_black_crows = talib.CDL3BLACKCROWS(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        if three_black_crows.T[-1] != 0:
            dict_of_result[str(time_period) + " three black crows"] = "sell"

        # #it's down
        # handing_man = talib.CDLHANGINGMAN(dataframe.open, dataframe.high, dataframe.low, dataframe.close)

        # if handing_man.T[-1] != 0:
        #     dict_of_result[str(time_period) + " handing man"] = "sell"

    if not bool(dict_of_result):
        return 'undefined'

    return dict_of_result

