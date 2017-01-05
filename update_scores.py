#!/usr/bin/python
import datetime as datetime
import os
import json

import MySQLdb

from sms_hunt import db_config
from match_updates.get_daily_matches import (check_for_daily_file, get_matches_from_db,
                                             get_live_matches, compare_matches_and_update,
                                             get_phone_numbers_and_send_sms)

# Get login for goal API
api_json_path = os.path.dirname(os.path.abspath(__file__))
api_json_path = os.path.abspath(os.path.join(os.sep, api_json_path, 'config_files', 'goal_api_config.json'))
with open(api_json_path) as api_connection_file:
    api_config = json.load(api_connection_file)
login_goal_api = api_config['login_goal_api']

# Establish database connection
db = MySQLdb.connect(host=db_config['host'],
                     user=db_config['user'],
                     passwd=db_config['password'],
                     db=db_config['database'])

# Calculate current date and time
i = datetime.datetime.now()
date_str = str(i.strftime('%d.%m.%Y'))
# date_str = '30.09.2016'
time_str = str(i.strftime('%H:%M'))
hour_str = i.strftime('%H')
minute_str = i.strftime('%M')

# Set competition
# 1204 = Premier League, 1229 = Bundesliga, 1005 = UEFA Champions League, 1007 = UEFA Europa League
# 1198 = Fa Cup, 1205 = Championship (2nd league)
competition = '1204,1229,1005,1007'
# if a minute requirement is needed, use this:
# minutes = ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18',
#           '20', '22', '24', '26', '28', '30', '32', '34', '36', '38',
#           '40', '42', '44', '46', '48', '50', '52', '54', '56', '58']

# Check if daily file exists. If not create one. Retrieve trigger times.
# manually
# file_path = 'match_updates/' + date_str + '.txt'
# automatically in cronjob
file_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(os.sep, file_path, 'match_updates/daily_files', date_str + '.txt')

# Check what to do based on txt file
match_day, trigger_times = check_for_daily_file(db, file_path, date_str, competition, login_goal_api)

# We have a match day today, and a valid hours and minute. Let's check the score
if (match_day and (hour_str in trigger_times)):  # or True:

    # Get matches in db
    db_matches = get_matches_from_db(db, date_str)
    if len(db_matches) == 0:
        print('no db matches found')
    # Get live matches
    live_matches = get_live_matches(date_str, competition, login_goal_api)
    if len(live_matches) == 0:
        print('no live matches found')

    # Compare both for score updates
    updated_matches = compare_matches_and_update(db, db_matches, live_matches)
    if len(updated_matches) > 0:
        print('matches with an update found!')
        for match in updated_matches:
            get_phone_numbers_and_send_sms(db, match)
    else:
        print('no update in any match')

# Commit and close database connection
db.commit()
db.close()
