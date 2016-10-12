import json
import MySQLdb
import datetime as datetime
import os

from db_functions import select_all

with open('config_files/db_config.json') as data_file:
    data_config = json.load(data_file)

db = MySQLdb.connect(host=data_config['host'],
                     user=data_config['user'],
                     passwd=data_config['password'],
                     db=data_config['database'])

i = datetime.datetime.now()
date_str = str(i.strftime('%d.%m.%Y'))
table = 'goalsms'

data = select_all(table, db)
data.to_json('backend/backup_tables/backup_' + table + '_' + date_str + '.json', orient='split')
data.to_csv('backend/backup_tables/backup_' + table + '_' + date_str + '.csv')

db.commit()
db.close()
