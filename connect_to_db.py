import pandas as pd
import MySQLdb
import json
from pprint import pprint
from IPython import embed

with open('db_connection.json') as data_file:
    data = json.load(data_file)
pprint(data)


db = MySQLdb.connect(host = data['host'], user = data['user'], passwd = data['password'], db = data['database'])


# Get data
df = pd.read_sql("SELECT * FROM test;", con=db)
#col = ['PersonID', 'LastName', 'FirstName', 'Address', 'City']
col = df.columns


# Append data
data2 = [(2, 'Schaack', 'Paul', 'young man', 'Hamburgo')]
df2 = pd.DataFrame(data2, columns=col)
embed()
df2.to_sql('test',db, flavor='mysql', if_exists = 'append')


# Delete table
cur = db.cursor()
sql = 'DROP table test;'
#cur.execute(sql)


# Create table
cur = db.cursor()
sql = '''CREATE TABLE test
(
PersonID int,
LastName varchar(255),
FirstName varchar(255),
Address varchar(255),
City varchar(255)
);'''
#cur.execute(sql)


# Insert into table
sql2 = '''INSERT INTO test(PersonID,
         LastName, FirstName, Address, City)
         VALUES (5, 'Mohan', 'Dida', 'Good street', 'London');'''
#cur.execute(sql2)



db.commit()
db.close()







