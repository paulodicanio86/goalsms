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
    add_daily_matches_to_db(db, date_str=date_str, competition='1204')

# Get matches in db
db_matches = get_matches_from_db(db, date_str='03.01.2016')
if len(db_matches) > 0:
    print('no matches today')
# Now check
live_matches = get_live_matches(date_str='03.01.2016', competition='1204')

updated_matches = compare_matches_and_update(db_matches, live_matches)
# FIND PEOPLE SUBSCRIBED TO UPDATED MATCHES AND SEND SMS

embed()


# Commit and close database connection
db.commit()
db.close()
