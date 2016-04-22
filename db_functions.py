import pandas as pd
from string_functions import *


# Execute any SQL statement
def execute_statement(statement, db):
    return pd.read_sql(statement, con=db)


# Query db to select all
def select_all(table_name, db):
    sql_query = 'SELECT * FROM {table_name};'.format(table_name=table_name)
    return execute_statement(sql_query, db)


# Query db to see if entry is in valid table
def select_number_from_valid_table(db, phone_number, table_name='valid'):
    sql_query = '''SELECT * FROM {table_name} WHERE PHONE_NUMBER='{phone_number}'
                AND VALID_FROM <= CURDATE() AND CURDATE() <= VALID_TO and COMPLETED = 0;'''

    sql_query = sql_query.format(table_name=table_name, phone_number=phone_number)
    return execute_statement(sql_query, db)


# Query db to see if entry is in active table
def get_tour_from_active_table(db, phone_number, tour_id, table_name='active'):
    sql_query = '''SELECT * FROM {table_name} WHERE PHONE_NUMBER='{phone_number}'
                AND TOUR_ID = {tour_id};'''

    sql_query = sql_query.format(table_name=table_name, phone_number=phone_number, tour_id=tour_id)
    return execute_statement(sql_query, db)


# Query db to get the maximum stages of a tour
def get_maximum_stage_number(db, tour_id, table_name='tour'):
    sql_query = '''SELECT MAX(stage_number) AS total FROM {table_name} WHERE TOUR_ID={tour_id};'''

    sql_query = sql_query.format(table_name=table_name, tour_id=tour_id)
    return execute_statement(sql_query, db)


# Query db to get all stages of a tour
def get_all_stages(db, tour_id, table_name='tour'):
    sql_query = '''SELECT * FROM {table_name} WHERE TOUR_ID={tour_id};'''

    sql_query = sql_query.format(table_name=table_name, tour_id=tour_id)
    return execute_statement(sql_query, db)


# Query db to get a stage
def get_question(db, tour_id, stage_number, table_name='tour'):
    sql_query = '''SELECT question FROM {table_name} WHERE tour_id = {tour_id}
                AND stage_number = {stage_number};'''

    sql_query = sql_query.format(table_name=table_name, tour_id=tour_id, stage_number=stage_number)
    return execute_statement(sql_query, db)


# Query db to get a stage
def get_answer(db, tour_id, stage_number, table_name='tour'):
    sql_query = '''SELECT answer FROM {table_name} WHERE tour_id = {tour_id}
                AND stage_number = {stage_number};'''

    sql_query = sql_query.format(table_name=table_name, tour_id=tour_id, stage_number=stage_number)
    return execute_statement(sql_query, db)


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


# Update active table
def update_active_table(db, column_name, column_value, phone_number, tour_id):
    table_name = "active"
    column_value = str(column_value)
    condition_1 = "phone_number='" + str(phone_number) + "'"
    condition_2 = "tour_id = " + str(tour_id)
    update_row(table_name, db, column_name, column_value, condition_1, condition_2)


# Update row
def update_row(table_name, db, column_name, column_value, condition_1, condition_2):
    cursor = db.cursor()

    sql_query = '''SET SQL_SAFE_UPDATES = 0;
                   UPDATE {table_name}
                   SET {column_name}={column_value}
                   WHERE {condition_1} and {condition_2};
                   '''.format(table_name=table_name,
                              column_name=column_name,
                              column_value=column_value,
                              condition_1=condition_1,
                              condition_2=condition_2
                              )
    cursor.execute(sql_query)


# Update active table
def delete_from_active_table(db, phone_number, tour_id):
    table_name = "active"
    condition_1 = "phone_number='" + str(phone_number) + "'"
    condition_2 = "tour_id = " + str(tour_id)
    delete_row(table_name, db, condition_1, condition_2)


# Delete row
def delete_row(table_name, db, condition_1, condition_2):
    cursor = db.cursor()

    sql_query = '''SET SQL_SAFE_UPDATES = 0;
                   DELETE FROM {table_name}
                   WHERE {condition_1} and {condition_2};
                   '''.format(table_name=table_name,
                              condition_1=condition_1,
                              condition_2=condition_2
                              )
    cursor.execute(sql_query)


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
def make_table(name, db, columns, types, default_row=None, primary_key=None):
    # create table - assuming it doesn't exist yet
    column_types_str = convert_column_types_to_string(columns, types, primary_key)
    create_table(name, db, column_types_str)

    # if a default row is given then fill it
    if default_row:
        columns_str = convert_columns_to_string(columns)
        default_row_str = convert_values_to_string(default_row)

        insert_into_table(name, db, columns_str, default_row_str)


# Insert array(s) into table
def insert_array_to_table(name, db, columns, rows):
    columns_str = convert_columns_to_string(columns)

    # for several rows these need to be joined up first
    if type(rows[0]) == list:
        row_array = []
        for row in rows:
            row_array.append(convert_values_to_string(row))
        rows_str = join_rows(row_array)
    # if just one row is given fill it
    else:
        rows_str = convert_values_to_string(rows)

    insert_into_table(name, db, columns_str, rows_str)
