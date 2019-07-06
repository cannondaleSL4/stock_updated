import re
import json
from operator import itemgetter
from markupsafe import Markup


class ResultAnalyse:

    result_for_html = Markup()

    def __init__(self, results):
        self.result_for_html = self.result_to_markup(results)

    def result_to_markup(self, result):
        result_html = ""

        if 'wma result' in result:
            wma_results = result.get('wma result')

            buy_dict_wma = dict()
            sell_dict_wma = dict()

            result_html += "<div class=\"col\"><table class=\"table table-inverse\"> <thread>" + \
                      "<tr><th scope=\"col\">Take a look for instrument(s)</th><th scope=\"col\">{}</th></tr></thread>".format(
                          "WMA")
            for key in wma_results:
                if 'buy' in wma_results.get(key).get('day'):
                    buy_dict_wma[key] = wma_results.get(key)
                else:
                    sell_dict_wma[key] = wma_results.get(key)

            buy_list = self.sort_by_days(buy_dict_wma)
            sell_list = self.sort_by_days(sell_dict_wma)

            for res in buy_list:
                result_html += "<tr><td>" + res.split("|")[0] + "</td><td>" + res.split("|")[1] + "</td></tr>"
            for res in sell_list:
                result_html += "<tr><td>" + res.split("|")[0] + "</td><td>" + res.split("|")[1] + "</td></tr>"

            result_html += "</table></div>"

        if 'williams' in result:
            william_result = result.get('williams')
            result_html += "<div class=\"col\"><table class=\"table table-inverse\"> <thread>" + \
                           "<tr><th scope=\"col\">Take a look for instrument(s)</th>" \
                           "<th scope=\"col\">{}</th></tr></thread>".format(
                               "Williams R(%)")
            for res in sorted(william_result.keys()):
                result_html += "<tr><td>" + res + "</td><td>" + william_result.get(res) + "</td></tr>"
            result_html += "</table></div>"
        if 'rsi result' in result:
            rsi_results = result.get('rsi result')
            result_html += "<div class=\"col\"><table class=\"table table-inverse\"> <thread>" + \
                           "<tr><th scope=\"col\">Take a look for instrument(s)</th>" \
                           "<th scope=\"col\">{}</th></tr></thread>".format(
                               "RSI")
            for res in sorted(rsi_results.keys()):
                result_html += "<tr><td>" + res + "</td><td>" + rsi_results.get(res) + "</td></tr>"
            result_html += "</table></div>"
        return Markup(result_html)

    def sort_by_days(self, dict_wma):
        list_sorted = list()
        temp_dict = dict()

        for key in sorted(dict_wma):
            number = int(re.findall(r'\d+', dict_wma.get(key).get("day"))[0])
            temp_dict[key] = number

        sorted_dict = sorted(temp_dict.items(), key=itemgetter(1))

        for key in sorted_dict:
            result = key[0] + " | " + dict_wma.get(key[0]).get("day")
            list_sorted.append(result)

        return list_sorted

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
