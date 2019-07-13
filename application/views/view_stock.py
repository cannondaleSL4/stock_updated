import os
import logging

from flask import Blueprint, Markup, render_template, request, flash
from analyse import make_analyse
from download_update import *
from indicators_analyse import *
from const import *

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
view_stock = Blueprint('view_stock', __name__, template_folder=template_dir, static_folder=static_dir)


@view_stock.route("/")
def stock_page():

    return render_template('stocks.html',
                           first_page="/currency", second_page="/",
                           active="nav-link",
                           not_active="nav-link active",
                           instruments=sorted(stock_instruments.keys()))


@view_stock.route('/', methods=['POST'])
def stock_post():
    list_for_update = list(stock_instruments.keys())
    result_for_html = ""
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
        result_for_html = result_of_analyse.result_for_html

        if not result_of_analyse:
            flash("has no any results")

    return render_template('stocks.html',
                           first_page="/currency", second_page="/",
                           active="nav-link",
                           not_active="nav-link active",
                           instruments=sorted(stock_instruments.keys()), markup_result=result_for_html)
