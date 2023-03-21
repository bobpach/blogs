"""Contains the Connection Manager Class

Returns:
    psycopg2.connection: A connection to a postgres database
"""
import psycopg2
from config_manager import ConfigManager
from databases import Databases


class ConnectionManager:
    """Opens and closes postgres database connections

    Returns:
        psycopg2.connection: A connection to a postgres database
    """

    cm = ConfigManager()

    # initialize with a connection to the postgres database
    def __init__(self):
        self.connect_to_postgres_db()

    # provides postgres db connection
    @property
    def postgres_db_connection(self):
        return self._conn

    # provides test db connection
    @property
    def test_db_connection(self):
        return self._test_db_conn

    # connects to postgres db and sets local connection variable
    def connect_to_postgres_db(self):

        self._conn = None

        try:
            # read connection parameters
            params = self.cm.get_postgres_connection_parameters()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self._conn = psycopg2.connect(**params)
            self._conn.autocommit = True

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.close_connection(self._conn, Databases.POSTGRES)

    # connects to test db and sets local connection variable
    def connect_to_test_db(self):

        self._test_db_conn = None

        try:
            # read connection parameters
            params = self.cm.get_test_db_connection_parameters()
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self._test_db_conn = psycopg2.connect(**params)
            self._test_db_conn.autocommit = True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.close_connection(self._test_db_conn, Databases.TEST_DB)

    # closes database connection and clears local variable
    def close_connection(self, conn, Databases):

        if conn is None:
            return
        conn.close()
        print('Database %s connection closed.' % (Databases))

        if Databases == Databases.TEST_DB:
            self._test_db_conn = None
        else:
            self._conn = None
