import datetime as datetime
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


# Get daily matches
if not date_in_table(db, date_str):
    competition = '1204'  # Premier League
    add_daily_matches_to_db(db, date_str, competition='1204')


# Check every 2 minutes of a game after kick off time.
# Get matches in db
db_matches = get_matches_from_db(db, date_str)
if len(db_matches) > 0:
    print('no matches today')
    # STOP HERE NOW?

# Get live matches
live_matches = get_live_matches(date_str, competition='1204')

updated_matches = compare_matches_and_update(db, db_matches, live_matches)
# FIND PEOPLE SUBSCRIBED TO UPDATED MATCHES (localteamname + visitorteam_name)
# AND SEND SMS


embed()


# Commit and close database connection
db.commit()
db.close()
