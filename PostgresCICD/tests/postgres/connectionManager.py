#!/usr/bin/python
import psycopg2
from config import config, test_db_config

class ConnectionManager:
      
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
            params = config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self._conn = psycopg2.connect(**params)
            self._conn.autocommit = True
  
          except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.close_connection(self._conn)

      # connects to test db and sets local connection variable
      def connect_to_test_db(self, password):
       
          self._test_db_conn = None
          
          try:
            # read connection parameters
            params = test_db_config()
            params["password"] = password
             
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self._test_db_conn = psycopg2.connect(**params)
            self._test_db_conn.autocommit = True
          except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.close_connection(self._test_db_conn)

      # closes database connection and clears local variable
      def close_connection(self, conn, Databases):

        if conn == None:
          return
        else:
          conn.close()
          print('Database %s connection closed.' % (Databases))
        
        if Databases == Databases.TEST_DB:
          self._test_db_conn = None
        else:
          self._conn = None 