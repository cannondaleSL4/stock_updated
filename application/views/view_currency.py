import os
import const

from flask import Blueprint, Markup, render_template, request, flash

from analyse import make_analyse, set_currensy_result
from download_update import *
from indicators_analyse import *
from prepare_markup import *
from const import *
from optimisation import get_best_params
from database import update_last_result

from prepare_markup import prepare_message

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')

view_currency = Blueprint('view_currency', __name__, template_folder=template_dir, static_folder=static_dir,
                          static_url_path=static_dir)


@view_currency.route("/")
def currency_page():
    # if not const.database_uploaded:
    #     flash("Please waiting database still uploading")

    return render_template('currency.html',
                           first_page="", second_page="/stock",
                           active="nav-link active",
                           not_active="nav-link",
                           instruments=sorted(currency.keys()))


@view_currency.route('/', methods=['POST'])
def currency_post():
    markup_result = dict()
    list_for_update = list(currency.keys())
    list_for_update.extend(list(goods.keys()))
    if request.form['form'] == 'Upload data':
        create_dir("currency")
        create_dir("goods")
        if len(request.form.getlist('instr')) == 0:
            clear_dir("currency")
            clear_dir("goods")
            result = "upload all instruments has been executed"
        else:
            list_for_update = request.form.getlist('instr')
            result = Markup("update for : </br> {} </br> quotes was been executed"
                            .format('</br>'.join(request.form.getlist('instr'))))
        make_request(list_for_update, today_only=False)
        flash(result)
    if request.form['form'] == 'Update data':
        create_dir("currency")
        create_dir("goods")
        if len(request.form.getlist('instr')) == 0:
            clear_dir("currency")
            clear_dir("goods")
            result = "update all instruments has been executed"
        else:
            list_for_update = request.form.getlist('instr')
            result = Markup("update for : </br> {} </br> quotes was been executed"
                            .format('</br>'.join(request.form.getlist('instr'))))
        make_request(list_for_update, today_only=True)
        flash(result)
    if request.form['form'] == 'Clear':
        create_dir("currency")
        clear_dir("currency")
        create_dir("goods")
        clear_dir("goods")
        result = "all data has been clear from {}/currency".format(UPLOAD_FOLDER)
        flash(result)

    if request.form['form'] == 'Analyse':
        result_of_analyse = make_analyse(list_for_update)
        indicators_result = result_of_analyse.get('indicators')
        result = indicators_result.get('wma 4 result')
        result_pattern = indicators_result.get('pattern')
        last_result = update_last_result("currency", result)
        # text_for_message_telegram = prepare_message(indicators_result, last_result)
        # from start import send_telegram
        # send_telegram(text_for_message_telegram)
        print(result)
        print(result_pattern)
        markup_result['wma 4'] = result_wma_to_markup(result)

    if request.form['form'] == 'Optimize':
        get_best_params(list_for_update)


    return render_template('currency.html',
                           first_page="", second_page="/stock",
                           active="nav-link active",
                           not_active="nav-link",
                           instruments=sorted(currency.keys()), markup_result=markup_result)