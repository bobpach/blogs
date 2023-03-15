#!/usr/bin/python
import psycopg2

from config import config, test_db_config

def postgres_connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        conn.autocommit = True
  
        return conn

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        close_connection(conn)

def test_db_connect(password):
    """ Connect to the PostgreSQL database server """
    
    print("Passed Password")
    print(password) 
        
    conn = None
    try:
        # read connection parameters
        params = test_db_config()
        params["password"] = password
              
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        
        conn.autocommit = True
		
        return conn

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        close_connection(conn)

def close_connection(conn):
    """Closing the database connection"""
    	# close the communication with the PostgreSQL
    if conn is not None:
       conn.close()
       conn = None
       print('Database connection closed.')