#!/usr/bin/python
import datetime as datetime
import os
import json

from sms_hunt import db_config
from backend.db_class import DB
from match_updates.matchday import MatchDay
from match_updates.get_daily_matches import (check_for_daily_file, get_live_matches)

# from IPython import embed

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

# Establish database connection
db = DB(db_config)

# Calculate current date and time
i = datetime.datetime.now()
date_str = str(i.strftime('%d.%m.%Y'))
# date_str = '22.01.2017'
# time_str = str(i.strftime('%H:%M'))
hour_str = i.strftime('%H')
# hour_str = '17'
# minute_str = i.strftime('%M')

# Set competitions
# 1204 = Premier League, 1229 = Bundesliga, 1005 = UEFA Champions League, 1007 = UEFA Europa League
# 1198 = Fa Cup, 1205 = Championship (2nd league)
comp_id = '1204,1229,1005,1007'

# Check if daily file exists. If not create one. Retrieve trigger times.
file_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(os.sep, file_path, 'match_updates/daily_files', date_str + '.txt')

if stop_updates == 1:
    match_day = False
    trigger_times = []
else:
    match_day, trigger_times = check_for_daily_file(db, file_path, date_str, comp_id, login_goal_api)

# We have a match day today, and a valid hours and minute. Let's check the score
if match_day and (hour_str in trigger_times):  # or True:

    # Create MatchDay objects
    PL = MatchDay(db, date_str, '1204')
    BL = MatchDay(db, date_str, '1229')
    CL = MatchDay(db, date_str, '1005')
    EL = MatchDay(db, date_str, '1007')
    match_days = [PL, BL, CL, EL]

    # Get live matches
    live_matches = get_live_matches(date_str, comp_id, login_goal_api)
    if len(live_matches) == 0:
        print('no live matches found')

    # Update leagues and send sms
    for league in match_days:
        league.get_db_matches()
        league.set_live_matches(live_matches)
        league.find_updated_matches()
        league.send_sms_updates()

# Close database connection
db.close()
