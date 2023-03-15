from connect import postgres_connect, test_db_connect, close_connection
from  userManager import UserManager
from dbManager import dbManager

# get postgres database connection
conn = postgres_connect()

# get cursor
cur = conn.cursor()

def run_tests():

    try:
      
      # print the current postgres version  
      get_version()

      # create the test user
      testUser = UserManager.create_test_user(cur)
      
      # switch from the postgres user to the test user  
      UserManager.switch_to_test_user(cur)
      
      # create the test database  
      dbManager.create_database(cur)
      
      # connect to the test database  
      test_db_conn = test_db_connect(testUser.password)
      test_cur = test_db_conn.cursor()
    
      # create a test schema in the test database
      dbManager.create_schema(test_cur)
      
      # create a table with data in the test schema  
      dbManager.create_table(test_cur)
        
      # validate data
      print("Validating Data: Expecting 1000 Rows")
      test_cur.execute('SELECT COUNT(0) from test_schema.test_table') 
      row_count = test_cur.fetchone()[0]
      if row_count ==100:
          print("Success:  Returned %d" % (row_count))
      else:
          raise ValueError('Error: Expected 1000 rows but got %d' % (row_count))
      
      UserManager.switch_to_postgres_user(cur)
            
      # cleanup all test objects roles, and vacuum
      dbManager.cleanup_test_db_objects(test_cur)
      test_cur.close()
      close_connection(test_db_conn)      
      dbManager.cleanup_postgres_db_objects(cur)
      cur.close()

    except (Exception) as error:
        print(error)
        pass
    finally:
        close_connection(conn)
        
        
def cleanup(cur, test_cur):
    dbManager.cleanup_test_db_objects(test_cur)
    test_cur.close()
    dbManager.cleanup_postgres_db_objects(cur)
    cur.close()
        
def get_version():
        
    	# get the postgres version
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        
        print(db_version)
             
if __name__ == '__main__':
    run_tests()
