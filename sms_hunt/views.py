import os

from flask import request, send_from_directory, render_template, url_for, redirect
from sms_hunt import app, db_config, stripe_config, team_data, app_config
from sms import Sms
from models_tour import follow_tour
from models_goals import (default_dic, payments, currencies, leagues_list, teams_list, teams_dic,
                          country_leagues, variable_names, country_codes,
                          add_data_and_send_sms, charge_stripe)
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
    for league_name in country_leagues:
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
                           league_value=league_value
                           )


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
        values_dic[entry] = convert_entries(entry, values_dic[entry])
        valid_dic[entry] = validate_entries(entry, values_dic[entry], country_codes)

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

    if charge_stripe_flag == 1:
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
                          service_id)

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
# /sms_tour POST
#######################################
@app.route('/sms_tour', methods=['POST'])
def sms_tour():
    # Get data from POST request, add to sms class and validate
    sms = Sms(request.form['content'], request.form['sender'])
    sms.validate_content()
    sms.validate_sender()

    # Establish database connection
    db = DB(db_config)

    sms.validate_sms_and_get_tour(db)
    # Is the message valid?
    if not sms.is_valid:
        return ''

    # Save sms and follow a tour
    sms.save_message_to_db(db, 'messages')
    follow_tour(db, sms)

    # Commit and close database connection
    db.close()
    return ''


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
