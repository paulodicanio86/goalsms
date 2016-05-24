import json
import os

import MySQLdb
from flask import request

from sms_hunt import app

from sms import Sms
from models import follow_tour

# Open db connection strings
db_json_path = os.path.dirname(os.path.abspath(__file__))
db_json_path = os.path.abspath(os.path.join(os.sep, db_json_path, 'db_connection.json'))

with open(db_json_path) as db_connection_file:
    db_config = json.load(db_connection_file)


@app.route('/')
def start():
    return 'Hello World!'


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


@app.route('/show')
def show_sms_entries():
    from db_functions import select_all

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
