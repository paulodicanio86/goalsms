from flask import request
from datetime import datetime
import json
import MySQLdb

from app import app

from db_functions import *
from string_functions import *
from make_default_tables import *

with open('db_connection.json') as data_file:
    data_config = json.load(data_file)

db = MySQLdb.connect(host=data_config['host'],
                     user=data_config['user'],
                     passwd=data_config['password'],
                     db=data_config['database'])

db2 = []


@app.route('/')
def start():
    return 'Hello World!'


@app.route('/sms', methods=['POST'])
def hello():
    sender = request.form['sender']
    content = request.form['content']

    DT = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    D = '{:%Y-%m-%d}'.format(datetime.now())

    text_row = [sender, content, D, DT]
    text_row_str = convert_values_to_string(text_row)

    insert_into_table('dummy', db, get_dummy_table_columns(), text_row_str)

    db2.append(sender)
    db2.append(content)
    return None


@app.route('/show')
def show_entries():
    return ','.join(db)


@app.route('/clear')
def clear():
    db = []
    return 'cleared'
