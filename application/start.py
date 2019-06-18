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
from prepare_markup import *
from views.view_currency import view_currency
from views.view_stock import view_stock
from const import *
from database import *
from prepare_markup import prepare_message

from optimisation import get_best_params

logging.basicConfig(level=logging.INFO)
port = int(os.environ.get('PORT', 8080))
url_update = os.environ.get('URL_UPDATE', 'https://app-dmba.herokuapp.com')


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(view_currency)
app.register_blueprint(view_stock)


def run_forest_run():
    get_best_params()


if __name__ == "__main__":
    init()
    t_1 = Thread(target=run_forest_run)
    t_1.start()
    app.run(host='0.0.0.0', port=port)
