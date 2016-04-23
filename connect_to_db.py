import json
from pprint import pprint
import MySQLdb
from IPython import embed

from db_functions import *
from string_functions import *
from make_default_tables import *

with open('db_connection.json') as data_file:
    data_config = json.load(data_file)
pprint(data_config)

db = MySQLdb.connect(host=data_config['host'],
                     user=data_config['user'],
                     passwd=data_config['password'],
                     db=data_config['database'])

delete_table('messages', db)
delete_table('valid', db)
delete_table('active', db)
delete_table('tour_name', db)
delete_table('tour', db)
# default tables
make_default_tables(db)
embed()
# delete_table('tour_name', db)
# delete_table('tour', db)
# delete_table('dummy', db)
# delete_table('valid', db)
# delete_table('active', db)
# embed()


db.commit()
db.close()
