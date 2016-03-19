# import global functions

import json
import MySQLdb
import os
from flask import request
from datetime import datetime
import pandas as pd

# import local functions
from app import app

from sms import Sms
from tour import *
from db_functions import *
from string_functions import *
from make_default_tables import get_table_columns

# Open db connection strings
db_json_path = os.path.dirname(os.path.abspath(__file__))
db_json_path = os.path.abspath(os.path.join(os.sep, db_json_path, 'db_connection.json'))

with open(db_json_path) as db_connection_file:
    db_config = json.load(db_connection_file)


@app.route('/')
def start():
    return 'Hello World!'


@app.route('/sms', methods=['POST'])
def hello():
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

    follow_tour(db, sms)

    # Get message meta data
    message = sms.get_message_array()

    # Get date and datetime
    dt = datetime.now()
    dt_str = '{:%Y-%m-%d %H:%M:%S}'.format(dt)
    d_str = '{:%Y-%m-%d}'.format(dt)
    #  store the message
    text_row = [sms.sender, sms.content, d_str, dt_str]
    # Add message to dummy table
    insert_array_to_table('dummy', db, get_table_columns('tables/dummy_table.json'), text_row)

    # Commit and close database connection
    db.commit()
    db.close()
    return ''


@app.route('/show')
def show_entries():
    # Establish database connection
    db = MySQLdb.connect(host=db_config['host'],
                         user=db_config['user'],
                         passwd=db_config['password'],
                         db=db_config['database'])
    df = select_all('dummy', db)

    # Commit and close database connection
    db.commit()
    db.close()

    return str(df)
