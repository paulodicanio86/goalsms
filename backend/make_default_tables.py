import os
import json

from db_functions import make_table, insert_array_to_table, encode_value


def make_default_tables_goalsms(db):
    make_default_table(db, 'tables/goalsms_table.json')
    make_default_table(db, 'tables/matches_table.json')


def make_default_tables_tour(db):
    make_default_table(db, 'tables/valid_table.json')
    make_default_table(db, 'tables/tour_name_table.json')
    make_default_table(db, 'tables/messages_table.json')
    make_default_table(db, 'tables/tour_table.json')
    make_default_table(db, 'tables/active_table.json')
    make_default_table(db, 'tables/finished_tours_table.json')


def make_default_table(db, file_name):
    # Open json file
    file_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(os.sep, file_path, file_name))

    with open(file_path, 'r') as fp:
        table_dic = json.load(fp)

    # Extract fields, encoding unicode to str
    name = table_dic['name'].encode('UTF8')
    columns = [x.encode('UTF8') for x in table_dic['columns']]
    types = [x.encode('UTF8') for x in table_dic['types']]

    # Test if a default row is given and if yes then include
    default_row = None
    keys = [x.encode('UTF8') for x in table_dic.keys()]
    if 'default_row' in keys:
        default_row = [encode_value(x) for x in table_dic['default_row']]
    # Test if a primary key is defined and add if yes
    primary_key = None
    if 'primary_key' in keys:
        primary_key = table_dic['primary_key'].encode('UTF8')

    # Make the actual table
    make_table(name, db, columns, types, default_row, primary_key)

    # If several default rows are given then include all of them
    if 'default_rows' in keys:
        rows = []
        for row in table_dic['default_rows']:
            rows.append([encode_value(x) for x in row])
        insert_array_to_table(name, db, columns, rows)



