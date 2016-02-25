# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)


db = []

@app.route('/')
def start():
    return 'Hello World!'


@app.route('/sms')
def add_entry():
    db.append('entry')
    return('SMS received')

@app.route('/show')
def show_entries():
    return(','.join(db))

@app.route('/clear')
def clear():
    db = []
    return('cleared')

if __name__ == '__main__':
    app.run()