""" Main module to run the PostgreSQL deployment tests

Raises:
    ValueError: If query row count doesn't match expected value raise an error.
"""
from  user_manager import UserManager
from database_manager import dbManager
from connection_manager import ConnectionManager
from databases import Databases

cm = ConnectionManager()
dbm = dbManager()
um = UserManager()

def run_tests():
    """ Runs the PostgreSQL deployment tests

    Raises:
        ValueError: If query row count doesn't match expected value raise an error.
    """

    try:
      # get postgres database connection
      conn = cm.postgres_db_connection

      # get cursor
      cur = conn.cursor()

      # print the current postgres version
      get_version(cur)

      # create the test user
      test_user = um.create_test_user(cur)

      # switch from the postgres user to the test user
      um.switch_to_test_user(cur)

      # create the test database
      dbm.create_database(cur)

      # connect to the test database with the test user
      cm.connect_to_test_db(test_user.password)
      test_db_conn = cm.test_db_connection
      
      #remove test user state
      test_user = None

      # get test_db cursor
      test_cur = test_db_conn.cursor()

      # create a test schema in the test database
      dbm.create_schema(test_cur)

      # create a table with data in the test schema
      dbm.create_table(test_cur)

      # validate data
      print("Validating Data: Expecting 1000 Rows")
      test_cur.execute('SELECT COUNT(0) from test_schema.test_table') 

      # get the row count from the query result
      row_count = test_cur.fetchone()[0]

      # If returned rows don't match expected value raise an error
      if row_count == 1000:
          print("Success:  Returned %d Rows" % (row_count))
      else:
          raise ValueError('Error: Expected 1000 rows but got %d' % (row_count))

    # handle exceptions and cleanup any objects created during test
    except (Exception) as error:
        print(error)
    finally:
        cleanup(cur, test_cur)


def cleanup(cur, test_cur):

    # switch to postgres user
    um.switch_to_postgres_user(cur)

    # drop test_table and test_schema 
    dbm.cleanup_test_db_objects(test_cur)

    # close cursor and test_db connection
    test_cur.close()
    cm.close_connection(cm.test_db_connection, Databases.TEST_DB)  

    # drop test_db and test_user
    dbm.cleanup_postgres_db_objects(cur)

    # close cursor and postgres db connection
    cur.close()
    cm.close_connection(cm.postgres_db_connection, Databases.POSTGRES)

def get_version(cur):

   	# get the postgres version
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    print(db_version)

# entry point
if __name__ == '__main__':
    run_tests()
