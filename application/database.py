import json
from datetime import datetime

import sqlite3
import logging
import const
import pandas as pd

con = sqlite3.connect("./database/quotes.db", check_same_thread=False)

logging.basicConfig(level=logging.INFO)

create_quotes = """CREATE TABLE IF NOT EXISTS quotes
                      (id integer primary key,instrument text, code text, date timestamp,
                       open text, high real, low real, close real, vol bigint, UNIQUE(code, date) ON CONFLICT REPLACE)
                   """
create_index_code = "CREATE INDEX IF NOT EXISTS  index_quotes_code ON quotes(code)"
create_index_instrument = "CREATE INDEX  IF NOT EXISTS index_quotes_instrument ON quotes(instrument)"

create_table_last_result = "CREATE TABLE IF NOT EXISTS last_result(instrument text primary key, result json," \
                           " date timestamp)"
get_last_result = "SELECT * FROM last_result WHERE instrument = '{}'"
insert_last_result = "INSERT INTO last_result (instrument, result, date) values(?,?,?)"
select_last_record = "SELECT * FROM last_result WHERE instrument= '{}'"


insert = "INSERT INTO quotes(instrument, code, date, open, high, low, close, vol) values(?, ?, ?, ?, ?, ?, ?, ?)"
select_database_by_code = "SELECT * FROM quotes WHERE code= {}"


def start_database():
    cursor = con.cursor()
    cursor.execute(create_quotes)
    cursor.execute(create_table_last_result)
    cursor.execute(create_index_code)
    cursor.execute(create_index_instrument)
    con.commit()


def save_to_db(combined_csv, instrument):
    cur = con.cursor()
    result_for_insert = []
    logging.info("begin update data for {} to database".format(instrument))
    for index, row in combined_csv.iterrows():
        result_for_insert.append([instrument, const.all_instruments.get(instrument), row.Date.timestamp(),
                                  row.Open, row.High, row.Low, row.Close, row.Vol])

    cur.executemany(insert, result_for_insert)
    con.commit()
    logging.info("successfully updated data for {} to database".format(instrument))


def select_from_database(instrument_code):
    df = pd.read_sql_query(select_database_by_code.format(instrument_code), con, index_col='date', parse_dates=['date'])
    df.index = pd.to_datetime(df.index, unit='s')
    df.drop('id', axis=1, inplace=True)
    return df


# working with global variable
def upload_database_status():
    const.database_uploaded = True


def select_from_database_last_record(stock_currency):
    cur = con.cursor()
    cur.execute(select_last_record.format(stock_currency))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    # return rows[0]
    return False


def update_last_result(instrument, updated_result, date):
    cur = con.cursor()
    cur.execute(insert_last_result, (instrument, (json.dumps(updated_result)), date))
    # cur.execute(insert_last_result.format(instrument, json.dumps(updated_result), date))
    con.commit()



