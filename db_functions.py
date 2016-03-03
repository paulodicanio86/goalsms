import pandas as pd


# Query db to select all
def select_all(table_name, db):
    sql_query = 'SELECT * FROM {table_name};'.format(table_name=table_name)

    df = pd.read_sql(sql_query, con=db)
    return df


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
