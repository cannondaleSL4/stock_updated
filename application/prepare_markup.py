import datetime
import pytz
from flask import Markup


def result_wma_to_markup(wma_result, indicator_name="WMA"):
    result = ""
    if len(wma_result) != 0:
        result += "<table class=\"table table-inverse\"> <thread>" + \
                  "<tr><th scope=\"col\">Take a look for instrument(s)</th><th scope=\"col\">{}</th></tr></thread>".format(indicator_name)
        for res in sorted(wma_result.keys()):
            result += "<tr><td>" + res + "</td><td>" + wma_result.get(res).get('4 hours') + "</td></tr>"
        result += "</table>"
    return Markup(result)


def prepare_message(dict_result, old_result):

    new = list()
    droped = list()

    if old_result is not None:
        for instrument in old_result:
            if instrument in dict_result:
                continue
            else:
                new.append(instrument)

        for instrument in dict_result:
            if instrument in old_result:
                continue
            else:
                droped.append(instrument)

        result_dict = dict()

    for items in dict_result:
        temp = dict_result.get(items).get("4 hours")
        temp = temp.replace('&', 'AND')
        temp = temp.replace("sell during:", "sell ")
        temp = temp.replace("sell during:", "sell ")
        temp = temp.replace("periods of(4 hours)", "periods")
        result_dict[items] = temp

    result = "*{} {}*%0A".format(datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S'), "4 hours")
    for key in result_dict:
        result += "{}:{}%0A".format(key, result_dict.get(key))

    if len(new) != 0:
        result += "*%0A New instrument(s) is(are):*"
        for item in new:
            result += "%0A{}".format(item)

    if len(droped) != 0:
        result += "*%0A Instrument(s) was(were) dropped:*"
        for item in droped:
            result += "%0A{}".format(item)

    return result