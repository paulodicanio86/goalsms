import datetime as datetime
import os as os
import MySQLdb

from sms_hunt import db_config
from match_updates.functions.db_functions import date_in_table
from match_updates.get_daily_matches import (add_daily_matches_to_db, get_matches_from_db,
                                             get_live_matches, compare_matches_and_update)

from IPython import embed

# Establish database connection
db = MySQLdb.connect(host=db_config['host'],
                     user=db_config['user'],
                     passwd=db_config['password'],
                     db=db_config['database'])

# Calculate current date and time
i = datetime.datetime.now()
date_str = str(i.strftime('%d.%m.%Y'))
time_str = str(i.strftime('%H:%M'))
hour_int = int(i.strftime('%H'))
minute_int = int(i.strftime('%M'))

# check if daily file exists. if not create one.
match_day = False
file_path = 'match_updates/' + date_str + '.txt'

# File exists
if os.path.isfile(file_path):
    f = open(file_path, 'r')
    content = f.readline()

    if content == 'False':
        match_day = False
    else:
        match_day = True
        # Retrieve more information
        ko_times = content  # .split('.')
        print('Kick of times are: ', content)
    f.close()
# File does not exist
else:
    f = open(file_path, 'w')

    if not date_in_table(db, date_str):
        competition = '1204'  # Premier League
        add_daily_matches_to_db(db, date_str, competition='1204')

    # Now check if there are any matches today:
    if date_in_table(db, date_str):
        f.write('True')  # Fill in more information here?
    else:
        f.write('False')

    f.close()

# We have a match day today
if match_day:

    # Is current time during matches? then continue

    # Check every 2 minutes of a game after kick off time.

    # Get matches in db
    db_matches = get_matches_from_db(db, date_str)
    if len(db_matches) > 0:
        print('no matches found')
    # Get live matches
    live_matches = get_live_matches(date_str, competition='1204')

    # Compare both for score updates
    updated_matches = compare_matches_and_update(db, db_matches, live_matches)


    # FIND PEOPLE SUBSCRIBED TO UPDATED MATCHES (localteamname + visitorteam_name)
    # AND SEND SMS


    embed()


# Commit and close database connection
db.commit()
db.close()
