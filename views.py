# import global functions

import json
import MySQLdb
from os import path, sep
from flask import request
from datetime import datetime
import pandas as pd

# import local functions
from app import app

from db_functions import *
from string_functions import *
from make_default_tables import *

# Open db connection strings
db_json = path.dirname(path.abspath(__file__))
db_json = path.abspath(path.join(sep, db_json, 'db_connection.json'))

with open(db_json) as data_file:
    data_config = json.load(data_file)


@app.route('/')
def start():
    return 'Hello World!'


@app.route('/sms', methods=['POST'])
def hello():
    # Get data from POST request and add date and datetime
    sender = str(request.form['sender'])
    content = str(request.form['content'])
    dt = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    d = '{:%Y-%m-%d}'.format(datetime.now())

    text_row = [sender, content, d, dt]

    # Establish database connection
    db = MySQLdb.connect(host=data_config['host'],
                         user=data_config['user'],
                         passwd=data_config['password'],
                         db=data_config['database'])

    # Add data to table
    insert_array_to_table('dummy', db, get_dummy_table_columns(), text_row)

    # Commit and close database connection
    db.commit()
    db.close()

    return ''


@app.route('/show')
def show_entries():
    # Establish database connection
    db = MySQLdb.connect(host=data_config['host'],
                         user=data_config['user'],
                         passwd=data_config['password'],
                         db=data_config['database'])
    df = select_all('dummy', db)

    # Commit and close database connection
    db.commit()
    db.close()

    return str(df)
