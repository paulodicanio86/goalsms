import MySQLdb
import sshtunnel
import pandas as pd

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0


class DB:
    _config_dic = None
    _tunnel = None
    _db = None
    _cursor = None

    def __init__(self, db_config):
        self._config_dic = db_config

    def init(self):
        self._tunnel = None
        self._db = None
        self._cursor = None

        self._tunnel = sshtunnel.SSHTunnelForwarder(
            (self._config_dic['ssh_server']),
            ssh_username=self._config_dic['user'],
            ssh_password=self._config_dic['ssh_password'],
            remote_bind_address=(self._config_dic['host'], self._config_dic['port']))

        self._tunnel.start()

        self._db = MySQLdb.connect(host=self._config_dic['localhost'],
                                   user=self._config_dic['user'],
                                   passwd=self._config_dic['password'],
                                   db=self._config_dic['database'],
                                   port=self._tunnel.local_bind_port)

    def get(self, sql_query):
        return pd.read_sql(sql_query, con=self._db)

    def execute(self, sql_query):
        self._cursor = self._db.cursor()
        self._cursor.execute(sql_query)
        self._cursor.close()

    def commit(self):
        self._db.commit()

    def close(self):
        self._db.close()
        self._tunnel.stop()
