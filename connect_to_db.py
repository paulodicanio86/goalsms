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

delete_table('dummy', db)
# default tables
make_default_tables(db)
embed()
delete_table('valid', db)
delete_table('tour_name', db)
delete_table('tour', db)
#delete_table('dummy', db)
# embed()

# play around with other things
a = """
columns = ['LastName', 'FirstName', 'Address', 'City']
types = ['varchar(255)', 'varchar(255)', 'varchar(255)', 'varchar(255)']

a = convert_column_types_to_string(columns, types)
create_table('dada', db, a)
#embed()

values_1 = ['Mohan', 'Dida', 'Good street', 'London']
values_2 = ['Derek', 'Abba', 'Bad street', 'Hamburg']
b = convert_columns_to_string(columns)
c1 = convert_values_to_string(values_1)
c2 = convert_values_to_string(values_2)
c = join_rows([c1, c2])
#embed()

insert_into_table('dada', db, b, c1)
insert_into_table('dada', db, b, c1)
insert_into_table('dada', db, b, c)

#embed()
delete_table('dada', db)
"""

db.commit()
db.close()
