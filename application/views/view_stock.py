import os
import logging
import const


from flask import Blueprint, Markup, render_template, request, flash
from analyse import make_analyse, set_stocks_result
from download_update import *
from indicators_analyse import *
from const import *
from prepare_markup import *

from database import update_last_result

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
view_stock = Blueprint('view_stock', __name__, template_folder=template_dir, static_folder=static_dir)


@view_stock.route("/stock")
def stock_page():
    # if not const.database_uploaded:
    #     flash("Please waiting database still uploading")

    return render_template('stocks.html',
                           first_page="/", second_page="",
                           active="nav-link",
                           not_active="nav-link active",
                           instruments=sorted(stock_instruments.keys()))


@view_stock.route('/stock', methods=['POST'])
def stock_post():
    markup_result = dict()
    list_for_update = list(stock_instruments.keys())
    if request.form['form'] == 'Upload data':
        create_dir("stock")
        if len(request.form.getlist('instr')) == 0:
            clear_dir("stock")
            result = "update all instruments has been executed"
        else:
            list_for_update = request.form.getlist('instr')
            result = Markup("update for : </br> {} </br> quotes was been executed"
                            .format('</br>'.join(request.form.getlist('instr'))))
        make_request(list_for_update, today_only=False)
        flash(result)

    if request.form['form'] == 'Update data':
        create_dir("stock")
        if len(request.form.getlist('instr')) == 0:
            clear_dir("stock")
            result = "update all instruments has been executed"
        else:
            list_for_update = request.form.getlist('instr')
            result = Markup("update for : </br> {} </br> quotes was been executed"
                            .format('</br>'.join(request.form.getlist('instr'))))
        make_request(list_for_update, today_only=True)
        flash(result)

    if request.form['form'] == 'Clear':
        create_dir("stock")
        clear_dir("stock")
        result = "all data has been clear from {}/stock".format(UPLOAD_FOLDER)

        flash(result)

    if request.form['form'] == 'Analyse':
        result_of_analyse = make_analyse(list_for_update)
        indicators_result = result_of_analyse.get('indicators')
        result_wma = indicators_result.get('wma result')
        result_rsi = indicators_result.get('rsi result')
        result_williams = indicators_result.get('williams')
        # last_result = update_last_result("stock", result_wma)
        # text_for_message_telegram = prepare_message(indicators_result, last_result)
        # from start import send_telegram
        # send_telegram(text_for_message_telegram)
        if result_wma:
            logging.info(result_wma)
            markup_result['wma 4'] = result_wma_to_markup(result_wma)

        if result_rsi:
            logging.info(result_rsi)
            markup_result['rsi'] = result_wma_to_markup(result_rsi, "RSI")

        if result_williams:
            logging.info(result_williams)
            markup_result['williams'] = result_wma_to_markup(result_williams, "WILLIAMS")

        if not result_wma and not result_rsi:
            flash("has no any results")

    return render_template('stocks.html',
                           first_page="/", second_page="",
                           active="nav-link",
                           not_active="nav-link active",
                           instruments=sorted(stock_instruments.keys()), markup_result=markup_result)
