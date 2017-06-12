import json
from db_class import DB
from db_functions import *
from make_default_tables import *

from IPython import embed

with open('config_files/db_config.json') as data_file:
    data_config = json.load(data_file)

db = DB(data_config)

# delete_table('messages', db)
# delete_table('valid', db)
# delete_table('active', db)
# delete_table('tour_name', db)
# delete_table('tour', db)
# delete_table('finished_tours', db)
# make_default_tables_tour(db)
# embed()

delete_table('goalsms', db)
make_default_table(db, 'tables/goalsms_table.json')
delete_table('matches', db)
make_default_table(db, 'tables/matches_table.json')

# make_default_tables_goalsms(db)
# make_default_tables_tour(db)

db.close()
