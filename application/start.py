import logging
import os
import atexit
import ssl
from threading import Thread
from urllib.request import urlopen
from datetime import datetime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pytz
import requests
from flask import Flask
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from analyse import make_analyse, clear_lists_of_results, set_currensy_result, set_stocks_result
from download_update import create_dir, make_request, clear_dir
from prepare_markup import *
from views.view_currency import view_currency
from views.view_stock import view_stock
from const import *
from database import *
from prepare_markup import prepare_message, result_wma_to_markup

from database import update_last_result

port = int(os.environ.get('PORT', 8080))

logging.basicConfig(level=logging.INFO)

url_update = os.environ.get('URL_UPDATE', 'https://app-dmba.herokuapp.com')

mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
token = os.environ.get('TOKEN', '')
chatid = os.environ.get('CHATID', '')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(view_currency)
app.register_blueprint(view_stock)
Bootstrap(app)


def execute(list_for_update):
    logging.info("start automatic update job at the " +
                 datetime.now(pytz.timezone('Europe/Moscow')).strftime("%d.%m.%Y %Y-%m-%d %H:%M:%S"))
    make_request(list_for_update, today_only=True)
    result_of_analyse = make_analyse(list_for_update)
    indicators_result = result_of_analyse.get('indicators')
    wma_result = indicators_result.get('wma result')
    if list_for_update[0] in currency or list_for_update[0] in goods:
        last_result = update_last_result("currency", wma_result)
        text_for_message_telegram = prepare_message(indicators_result, last_result)
        text_for_message_email = result_wma_to_markup(wma_result)
    else:
        last_result = update_last_result("stocks", wma_result)
        text_for_message_telegram = prepare_message(indicators_result, last_result)
        text_for_message_email = result_wma_to_markup(wma_result)
    logging.info(text_for_message_telegram)
    send_email(mail_username, mail_password, mail_username, text_for_message_email)
    send_telegram(text_for_message_telegram)
    logging.info("automatic job was executed at the " +
                 datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S'))


def send_email(user, pwd, recipient, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]

    message = MIMEMultipart("alternative")

    part = MIMEText(body, "html")
    message.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(user, pwd)
            server.sendmail(
                FROM, TO, message.as_string()
            )
        logging.info('successfully sent the mail')
    except:
        logging.info("failed to send mail")


def send_telegram(text):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(token,
                                                                                                     chatid, text)
    logging.info(url)
    try:
        requests.post(url, timeout=3)
    except:
        logging.info("make sure your telegram bot parameter was set correct!")


def run_job_stock():
    if working_period():
        list_for_update = list(stock_instruments.keys())
        execute(list_for_update)


def run_job_currency():
    if working_period():
        list_for_update = list(currency.keys())
        list_for_update.extend(goods.keys())
        execute(list_for_update)


def ping_yandex():
    try:
        logging.info("ping")
        urlopen(url_update)
    except:
        logging.info("could not ping ")


def working_period():
    week_no = datetime.today().weekday()
    if week_no < 5:
        return True
    else:
        return False


def united_jobs():
    run_job_currency()
    run_job_stock()


def start_upload_database():
    logging.info("start download quotes to database")
    create_dir("currency")
    create_dir("stock")
    create_dir("goods")
    start_database()
    # change to false for debug and true for working
    if True:
        list_for_update = list(all_instruments.keys())
        make_request(list_for_update, today_only=False)
        logging.info("database was uploaded")
    upload_database_status()


def clear_global_result():
    clear_lists_of_results()
    logging.info("clear result of preview analyse")


if __name__ == "__main__":
    init()
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Moscow'))
    scheduler.add_job(ping_yandex, 'interval', minutes=25)

    scheduler.add_job(clear_global_result, 'cron', hour=4, minute=19)
    scheduler.add_job(run_job_currency, 'cron', hour=4, minute=20)

    scheduler.add_job(clear_global_result, 'cron', hour=8, minute=19)
    scheduler.add_job(run_job_currency, 'cron', hour=8, minute=20)

    scheduler.add_job(clear_global_result, 'cron', hour=12, minute=19)
    scheduler.add_job(run_job_currency, 'cron', hour=12, minute=20)

    scheduler.add_job(clear_global_result, 'cron', hour=16, minute=32)
    scheduler.add_job(united_jobs, 'cron', hour=16, minute=33)

    scheduler.add_job(clear_global_result, 'cron', hour=20, minute=19)
    scheduler.add_job(run_job_currency, 'cron', hour=20, minute=20)

    scheduler.add_job(clear_global_result, 'cron', hour=00, minute=19)
    scheduler.add_job(run_job_currency, 'cron', hour=00, minute=20)


    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    t_2 = Thread(target=start_upload_database)
    t_2.start()
    send_email(mail_username, mail_password, mail_username, "App has been restarted")
    send_telegram("application has been restarted: {}"
                  .format(datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')))
    app.run(host='0.0.0.0', port=port)