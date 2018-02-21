import json
import os

from flask import Flask
from flask_sslify import SSLify

######################
# Load settings from json files
######################

# Open app data file
app_json_path = os.path.dirname(os.path.abspath(__file__))
app_json_path = os.path.abspath(os.path.join(os.sep, app_json_path, os.pardir, 'config_files', 'app_config.json'))

with open(app_json_path) as app_config_file:
    app_config = json.load(app_config_file)
    sslify_flag = app_config['sslify_flag']

# Open team data file
team_json_path = os.path.dirname(os.path.abspath(__file__))
team_json_path = os.path.join(os.sep, team_json_path, 'content', 'team_data.json')

with open(team_json_path) as team_data_file:
    team_data = json.load(team_data_file)

# Open sms content file
content_json_path = os.path.dirname(os.path.abspath(__file__))
content_json_path = os.path.join(os.sep, content_json_path, 'content', 'sms_content.json')

with open(content_json_path) as sms_content_file:
    sms_content = json.load(sms_content_file)


# Open db config file
db_json_path = os.path.dirname(os.path.abspath(__file__))
db_json_path = os.path.abspath(os.path.join(os.sep, db_json_path, os.pardir, 'config_files', 'db_config.json'))

with open(db_json_path) as db_config_file:
    db_config = json.load(db_config_file)

# Open sms config file
sms_json_path = os.path.dirname(os.path.abspath(__file__))
sms_json_path = os.path.abspath(os.path.join(os.sep, sms_json_path, os.pardir, 'config_files', 'sms_config.json'))

with open(sms_json_path) as sms_config_file:
    sms_config = json.load(sms_config_file)


# Open keys config file
stripe_json_path = os.path.dirname(os.path.abspath(__file__))
stripe_json_path = os.path.abspath(
    os.path.join(os.sep, stripe_json_path, os.pardir, 'config_files', 'stripe_config.json'))

with open(stripe_json_path) as stripe_config_file:
    stripe_config = json.load(stripe_config_file)


# Open email config file
email_json_path = os.path.dirname(os.path.abspath(__file__))
email_json_path = os.path.join(os.sep, email_json_path, os.pardir, 'config_files', 'email_config.json')

with open(email_json_path) as email_config_file:
    email_config = json.load(email_config_file)


######################
# Initialise app
######################

# Flask initialisation
app = Flask(__name__)
if sslify_flag == 1:
    sslify = SSLify(app)

# set the secret key. keep this really secret:
app.secret_key = stripe_config['app_secret_key']

# activate/make views ready
import goalsms.views
