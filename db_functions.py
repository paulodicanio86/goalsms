import pandas as pd
from string_functions import *


# Query db to select all
def select_all(table_name, db):
    sql_query = 'SELECT * FROM {table_name};'.format(table_name=table_name)
    return pd.read_sql(sql_query, con=db)


# Delete table
def delete_table(table_name, db):
    cursor = db.cursor()
    sql_query = 'DROP TABLE {table_name};'.format(table_name=table_name)
    cursor.execute(sql_query)
    db.commit()


# Create table
def create_table(table_name, db, columns_types):
    cursor = db.cursor()

    sql_query = '''CREATE TABLE {table_name} {columns_types};
                '''.format(table_name=table_name,
                           columns_types=columns_types)
    cursor.execute(sql_query)
    db.commit()


# Insert into table
def insert_into_table(table_name, db, columns, values):
    cursor = db.cursor()

    sql_query = '''INSERT INTO {table_name} {columns}
                    VALUES {values};
                '''.format(table_name=table_name,
                           columns=columns,
                           values=values)
    cursor.execute(sql_query)
    db.commit()


# Make a table and fill with a default row
def make_table(name, db, columns, types, default_row=None):
    # create table - assuming it doesn't exist yet
    column_types_str = convert_column_types_to_string(columns, types)
    create_table(name, db, column_types_str)

    # if a default row is given then fill it
    if default_row:
        columns_str = convert_columns_to_string(columns)
        default_row_str = convert_values_to_string(default_row)

        insert_into_table(name, db, columns_str, default_row_str)


# Insert array(s) into table
def insert_array_to_table(name, db, columns, rows):
    columns_str = convert_columns_to_string(columns)
    rows_str = ''

    # if just one row is given fill it
    if type(rows[0]) == str:
        rows_str = convert_values_to_string(rows)
    # for several rows these need to be joined up first
    elif type(rows[0]) == list:
        row_array = []
        for row in rows:
            row_array.append(convert_values_to_string(row))
        rows_str = join_rows(row_array)

    insert_into_table(name, db, columns_str, rows_str)


# Execute any SQL statement
def execute_statement(statement, db):
    return pd.read_sql(statement, con=db)
