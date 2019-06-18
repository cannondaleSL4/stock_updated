import logging
import os
import time
import atexit
from threading import Thread
from urllib.request import urlopen
from datetime import datetime

import pytz
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from prepare_markup import *
from views.view_currency import view_currency
from views.view_stock import view_stock
from const import *
from database import *
from prepare_markup import prepare_message

from optimisation import get_best_params

logging.basicConfig(level=logging.INFO)
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
port = int(os.environ.get('PORT', 8080))
url_update = os.environ.get('URL_UPDATE', 'https://app-dmba.herokuapp.com')


if mail_username and mail_password:
    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": mail_username,
        "MAIL_PASSWORD": mail_password
    }

mail = Mail()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(view_currency)
app.register_blueprint(view_stock)
if mail_username and mail_password:
    app.config.update(mail_settings)
    Bootstrap(app)
    mail = Mail(app)


def run_forest_run():
    get_best_params()


if __name__ == "__main__":
    init()
    t_1 = Thread(target=run_forest_run)
    t_1.start()
    app.run(host='0.0.0.0', port=port)
