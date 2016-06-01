import MySQLdb
import os
from flask import request, send_from_directory, render_template, url_for
# import stripe

from sms_hunt import app, db_config  # , stripe_keys

from sms import Sms
from models_tour import follow_tour


# stripe.api_key = stripe_keys['secret_key']


#######################################
# / start page
#######################################
@app.route('/')
def start():
    return render_template('layout.html',
                           title='Match SMS',
                           company='Football SMS',
                           year='2016'
                           )


#######################################
# /about
#######################################
@app.route('/about/')
def about():
    return render_template('about.html',
                           title='Match SMS',
                           company='company',
                           year='2016'
                           )


#######################################
# /contact
#######################################
@app.route('/contact/')
def contact():
    return render_template('contact.html',
                           title='Match SMS',
                           company='company',
                           year='2016'
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
# Not really needed....
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
                           title='Match SMS',
                           company='Football SMS',
                           year='2016'), 404


#######################################
# Favicon (also done in layout.html)
#######################################
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'ico/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')
