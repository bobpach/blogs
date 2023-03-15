from psycopg2 import sql

class dbManager:
    
  def create_database(cur):
    
    # set db name
    dbname = sql.Identifier('test_db')
    
    # commands to create database and assign privs
    print("Creating test database")
    create_cmd = sql.SQL('CREATE DATABASE {}').format(dbname)
    print("Assigning test_db privs to test_user")
    grant_cmd = sql.SQL('GRANT ALL PRIVILEGES ON DATABASE {} TO test_user').format(dbname)
    
    # execute commands
    cur.execute(create_cmd)
    cur.execute(grant_cmd)
  
  # create test schema
  def create_schema(cur):
    print("Creating test_schema in test_db")
    cur.execute('CREATE SCHEMA test_schema')
    
  # create table in test schema
  def create_table(cur):
    print("Creating test_table table with data in test_schema")
    cur.execute('CREATE TABLE test_schema.test_table AS SELECT s, md5(random()::text) FROM generate_Series(1,1000) s')
    
  def cleanup_test_db_objects(cur):
    print("Dropping test_table")
    cur.execute('DROP TABLE test_schema.test_table')
    print("Dropping test_schema")
    cur.execute('DROP SCHEMA test_schema')
    
  def cleanup_postgres_db_objects(cur):
    print("Dropping test_db")
    cur.execute('DROP DATABASE test_db')
    print("Dropping test_user")
    cur.execute('DROP ROLE test_user')