# get daily matches

import datetime as datetime
import os

from match import Match

from IPython import embed


i = datetime.datetime.now()
date_str = str(i.strftime('%d.%m.%Y'))
time_str = str(i.strftime('%H:%M'))


team_H = 'arsenal'
team_A = 'chelsea'
ko_time = '13:30'


directory = 'match_days/' + date_str
if not os.path.exists(directory):
    os.makedirs(directory)


embed()




# check how many users there are per match subscribed

# have final list of matches and users
