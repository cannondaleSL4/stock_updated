import datetime
from time import gmtime, strftime

import pytz
from flask import Markup

from const import currency, stock_instruments


def result_wma_to_markup(wma_result, indicator_name="WMA"):
    result = ""
    if len(wma_result) != 0:
        result += "<table class=\"table table-inverse\"> <thread>" + \
                  "<tr><th scope=\"col\">Take a look for instrument(s)</th><th scope=\"col\">{}</th></tr></thread>".format(indicator_name)
        for res in sorted(wma_result.keys()):
            result += "<tr><td>" + res + "</td><td>" + wma_result.get(res).get('4 hours') + "</td></tr>"
        result += "</table>"
    return Markup(result)


def prepare_message(dict):
    four_hours = "of(4 hours)"
    time_period = ""
    for key in dict:
        if four_hours in dict.get(key):
            time_period = "4 hours"
            updated_key = key.replace('&', 'AND')
            dict[updated_key] = dict.pop(key)
            dict[updated_key] = dict.get(key).replace(four_hours, "")
            dict[updated_key] = dict.get(key).replace("sell during:", "sell ")
            dict[updated_key] = dict.get(key).replace("buy during:", "buy ")

    result = "*{} {}*%0A".format(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S'),
                                 time_period)
    for key in dict:
        result += "{}:{}%0A".format(key, dict.get(key))
    return result