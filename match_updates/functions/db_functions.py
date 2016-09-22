from backend.db_functions import execute_statement, update_row


# Query db to check if date is in table
def date_in_table(db, date_str, table_name='matches'):
    sql_query = '''SELECT DISTINCT date_str FROM {table_name} WHERE date_str='{date_str}';'''
    sql_query = sql_query.format(table_name=table_name, date_str=date_str)
    result = execute_statement(sql_query, db)

    if len(result) > 0:
        return True
    else:
        return False


# Query to return all matches on the day
def get_matches(db, date_str, table_name='matches'):
    sql_query = '''SELECT date_str, localteam_name, visitorteam_name, localteam_score,
                visitorteam_score, time_str, status_str FROM {table_name} WHERE date_str='{date_str}';'''
    sql_query = sql_query.format(table_name=table_name, date_str=date_str)

    return execute_statement(sql_query, db)


# Update matches table
def update_matches_table(db, column_name, column_value, date_str, localteam_name):
    table_name = "matches"
    column_value = str(column_value)
    condition_1 = "date_str = '" + str(date_str) + "'"
    condition_2 = "localteam_name = '" + str(localteam_name) + "'"
    update_row(table_name, db, column_name, column_value, condition_1, condition_2)


# Query to get all kick off times of the day
def get_kick_off_times(db, date_str, table_name='matches'):
    sql_query = '''SELECT time_str FROM {table_name} WHERE date_str='{date_str}';'''
    sql_query = sql_query.format(table_name=table_name, date_str=date_str)

    return execute_statement(sql_query, db)


# Get user phone numbers who are signed up for one team
def get_phone_numbers(db, teams, table_name='goalsms'):
    sql_query = '''SELECT phone_number FROM {table_name} WHERE team in ({teams});'''
    sql_query = sql_query.format(table_name=table_name, teams=teams)

    return execute_statement(sql_query, db)
