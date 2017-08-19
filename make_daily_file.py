#!/usr/bin/python
import datetime as datetime
import os
import json

from sms_hunt import db_config
from backend.db_class import DB
from match_updates.get_daily_matches import (daily_file_exists, write_daily_file)

# Open app data file
app_json_path = os.path.dirname(os.path.abspath(__file__))
app_json_path = os.path.abspath(os.path.join(os.sep, app_json_path, 'config_files', 'app_config.json'))

with open(app_json_path) as app_config_file:
    app_config = json.load(app_config_file)
stop_updates = app_config['stop_updates']

# Get login for goal API
api_json_path = os.path.dirname(os.path.abspath(__file__))
api_json_path = os.path.abspath(os.path.join(os.sep, api_json_path, 'config_files', 'goal_api_config.json'))
with open(api_json_path) as api_connection_file:
    api_config = json.load(api_connection_file)
login_goal_api = api_config['login_goal_api']

#########################################

# Set competitions
# 1204 = Premier League, 1229 = Bundesliga, 1005 = UEFA Champions League, 1007 = UEFA Europa League
# 1198 = Fa Cup, 1205 = Championship (2nd league)
# comp_id = '1204,1229,1005,1007'
comp_id = '1204,1229'

# Run configuration settings
test_mode = False  # False
false_string = 'False - no matches today'

#########################################

# Calculate current date and time
time_obj = datetime.datetime.now()
date_str = str(time_obj.strftime('%d.%m.%Y'))
# Activate Test mode here
if test_mode:
    date_str = '26.07.2017'
hour_str = time_obj.strftime('%H')
minute_str = time_obj.strftime('%M')

file_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(os.sep, file_path, 'match_updates/daily_files', date_str + '.txt')

# Check if daily file exists. If not create one.
if stop_updates == 0 and not daily_file_exists(file_path):
    # Daily file doesn't exist, so let's create one
    # Initiate DB connection
    db = DB(db_config)
    db.init()
    text = write_daily_file(db, file_path, date_str, comp_id, login_goal_api, false_string)
    # Close DB connection
    db.close()
    print('Created daily file: ' + text + ' (for ' + date_str + ')')
