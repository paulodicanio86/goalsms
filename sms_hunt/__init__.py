import json
import os

from flask import Flask

######################
# Settings
######################
# general settings
# active = get_bool(os.environ['ONLINE']) # True/False = turn webpage on/off
company = 'Football SMS'
title = 'Match SMS'
domain = 'www.nicerpay.com'
company_email = 'info@nicerpay.com'
company_info_email = 'info@nicerpay.com'


# Open db connection strings
db_json_path = os.path.dirname(os.path.abspath(__file__))
db_json_path = os.path.abspath(os.path.join(os.sep, db_json_path, os.pardir, 'db_connection.json'))

with open(db_json_path) as db_connection_file:
    db_config = json.load(db_connection_file)

# Open sms config string file
sms_json_path = os.path.dirname(os.path.abspath(__file__))
sms_json_path = os.path.abspath(os.path.join(os.sep, sms_json_path, os.pardir, 'sms_config.json'))

with open(sms_json_path) as sms_config_file:
    sms_config = json.load(sms_config_file)


# Open sms content string file
content_json_path = os.path.dirname(os.path.abspath(__file__))
content_json_path = os.path.join(os.sep, content_json_path, 'content', 'sms_content.json')

with open(content_json_path) as sms_content_file:
    sms_content = json.load(sms_content_file)


# configure the email account
email_account = {
    'user': company_email,
    # 'password': os.environ['EMAIL_PWD'],
    'server': 'smtp.zoho.com',
    'port': 465,
    'from': company_email
}

# set the stripe keys
# stripe_keys = {
# 'secret_key': os.environ['SECRET_KEY'],
# 'publishable_key': os.environ['PUBLISHABLE_KEY']
# }


# Flask initialisation
app = Flask(__name__)

# set the secret key. keep this really secret:
app.secret_key = ''

# activate/make views ready
import sms_hunt.views
