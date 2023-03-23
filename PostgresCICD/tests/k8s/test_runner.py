""" Main module to run the PostgreSQL deployment tests

Raises:
    ValueError: If query row count doesn't match expected value raise an error.
"""
from user_manager import UserManager
from database_manager import DatabaseManager
from connection_manager import ConnectionManager
from logging_manager import LoggingManager
from databases import Databases

# initialize logger
logger = LoggingManager.logger

# Log entry for new test run
logger.info('******* STARTING NEW TEST RUN *******')

# initialize globals
cm = ConnectionManager()
dbm = DatabaseManager()
um = UserManager()


def run_tests():
    """ Runs the PostgreSQL deployment tests

    Raises:
        ValueError: If query row count doesn't match
            expected value raise an error.
    """

    try:

        cur = None
        test_cur = None
        conn = None

        # TODO: Only run on the primary node
        # TODO: Connect to replica svc and validate that table was replicated
        # with correct row count
        # TODO: Connect to replica svc and validate that drops were replicated

        # get postgres database connection
        conn = cm.postgres_db_connection

        # get cursor
        if conn is not None:
            cur = conn.cursor()

            # print the current postgres version
            get_version(cur)

            # # create the test user
            um.create_test_user(cur)

            # switch from the postgres user to the test user
            um.switch_to_test_user(cur)

            # create the test database
            dbm.create_database(cur)
        else:
            err = 'Unable to connect to the postgres database'
            raise ConnectionError(err, conn)

        # connect to the test database with the test user
        cm.connect_to_test_db()
        test_db_conn = cm.test_db_connection

        if test_db_conn is not None:

            # get test_db cursor
            test_cur = test_db_conn.cursor()

            # create a test schema in the test database
            dbm.create_schema(test_cur)

            # create a table with data in the test schema
            dbm.create_table(test_cur)

            # validate data
            logger.info("Validating Data: Expecting 1000 Rows")
            test_cur.execute('SELECT COUNT(0) from test_schema.test_table')

            # get the row count from the query result
            row_count = test_cur.fetchone()[0]

            assert row_count == 1000, "row count should be 1000"
            logger.info("*** Validation Succeeded! ***")

        else:
            err = 'Unable to connect to the test database'
            raise ConnectionError(err, conn)

    # handle exceptions and cleanup any objects created during test
    except (Exception) as error:
        logger.error(error, exc_info=True)
        # raise
    finally:
        cleanup(conn, cur, test_cur)


def cleanup(conn, cur, test_cur):
    """ Cleans all database users and objects created during the tests

    Args:
        conn psycopg2.connection: The database connection to be closed
        cur connection.cursor: The postgres db connection cursor
        test_cur connection.cursor: the test db connection cursor
    """
    if conn is None:
        return

    # switch to postgres user
    if cur is None:
        return
    else:
        um.switch_to_postgres_user(cur)

    # drop test_table and test_schema
    if test_cur is None:
        return
    else:
        dbm.cleanup_test_db_objects(test_cur)

    # close cursor and test_db connection
    test_cur.close()
    cm.close_connection(cm.test_db_connection, Databases.TEST_DB)

    # drop test_db and test_user
    dbm.cleanup_postgres_db_objects(cur)

    # close cursor and postgres db connection
    cur.close()
    cm.close_connection(cm.postgres_db_connection, Databases.POSTGRES)

    # remove logging handlers from logger
    LoggingManager.remove_handlers(logger)


def get_version(cur):
    """ Connects to the postgres database and gets the current postgres version

    Args:
        cur (connection.cursor: The postgres db connection cursor
    """
    # get the postgres version
    logger.info('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    logger.info(db_version)


# entry point
if __name__ == '__main__':
    run_tests()
