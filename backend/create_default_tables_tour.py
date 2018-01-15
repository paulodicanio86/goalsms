import json
from db_class import DB
from db_functions import *
from make_default_tables import *

with open('config_files/db_config.json') as data_file:
    data_config = json.load(data_file)

db = DB(data_config)
db.init()

# ----- DEFAULT TOUR
# delete_table('messages', db)
# delete_table('valid', db)
# delete_table('active', db)
# delete_table('tour_name', db)
# delete_table('tour', db)
# delete_table('finished_tours', db)


# ----- DEFAULT GOALSMS
# delete_table('goalsms', db)
# make_default_table(db, 'tables/goalsms_table.json')
# delete_table('matches', db)
# make_default_table(db, 'tables/matches_table.json')

# make_default_tables_goalsms(db)

# ----- DEFAULT GOALSMS_TEST TABLES AND ROWS
delete_table('goalsms_test', db)
make_default_table(db, 'tables/goalsms_test_table.json')
reset_test_mode_game('matches', db)


db.close()
