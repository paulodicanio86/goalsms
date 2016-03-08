from db_functions import *


def make_valid_table(db, name='valid'):
    columns = ['phone_number', 'tour_id', 'valid_from', 'valid_to']
    types = ['VARCHAR(255)', 'INT', 'DATE', 'DATE']
    default_row = ['00447776031697', 0, '2016-03-31', '2016-12-31']

    make_table(name, db, columns, types, default_row)


def make_tour_name_table(db, name='tour_name_table'):
    columns = ['tour_id', 'tour_name']
    types = ['INT', 'VARCHAR(255)']
    default_row = [0, 'simple default tour']

    make_table(name, db, columns, types, default_row)


def make_tour_table(db, name='tour_table'):
    columns = ['tour_id', 'question_number', 'question', 'answer', 'help_1', 'help_2']
    types = ['INT', 'INT', 'VARCHAR(255)', 'VARCHAR(255)', 'VARCHAR(255)', 'VARCHAR(255)']
    row_1 = [0, 0, 'Welcome. 1+1?', '2', 'really?', 'two?']
    row_2 = [0, 1, 'surname of the president of the US?', 'Obama', 'not Trump!', '']

    make_table(name, db, columns, types)
    insert_array_to_table(name, db, columns, [row_1, row_2])


def make_dummy_table(db, name='dummy'):
    columns = ['phone_number', 'content', 'date', 'datetime']
    types = ['VARCHAR(255)', 'VARCHAR(255)', 'DATE', 'DATETIME']

    make_table(name, db, columns, types)


def get_dummy_table_columns():
    columns = ['phone_number', 'content', 'date', 'datetime']
    return convert_columns_to_string(columns)
