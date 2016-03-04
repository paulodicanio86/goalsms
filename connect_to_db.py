import MySQLdb
import json
from pprint import pprint
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

# default tables
make_active_table(db)
make_tour_name_table(db)
make_tour_table(db)
embed()
delete_table('active', db)
delete_table('tour_name_table', db)
delete_table('tour_table', db)
embed()


# play around with other things
columns = ['LastName', 'FirstName', 'Address', 'City']
types = ['varchar(255)', 'varchar(255)', 'varchar(255)', 'varchar(255)']

a = convert_column_types_to_string(columns, types)
create_table('dada', db, a)
embed()

values_1 = ['Mohan', 'Dida', 'Good street', 'London']
values_2 = ['Derek', 'Abba', 'Bad street', 'Hamburg']
b = convert_columns_to_string(columns)
c1 = convert_values_to_string(values_1)
c2 = convert_values_to_string(values_2)
c = join_rows([c1, c2])
embed()

insert_into_table('dada', db, b, c1)
insert_into_table('dada', db, b, c1)
insert_into_table('dada', db, b, c)

embed()

delete_table('dada', db)

db.commit()
db.close()
