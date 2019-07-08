import datetime
import re
import json
from operator import itemgetter
from markupsafe import Markup
from const import *


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
            result_html += "<div class=\"col\"><table class=\"table table-inverse\"> <thread>" + \
                           "<tr><th scope=\"col\">Take a look for instrument(s)</th>"
            for instrument in current_deals:
                if instrument not in buy_dict_wma:
                    result_html += "<tr class=\"table-warning\"><td>" + instrument + "</td><td>"
                if instrument in sell_list:
                    result_html += "<tr class=\"table-danger\"><td>" + instrument + "</td><td>"
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

    # def to_json(self):
    #     return json.dumps(self, default=lambda o: o.__dict__,
    #                       sort_keys=True, indent=4)


class CustomEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return {'__datetime__': o.replace(microsecond=0).isoformat()}

        return {'__{}__'.format(o.__class__.__name__): o.__dict__}


def convert_to_dict(obj):
    """
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names.
    """

    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }

    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)

    return obj_dict


def dict_to_obj(our_dict):
    """
    Function that takes in a dict and returns a custom object associated with the dict.
    This function makes use of the "__module__" and "__class__" metadata in the dictionary
    to know which object type to create.
    """
    if "__class__" in our_dict:
        # Pop ensures we remove metadata from the dict to leave only the instance arguments
        class_name = our_dict.pop("__class__")

        # Get the module name from the dict and import it
        module_name = our_dict.pop("__module__")

        # We use the built in __import__ function since the module name is not yet known at runtime
        module = __import__(module_name)

        # Get the class from the module
        class_ = getattr(module, class_name)

        # Use dictionary unpacking to initialize the object
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj