import base64
import datetime
import os
import subprocess
import tempfile
import urllib

import math
import pandas as pd
import time
import glob

import pytz
import requests
from const import *

import logging

from database import save_to_db

logging.basicConfig(level=logging.INFO)

day_exclusion = ['Saturday', 'Sunday']
data_time = [["<DATE>", "<TIME>"]]
cols = ["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<VOL>"]
udapted_column_name = ['Date', 'Open', 'High', 'Low', 'Close', 'Vol']


def make_request(list_for_update, today_only=True):
    for instrument in list_for_update:
        if instrument in stocks_instruments:
            execute_request(instrument, market_codes.get('stocks'), "stock", today_only)
        elif instrument in index_instruments:
            execute_request(instrument, market_codes.get('indexes'), "stock", today_only)
        elif instrument in usa_industry:
            execute_request(instrument, market_codes.get('usa_industry'), "stock", today_only)
        elif instrument in etf:
            execute_request(instrument, market_codes.get('etf'), "stock", today_only)
        elif instrument in currency:
            execute_request(instrument, market_codes.get('currency'), "currency", today_only)
        elif instrument in goods:
            execute_request(instrument, market_codes.get('goods'), "goods", today_only)

    clear_dir("currency")
    clear_dir("stock")
    clear_dir("goods")


def execute_request(instrument, market_code, instrument_dir, today_only):
    logging.info("Start to update {} at the {}".format(str(instrument),
                                                       datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')))
    path_to_dir = UPLOAD_FOLDER + "/" + instrument_dir
    file_instrument_name = instrument.replace(" ", "_").replace("&", "_").replace("/", "_") + "_"
    instrument_code = str(all_instruments.get(instrument))

    list_of_dates = get_list_of_dates(today_only)
    successfully_download = True
    for i in range(0, len(list_of_dates)-1):
        file_name = file_instrument_name + list_of_dates[i].strftime("%m.%d.%Y") + "_" + list_of_dates[i+1].strftime("%m.%d.%Y") + "_" + instrument_code
        url_request = quotes_str.format(
            file_name,
            market_code,
            instrument_code,
            list_of_dates[i].day,
            list_of_dates[i].month - 1,
            list_of_dates[i].year,
            list_of_dates[i].strftime("%m.%d.%Y"),
            list_of_dates[i+1].day,
            list_of_dates[i+1].month - 1,
            list_of_dates[i+1].year,
            list_of_dates[i+1].strftime("%m.%d.%Y"),
            periods.get("_HOUR"),
            file_name
        )

        retries = 0
        while True and retries < 4:
            try:
                retries += 1
                urllib.request.urlretrieve(url_request, os.path.join(path_to_dir, file_name + "_TEMP.csv"))
                successfully_download = True
            except:
                successfully_download = False
                time.sleep(.7)
                logging.info("Could not make request to url {}".format(str(url_request)))
            else:
                break
        time.sleep(.5)
    logging.info("{} Was downloaded and now begin to parse files. time: {}".format(str(instrument),
                                                       datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime(
                                                           '%Y-%m-%d %H:%M:%S')))
    if not successfully_download:
        for temp_file in glob.glob(path_to_dir + "/*.csv"):
            if "_TEMP" in str(temp_file):
                os.unlink(temp_file)
    else:
        # merge in one csv file and remove after that
        list_of_files = sorted(glob.glob(path_to_dir + "/*.csv"), key=os.path.getctime)
        files = []
        for the_file in list_of_files:
            if instrument_code == str(the_file.split("_")[-2:-1][0]):
                files.append(the_file)

        combined_csv = prepare_csv_file(files)
        if not combined_csv.empty:
            combined_csv = combined_csv.drop_duplicates()
            save_to_db(combined_csv, instrument)
        else:
            logging.info("Empty dataframe from file " + str(instrument))
        for file in files:
            os.unlink(file)
    logging.info("End update {} at the {}".format(str(instrument),
                 datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')))


def get_list_of_dates(today_only=False):
    data_end = datetime.datetime.now().strftime("%m.%d.%Y")

    if today_only:
        # truly it should have been 1 but i had set 5 for safety
        period_ago = 5
        period = 2
        data_begin = (datetime.datetime.now() - datetime.timedelta(days=period_ago)).strftime("%m.%d.%Y")
        dates = pd.Series(pd.date_range(start=data_begin, end=data_end, periods=period))
        return dates.tolist()
    else:
        if os.environ.get('OPTIMISATION'):
            period_ago = 1500
        else:
            period_ago = 365
        data_begin = (datetime.datetime.now() - datetime.timedelta(days=period_ago)).strftime("%m.%d.%Y")

    period = int(math.ceil(period_ago/100))

    dates = pd.Series(pd.date_range(start=data_begin, end=data_end, periods=period))
    return dates.tolist()


def create_dir(dir_instrument):
    dir = UPLOAD_FOLDER + "/" + dir_instrument
    if not os.path.exists(dir):
        os.makedirs(dir)


def clear_dir(dir_instrument):
    dir = UPLOAD_FOLDER + "/" + dir_instrument
    for the_file in os.listdir(dir):
        file_path = os.path.join(dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    logging.info("directory {} was cleared".format(str(dir)))


def prepare_csv_file(files):
    overal_data = []

    for file in files:
        try:
            data = pd.read_csv(file, header=0, delim_whitespace=True, usecols=cols,
                       parse_dates=data_time, engine='python')
            data.columns = udapted_column_name

            # remove extra data for Saturday and Sunday
            data = data[~(pd.to_datetime(data['Date']).dt.weekday_name.isin(day_exclusion))]
            overal_data.append(data)
        except:
            logging.info("Could not parse file: {}".format(str(file)))
            return pd.DataFrame()
    return pd.concat(overal_data, axis=0)
