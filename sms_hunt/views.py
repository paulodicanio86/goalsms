import MySQLdb
import os
from flask import request, send_from_directory, render_template, url_for, redirect

from sms_hunt import app, db_config, stripe_config, team_data, app_config

from sms import Sms
from models_tour import follow_tour
from models_goals import (default_dic, payment_1, payment_2, payment_3, leagues_list, teams_list, teams_dic,
                          main_leagues, variable_names, default_country_code, country_codes,
                          add_data_and_send_sms, charge_stripe)
from functions.validation_functions import convert_entries, validate_entries

if stripe_config['stripe_test_flag'] == 0:
    key = stripe_config['stripe_live_publishable_key']
    secret_key = stripe_config['stripe_live_secret_key']
else:
    key = stripe_config['stripe_test_publishable_key']
    secret_key = stripe_config['stripe_test_secret_key']

company = app_config['company']
year = app_config['year']
title = app_config['title']


#######################################
# / start page
#######################################
@app.route('/')
def start(phone_number_dic=default_dic,
          name_dic=default_dic, team_valid=True):
    return render_template('start.html',
                           title=title,
                           company=company,
                           year=year,
                           payment=payment_1,
                           key=key,
                           phone_number=phone_number_dic,
                           name=name_dic,
                           leagues=leagues_list,
                           teams=teams_list,
                           team_valid=team_valid
                           )


#######################################
# / start page for each team
#######################################
@app.route('/team/<team_value>/')
def single_team(team_value,
                phone_number_dic=default_dic,
                name_dic=default_dic):
    team_value = team_value.lower()
    if team_value not in teams_dic.keys():
        return redirect(url_for('page_not_found_manual'))

    league_value = ''
    for league_name in main_leagues:
        if team_value in team_data[league_name]:
            league_value = league_name

    return render_template('team.html',
                           title=title,
                           company=company,
                           year=year,
                           payment=payment_1,
                           key=key,
                           phone_number=phone_number_dic,
                           name=name_dic,
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
    # get the values from the post
    values_dic = {}
    valid_dic = {}

    # fill, convert and validate entries
    for entry in variable_names:
        values_dic[entry] = request.form[entry]
        values_dic[entry] = convert_entries(entry, values_dic[entry], default_country_code)
        valid_dic[entry] = validate_entries(entry, values_dic[entry], country_codes)

    # reload if non-validated entries exist
    if False in valid_dic.values():
        false_values_dic = {}
        for entry in variable_names:
            false_values_dic[entry + '_dic'] = {'valid': valid_dic[entry],
                                                'value': values_dic[entry]}
        if request.form['single_team'] == 'False':
            return start(**false_values_dic)
        else:
            return single_team(request.form['team'], **false_values_dic)

    # if no team is chosen reload the base page with validated entries
    if request.form['team'] == 'no_team':
        chosen_values_dic = {}
        for entry in variable_names:
            chosen_values_dic[entry + '_dic'] = {'valid': valid_dic[entry],
                                                 'value': values_dic[entry]}
        chosen_values_dic['team_valid'] = False
        return start(**chosen_values_dic)

    # take card payment
    charge_successful = charge_stripe(payment=payment_1,
                                      email=request.form['stripeEmail'],
                                      secret_key=secret_key,
                                      stripe_token=request.form['stripeToken'],
                                      phone_number=values_dic['phone_number'])
    if not charge_successful:
        print(request.form['service'])
        print(request.form['stripeName'])
        return redirect(url_for('failure'))

    # Establish database connection
    db = MySQLdb.connect(host=db_config['host'],
                         user=db_config['user'],
                         passwd=db_config['password'],
                         db=db_config['database'])

    add_data_and_send_sms(db,
                          values_dic['phone_number'],
                          request.form['stripeEmail'],
                          request.form['team'],
                          request.form['league'],
                          request.form['stripeName'],
                          teams_dic[request.form['team']],
                          request.form['service'])

    # Commit and close database connection
    db.commit()
    db.close()

    # go to success page
    return redirect(url_for('success'))


#######################################
# /success
#######################################
@app.route('/success/')
def success():
    return render_template('success.html',
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
@app.route('/about/')
def about():
    return render_template('about.html',
                           title=title,
                           company=company,
                           year=year,
                           payment=payment_1
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
    db = MySQLdb.connect(host=db_config['host'],
                         user=db_config['user'],
                         passwd=db_config['password'],
                         db=db_config['database'])

    sms.validate_sms_and_get_tour(db)
    # Is the message valid?
    if not sms.is_valid:
        return ''

    # Save sms and follow a tour
    sms.save_message_to_db(db, 'messages')
    follow_tour(db, sms)

    # Commit and close database connection
    db.commit()
    db.close()
    return ''


#######################################
# For control purposes
#######################################
@app.route('/show')
def show_sms_entries():
    from backend.db_functions import select_all

    # Establish database connection
    db = MySQLdb.connect(host=db_config['host'],
                         user=db_config['user'],
                         passwd=db_config['password'],
                         db=db_config['database'])
    df = select_all('messages', db)

    # Commit and close database connection
    db.commit()
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
