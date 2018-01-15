import os
from datetime import datetime

from flask import request, send_from_directory, render_template, url_for, redirect
from goalsms import app, db_config, stripe_config, team_data, app_config
from models_goals import (default_dic, payments, currencies, leagues_dic, leagues_list, prefixes, prefixes_list,
                          services_dic, teams_list, teams_dic, variable_names, add_data_and_send_sms, charge_stripe)
from backend.db_class import DB
from functions.validation_functions import convert_entries, validate_entries

if stripe_config['stripe_test_flag'] == 0:
    key = stripe_config['stripe_live_publishable_key']
    secret_key = stripe_config['stripe_live_secret_key']
else:
    key = stripe_config['stripe_test_publishable_key']
    secret_key = stripe_config['stripe_test_secret_key']

charge_stripe_flag = stripe_config['charge_stripe_flag']

company = app_config['company']
year = app_config['year']
title = app_config['title']


#######################################
# / start page
#######################################
@app.route('/')
def start(phone_number_dic=default_dic):
    return render_template('start.html',
                           title=title,
                           company=company,
                           year=year,
                           payments=payments,
                           currencies=currencies,
                           key=key,
                           phone_number=phone_number_dic,
                           leagues=leagues_list,
                           services=services_dic,
                           prefixes=prefixes_list,
                           teams=teams_list
                           )


#######################################
# / start page for each team
#######################################
@app.route('/team/<team_value>/')
def single_team(team_value,
                phone_number_dic=default_dic):
    team_value = team_value.lower()

    if team_value not in teams_dic.keys():
        return redirect(url_for('page_not_found_manual'))

    # Find out the right league
    league_value = ''
    for league_name in leagues_dic.keys():
        if team_value in team_data[league_name]:
            league_value = league_name

    return render_template('team.html',
                           title=title,
                           company=company,
                           year=year,
                           payments=payments,
                           key=key,
                           phone_number=phone_number_dic,
                           team=teams_dic[team_value],
                           team_value=team_value,
                           league_value=league_value,
                           services=services_dic,
                           prefixes=prefixes_list
                           )


#######################################
# / daily file for each day
#######################################
@app.route('/daily/<daily_file_name>/')
def daily_file_check(daily_file_name):
    file_path = os.path.dirname('/home/pschaack/')
    file_path = os.path.abspath(os.path.join(os.sep, file_path, 'goalsms/match_updates/daily_files/', daily_file_name))

    time_obj = datetime.now()
    time_str = str(time_obj.strftime('%H:%M'))

    if os.path.isfile(file_path):
        f = open(file_path, 'r')
        content = f.readline()
        f.close()
        return content + ' at: ' + time_str
    else:
        return 'file does not exist: ' + daily_file_name + ' at: ' + time_str


#######################################
# /verify
#######################################
@app.route('/verify', methods=['GET'])
def verify_get():
    return redirect(url_for('start'))


@app.route('/verify', methods=['POST'])
def verify_post():
    # get the values from the POST request
    phone_number = request.form['phone_number']
    prefix = request.form['prefix']
    email = request.form['stripeEmail']
    name = request.form['stripeName']
    stripe_token = request.form['stripeToken']
    service_amount = request.form['service_amount']
    currency = request.form['currency']

    team_id = request.form['team_chosen']
    team_name = teams_dic[team_id]
    league_id = request.form['league_chosen']
    service_id = request.form['service_chosen']

    single_team_value = request.form['single_team']

    # check if a team was chosen
    if team_name == '':
        team_selected_bool = False
    else:
        team_selected_bool = True

    # print(name,
    #      email,
    #      phone_number,
    #      team_id,
    #      team_name,
    #      league_id,
    #      service_id,
    #      stripe_token,
    #      service_amount,
    #      currency,
    #      team_selected_bool)

    # fill, convert and validate entries
    values_dic = {}
    valid_dic = {}

    for entry in variable_names:
        values_dic[entry] = request.form[entry]
        values_dic[entry] = convert_entries(entry, values_dic[entry], prefix)
        valid_dic[entry] = validate_entries(entry, values_dic[entry], prefixes)

    # reload if non-validated entries exist
    if False in valid_dic.values() or not team_selected_bool:
        reload_values_dic = {}
        for entry in variable_names:
            reload_values_dic[entry + '_dic'] = {'valid': valid_dic[entry],
                                                 'value': values_dic[entry]}

        if single_team_value == 'False':
            return start(**reload_values_dic)
        else:
            return single_team(team_id, **reload_values_dic)

    # all entries are valid now, re-assign:
    phone_number = values_dic['phone_number']

    # print(name,
    #      email,
    #      phone_number,
    #      team_id,
    #      team_name,
    #      league_id,
    #      service_id,
    #      team_selected_bool)

    # take card payment
    payment = {'amount_integer': service_amount,
               'currency': currency}

    # default table is the TEST table.
    table_name = 'goalsms_test'

    if charge_stripe_flag == 1:
        # only if a real charge happens, use the real table (and not TEST table)
        table_name = 'goalsms'

        charge_successful = charge_stripe(payment=payment,
                                          email=email,
                                          secret_key=secret_key,
                                          stripe_token=stripe_token,
                                          phone_number=phone_number)
        if not charge_successful:
            print(service_id)
            print(name)
            return redirect(url_for('failure'))

    # Establish database connection
    db = DB(db_config)
    db.init()

    # Add data to DB and send sms
    add_data_and_send_sms(db,
                          name,
                          email,
                          phone_number,
                          team_id,
                          team_name,
                          league_id,
                          service_id,
                          table_name)

    # Close database connection
    db.close()

    # go to success page
    return success(service_amount, currency)


#######################################
# /success
#######################################
@app.route('/success/')
def success(value=0, currency='GBP'):
    return render_template('success.html',
                           value=(float(value) / 100.00),
                           currency=currency.upper(),
                           title=title,
                           company=company,
                           year=year
                           )


#######################################
# /failure
#######################################
@app.route('/failure/')
def failure():
    return render_template('failure.html',
                           title=title,
                           company=company,
                           year=year,

                           )


#######################################
# /about
#######################################
@app.route('/services/')
def services():
    return render_template('services.html',
                           title=title,
                           company=company,
                           year=year
                           )


#######################################
# /contact
#######################################
@app.route('/contact/')
def contact():
    return render_template('contact.html',
                           title=title,
                           company=company,
                           year=year
                           )


#######################################
# For control purposes
#######################################
@app.route('/show')
def show_sms_entries():
    from backend.db_functions import select_all

    # Establish database connection
    db = DB(db_config)
    df = select_all('messages', db)

    # Commit and close database connection
    db.close()

    return str(df)


#######################################
# Error 404
#######################################
@app.route('/404')
def page_not_found_manual():
    return render_template('404.html',
                           title=title,
                           company=company,
                           year=year)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',
                           title=title,
                           company=company,
                           year=year), 404


#######################################
# Favicon (also done in layout.html)
#######################################
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'ico/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')
