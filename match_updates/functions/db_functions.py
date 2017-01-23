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
def get_matches(db, date_str, comp_id='', table_name='matches'):
    comp_id = str(comp_id)
    condition = ''
    if comp_id != '':
        condition = " AND comp_id_str='" + comp_id + "'"

    sql_query = '''SELECT date_str, localteam_name, visitorteam_name, localteam_score,
                visitorteam_score, time_str, status_str, timer_str, comp_id_str
                FROM {table_name} WHERE date_str='{date_str}'{condition};'''
    sql_query = sql_query.format(table_name=table_name, date_str=date_str, condition=condition)

    return execute_statement(sql_query, db)


# Query to return all results of a given day for a given competition
def get_ft_standings(db, date_str, comp_id, table_name='matches'):
    sql_query = '''
    SELECT localteam_name, localteam_score,' - ' as separator_str, visitorteam_score, visitorteam_name
    FROM {table_name} WHERE status_str = 'FT' AND date_str = '{date_str}' AND comp_id_str = '{comp_id}';
    '''
    sql_query = sql_query.format(table_name=table_name, date_str=date_str, comp_id=comp_id)
    return execute_statement(sql_query, db)


# Test if all matches are finished (and there were some in the first place
def all_games_finished(db, date_str, comp_id, table_name='matches'):
    comp_id = str(comp_id)

    total_matches = '''SELECT count(*) AS total_matches FROM {table_name}
                    WHERE date_str = '{date_str}' AND comp_id_str='{comp_id}';'''

    total_matches = total_matches.format(table_name=table_name, date_str=date_str, comp_id=comp_id)
    no_total_matches = execute_statement(total_matches, db)
    no_total_matches = int(no_total_matches['total_matches'].values[0])

    ft_matches = '''SELECT count(*) AS ft_matches FROM {table_name}
                    WHERE date_str = '{date_str}' AND comp_id_str='{comp_id}' AND status_str = 'FT';'''

    ft_matches = ft_matches.format(table_name=table_name, date_str=date_str, comp_id=comp_id)
    no_ft_matches = execute_statement(ft_matches, db)
    no_ft_matches = int(no_ft_matches['ft_matches'].values[0])

    no_live_matches = no_total_matches - no_ft_matches
    if no_live_matches == 0 and total_matches > 0:
        return True
    else:
        return False


# Update matches table
def update_matches_table(db, column_name, column_value, date_str, localteam_name):
    table_name = "matches"
    column_value = "'" + str(column_value) + "'"
    condition_1 = "date_str = '" + str(date_str) + "'"
    condition_2 = "localteam_name = '" + str(localteam_name) + "'"
    update_row(table_name, db, column_name, column_value, condition_1, condition_2)


# Query to get all kick off times of the day
def get_kick_off_times(db, date_str, table_name='matches'):
    sql_query = '''SELECT time_str FROM {table_name} WHERE date_str='{date_str}';'''
    sql_query = sql_query.format(table_name=table_name, date_str=date_str)

    return execute_statement(sql_query, db)


# Get user phone numbers who are signed up for one team
def get_phone_numbers(db, teams, mode, table_name='goalsms'):
    mode = str(mode)
    sql_query = '''SELECT phone_number FROM {table_name} WHERE team IN ({teams}) AND mode = {mode};'''
    sql_query = sql_query.format(table_name=table_name, teams=teams, mode=mode)

    return execute_statement(sql_query, db)
