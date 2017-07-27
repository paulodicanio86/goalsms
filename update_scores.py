#!/usr/bin/python
import datetime as datetime
import os
import json

from sms_hunt import db_config
from backend.db_class import DB
from match_updates.matchday import MatchDay
from match_updates.get_daily_matches import (daily_file_exists, read_daily_file, write_daily_file, get_live_matches)

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


# Calculate current date and time
i = datetime.datetime.now()
date_str = str(i.strftime('%d.%m.%Y'))
# date_str = '22.01.2017'
# time_str = str(i.strftime('%H:%M'))
hour_str = i.strftime('%H')
# hour_str = '17'
# minute_str = i.strftime('%M')

# Check if daily file exists. If not create one. Retrieve trigger times.
file_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(os.sep, file_path, 'match_updates/daily_files', date_str + '.txt')

# Set competitions
# 1204 = Premier League, 1229 = Bundesliga, 1005 = UEFA Champions League, 1007 = UEFA Europa League
# 1198 = Fa Cup, 1205 = Championship (2nd league)
comp_id = '1204,1229,1005,1007'
false_string = 'False - no matches today'
match_day = False
trigger_times = []

# Activate Test mode here
test_mode = True  # TEST MODE
if test_mode:
    date_str = '26.07.2017'


# If updates are allowed read the file to check
if stop_updates == 0:

    if daily_file_exists(file_path):
        # Daily file exists, so let's read the content
        match_day, trigger_times = read_daily_file(file_path, false_string)
    else:
        # Daily file doesn't exist, so let's create one

        # Initiate DB connection
        db = DB(db_config)
        db.init()
        write_daily_file(db, file_path, date_str, comp_id, login_goal_api, false_string)
        # Close DB connection
        db.close()


# We have a match day today, and a valid hours and minute. Let's check the score
if (match_day and (hour_str in trigger_times)) or test_mode:  # or True:

    # Initiate DB connection
    db = DB(db_config)
    db.init()

    # Create MatchDay objects
    PL = MatchDay(date_str, '1204', 'premier_league')
    BL = MatchDay(date_str, '1229', 'bundesliga')
    CL = MatchDay(date_str, '1005', 'champions_league')
    EL = MatchDay(date_str, '1007', 'europa_league')
    match_days = [PL, BL, CL, EL]

    # Get live matches
    live_matches = get_live_matches(date_str, comp_id, login_goal_api, test_mode)
    if len(live_matches) == 0:
        print('no live matches found')
    else:
        # Update leagues and send sms
        for league in match_days:
            if not league.check_all_games_finished(db):
                league.get_db_matches(db)
                league.set_live_matches(live_matches)
                league.find_updated_matches(db)
                league.send_sms_updates(db)
                if league.check_all_games_finished(db):
                    league.send_sms_eod_ft(db)

    # Close DB connection
    db.close()
