from psycopg2 import sql
from passwordManager import PasswordManager
from testUser import TestUser

class UserManager:

  # create test user with permissions
  def create_test_user(cur):
    try:
        # initialize password manager
        passwordManager = PasswordManager()
        
        # create stateful object for the test user
        testUser = TestUser("test_user", passwordManager.password)
        
        # create test user and grant privileges 
        create_cmd = sql.SQL("CREATE USER test_user WITH PASSWORD {}").format(sql.Literal(passwordManager.password))
        cur.execute(create_cmd)
        grant_cmd = sql.SQL('ALTER ROLE test_user WITH SUPERUSER CREATEDB')
        cur.execute(grant_cmd)
        
        return testUser
    except (Exception) as error:
      print(error)
  
  # make test user the active user
  def switch_to_test_user(cur):
    cur.execute('SET ROLE test_user')
    
  # make postgres user the current user 
  def switch_to_postgres_user(cur):
    cur.execute('SET ROLE postgres')
   
  