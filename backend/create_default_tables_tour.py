import json
import MySQLdb
from IPython import embed

from db_functions import *
from make_default_tables import *

with open('db_connection.json') as data_file:
    data_config = json.load(data_file)

db = MySQLdb.connect(host=data_config['host'],
                     user=data_config['user'],
                     passwd=data_config['password'],
                     db=data_config['database'])

# delete_table('messages', db)
# delete_table('valid', db)
# delete_table('active', db)
# delete_table('tour_name', db)
# delete_table('tour', db)
# delete_table('finished_tours', db)
# make_default_tables_tour(db)
# embed()
# delete_table('tour_name', db)
# delete_table('tour', db)
# delete_table('dummy', db)
# delete_table('valid', db)
# delete_table('active', db)
# embed()

delete_table('eurosms', db)
make_default_tables_eurosms(db)

db.commit()
db.close()
