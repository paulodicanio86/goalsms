import json
import os

from flask import Flask

######################
# Load settings from json files
######################

# Open meta data file
meta_json_path = os.path.dirname(os.path.abspath(__file__))
meta_json_path = os.path.join(os.sep, meta_json_path, 'content', 'meta_data.json')

with open(meta_json_path) as meta_data_file:
    meta_data = json.load(meta_data_file)


# Open db connection file
db_json_path = os.path.dirname(os.path.abspath(__file__))
db_json_path = os.path.abspath(os.path.join(os.sep, db_json_path, os.pardir, 'db_connection.json'))

with open(db_json_path) as db_connection_file:
    db_config = json.load(db_connection_file)

# Open sms config file
sms_json_path = os.path.dirname(os.path.abspath(__file__))
sms_json_path = os.path.abspath(os.path.join(os.sep, sms_json_path, os.pardir, 'sms_config.json'))

with open(sms_json_path) as sms_config_file:
    sms_config = json.load(sms_config_file)


# Open sms content file
content_json_path = os.path.dirname(os.path.abspath(__file__))
content_json_path = os.path.join(os.sep, content_json_path, 'content', 'sms_content.json')

with open(content_json_path) as sms_content_file:
    sms_content = json.load(sms_content_file)


# Open keys config file
key_json_path = os.path.dirname(os.path.abspath(__file__))
key_json_path = os.path.abspath(os.path.join(os.sep, key_json_path, os.pardir, 'key_config.json'))

with open(key_json_path) as key_config_file:
    key_config = json.load(key_config_file)


# Open email config file
email_json_path = os.path.dirname(os.path.abspath(__file__))
email_json_path = os.path.join(os.sep, email_json_path, os.pardir, 'email_config.json')

with open(email_json_path) as email_config_file:
    email_config = json.load(email_config_file)


######################
# Initialise app
######################

# Flask initialisation
app = Flask(__name__)

# set the secret key. keep this really secret:
app.secret_key = key_config['app_secret_key']

# activate/make views ready
import sms_hunt.views
