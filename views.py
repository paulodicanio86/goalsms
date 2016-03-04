from app import app
from flask import request

db = []


@app.route('/')
def start():
    return 'Hello World!'


@app.route('/sms', methods=['POST'])
def hello():
    sender = request.form['sender']
    content = request.form['content']

    db.append(sender)
    db.append(content)
    return ''


@app.route('/show')
def show_entries():
    return ','.join(db)


@app.route('/clear')
def clear():
    db = []
    return 'cleared'
