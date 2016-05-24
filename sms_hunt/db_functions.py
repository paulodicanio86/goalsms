from backend.db_functions import execute_statement, update_row


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


# Query db to get column from a tour
def get_tour_column(db, column_name, tour_id, stage_number, table_name='tour'):
    sql_query = '''SELECT {column_name} FROM {table_name} WHERE tour_id = {tour_id}
                AND stage_number = {stage_number};'''

    sql_query = sql_query.format(column_name=column_name,
                                 table_name=table_name,
                                 tour_id=tour_id,
                                 stage_number=stage_number)
    return execute_statement(sql_query, db)


# Query db to get a stage
def get_answer(db, tour_id, stage_number, table_name='tour'):
    sql_query = '''SELECT answer FROM {table_name} WHERE tour_id = {tour_id}
                AND stage_number = {stage_number};'''

    sql_query = sql_query.format(table_name=table_name, tour_id=tour_id, stage_number=stage_number)
    return execute_statement(sql_query, db)


# Update active table
def update_active_table(db, column_name, column_value, phone_number, tour_id):
    table_name = "active"
    column_value = str(column_value)
    condition_1 = "phone_number='" + str(phone_number) + "'"
    condition_2 = "tour_id = " + str(tour_id)
    update_row(table_name, db, column_name, column_value, condition_1, condition_2)

# Update active table
def delete_from_active_table(db, phone_number, tour_id):
    table_name = "active"
    condition_1 = "phone_number='" + str(phone_number) + "'"
    condition_2 = "tour_id = " + str(tour_id)
    delete_row(table_name, db, condition_1, condition_2)
