import MySQLdb
import os
from flask import request, send_from_directory, render_template, url_for, redirect
import stripe

from sms_hunt import app, db_config, key_config, meta_data

from sms import Sms
from models_tour import follow_tour
from functions.validation_functions import convert_entries, validate_entries

stripe.api_key = key_config['stripe_secret_key']
key = key_config['stripe_publishable_key']
company = meta_data['company']
year = meta_data['year']
title = meta_data['title']

variable_names = ['team', 'phone_number', 'email']
country_code = '44'


#######################################
# / start page
#######################################
default_dic = {'valid': True,
               'value': ''
               }

payment = {'amount_pence': 300,
           'amount': 3.00,
           'currency': 'gbp',
           'currency_html': '&pound;'
           }


@app.route('/')
def start(team_dic=default_dic, phone_number_dic=default_dic, email_dic=default_dic):
    return render_template('start.html',
                           title=title,
                           company=company,
                           year=year,
                           phone_number=phone_number_dic,
                           email=email_dic,
                           payment=payment,
                           key=key
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
        values_dic[entry] = convert_entries(entry, values_dic[entry], country_code)
        valid_dic[entry] = validate_entries(entry, values_dic[entry])

    # reload if non-validated entries exist
    if False in valid_dic.values():
        false_values_dic = {}
        for entry in variable_names:
            false_values_dic[entry + '_dic'] = {'valid': valid_dic[entry],
                                       'value': values_dic[entry]
                                       }
        return start(**false_values_dic)
    else:
        return str(values_dic)
        #    return charge(payment=values, add_fee=get_boolean(request.form['add_fee']))


#######################################
# /about
#######################################
@app.route('/about/')
def about():
    return render_template('about.html',
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
