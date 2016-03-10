# import global functions

import json
import MySQLdb
import os
from flask import request
from datetime import datetime
import pandas as pd

# import local functions
from app import app

from db_functions import *
from string_functions import *
from make_default_tables import *

# Open db connection strings
db_json_path = os.path.dirname(os.path.abspath(__file__))
db_json_path = os.path.abspath(os.path.join(os.sep, db_json_path, 'db_connection.json'))

with open(db_json_path) as db_connection_file:
    data_config = json.load(db_connection_file)


@app.route('/')
def start():
    return 'Hello World!'


@app.route('/sms', methods=['POST'])
def hello():
    # Get data from POST request and add date and datetime
    sender = str(request.form['sender'])
    content = str(request.form['content'])
    # Validate message content here and remove bad characters
    content = validate_content(content)

    # Establish database connection
    db = MySQLdb.connect(host=data_config['host'],
                         user=data_config['user'],
                         passwd=data_config['password'],
                         db=data_config['database'])

    # Get date and datetime to store the message
    dt = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    d = '{:%Y-%m-%d}'.format(datetime.now())
    text_row = [sender, content, d, dt]
    # Add message to dummy table
    insert_array_to_table('dummy', db, get_table_columns('tables/dummy_table.json'), text_row)

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
