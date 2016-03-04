from db_functions import *


def make_active_table(db, name = 'active'):
    columns = ['number', 'tour_id', 'valid_from', 'valid_to']
    types = ['var_char(255)', 'int', 'date', 'date']
    default_row = ['00447776031697', 0, '01/01/2016', '31/12/2016']

    make_table(name, db, columns, types, default_row)


def make_tour_name_table(db, name = 'tour_name_table'):
    columns = ['tour_id', 'tour_name']
    types = ['int', 'var_char(255)']
    default_row = [0, 'simple default tour']

    make_table(name, db, columns, types, default_row)


def make_tour_table(db, name = 'tour_table'):
    columns = ['tour_id', 'question_number', 'question', 'answer', 'help_1', 'help_2']
    types = ['int', 'int', 'var_char(255)', 'var_char(255)', 'var_char(255)', 'var_char(255)']
    row_1 = [0, 0, 'Welcome. 1+1?', '2', 'really?', 'two?']
    row_2 = [0, 1, 'surname of the president of the US?', 'Obama', 'not Trump!', '']

    make_table(name, db, columns, types)
    insert_array_to_table(name, db, columns, [row_1, row_2])
