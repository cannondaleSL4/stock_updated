import logging
import os
import const

from flask import Blueprint, Markup, render_template, request, flash

from analyse import make_analyse
from download_update import *
from const import *
from optimisation import get_best_params
from indicators_analyse import *


template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')

view_currency = Blueprint('view_currency', __name__, template_folder=template_dir, static_folder=static_dir,
                          static_url_path=static_dir)


@view_currency.route("/currency")
def currency_page():

    return render_template('currency.html',
                           first_page="", second_page="/",
                           active="nav-link active",
                           not_active="nav-link",
                           instruments=sorted(currency.keys()))


@view_currency.route('/currency', methods=['POST'])
def currency_post():
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

    if request.form['form'] == 'Optimize':
        get_best_params(list_for_update)

    if request.form['form'] == 'Analyse':
        result_of_analyse = make_analyse(list_for_update)

        if not result_of_analyse:
            flash("has no any results")

    return render_template('currency.html',
                           first_page="", second_page="/",
                           active="nav-link active",
                           not_active="nav-link",
                           instruments=sorted(currency.keys()), markup_result=result_of_analyse.result_for_html)