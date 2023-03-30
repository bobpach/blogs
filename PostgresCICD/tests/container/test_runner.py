""" Main module to run the PostgreSQL deployment tests

Raises:
    ValueError: If query row count doesn't match expected value raise an error.
"""
import os
import time
from connection_manager import ConnectionManager
from databases import Databases
from database_manager import DatabaseManager
from data_node_type import DataNodeType
from kubernetes import client, config
from logging_manager import LoggingManager
from user_manager import UserManager


# initialize logger
lm = LoggingManager()

# Log entry for new test run
LoggingManager.logger.info('******* STARTING NEW TEST RUN *******')

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
        # set locals
        conn = None
        primary_test_db_conn = None
        replica_test_db_conn = None
        cur = None
        primary_test_cur = None
        replica_test_cur = None

        # determine if the cluster has any replica pods
        replica_exists = does_postgres_cluster_have_replicas()

        is_primary = is_host_primary_data_pod()
        if not is_primary:
            LoggingManager.logger.info("Not primary at test time. "
                                       "Please see primary data node"
                                       "self_test.log for test results.")
            # Keep container alive to prevent crash loopback
            # minimal resources used by this approach
            while True:
                time.sleep(1)

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

        # connect to the primary test database with the test user
        cm.connect_to_primary_test_db()
        primary_test_db_conn = cm.primary_test_db_connection

        if primary_test_db_conn is not None:

            # get test_db cursor
            primary_test_cur = primary_test_db_conn.cursor()

            # create a test schema in the test database
            dbm.create_schema(primary_test_cur)

            # create a table with data in the test schema
            dbm.create_table(primary_test_cur)

            validate_data(primary_test_cur, DataNodeType.PRIMARY)

        if replica_exists is True:
            # connect to the replica test database with the test user
            time.sleep(10)
            cm.connect_to_replica_test_db()
            replica_test_db_conn = cm.replica_test_db_connection

            if replica_test_db_conn is not None:

                # get test_db cursor
                replica_test_cur = replica_test_db_conn.cursor()
                validate_data(replica_test_cur, DataNodeType.REPLICA)
        else:
            LoggingManager.logger.warning("No replica pods detected. "
                                          "This postgres cluster is not "
                                          "highly available.")
    except (Exception) as error:
        LoggingManager.logger.error(error, exc_info=True)
    finally:
        if replica_exists is True:
            cleanup(conn, replica_test_cur, Databases.TEST_DB,
                    DataNodeType.REPLICA)
        cleanup(conn, primary_test_cur, Databases.TEST_DB,
                DataNodeType.PRIMARY)
        cleanup(conn, cur, Databases.POSTGRES, DataNodeType.PRIMARY)

        # remove logging handlers from logger
        lm.remove_handlers(LoggingManager.logger)


def validate_data(test_db_cur, DataNodeType):
    """ Determines if the expected data actually exists

    Args:
        test_db_cur (psycopg2.connection.cursor): The cursor to the active
        connection being validated
        DataNodeType (ENUM): Primary or Replica data node connection

    Raises:
        ConnectionError: Error received when attempting to validate data
    """
    if test_db_cur is not None:

        # validate data
        LoggingManager.logger.info('Validating %s Data: Expecting 1000 Rows'
                                   % (DataNodeType))
        test_db_cur.execute('SELECT COUNT(0) from test_schema.test_table')

        # get the row count from the query result
        row_count = test_db_cur.fetchone()[0]

        assert row_count == 1000, "row count should be 1000"
        LoggingManager.logger.info("*** %s Validation Succeeded! ***"
                                   % (DataNodeType))

    else:
        err = 'Unable to connect to the primary test database'
        raise ConnectionError(err, test_db_cur)


def cleanup(conn, cur, Databases, DataNodeType):
    """ Cleans all database users and objects created during the tests

    Args:
        conn psycopg2.connection: The database connection to be closed
        cur connection.cursor: The postgres db connection cursor
        primary_test_cur connection.cursor: the test db connection cursor
    """
    if conn is None:
        return

    # switch to postgres user
    if cur is None:
        return

    # cleanup postgres db objects
    if Databases == Databases.POSTGRES:
        um.switch_to_postgres_user(cur)
        # drop test_db and test_user
        dbm.cleanup_postgres_db_objects(cur)

        # close cursor and postgres db connection
        cur.close()
        cm.close_connection(cm.postgres_db_connection,
                            Databases.POSTGRES, DataNodeType)

    # cleanup test db objects
    if Databases == Databases.TEST_DB:
        if DataNodeType == DataNodeType.PRIMARY:
            # drop test_table and test_schema
            dbm.cleanup_test_db_objects(cur)
            # close cursor and test_db connections
            cur.close()
            cm.close_connection(cm.primary_test_db_connection,
                                Databases.TEST_DB, DataNodeType)
        else:
            cur.close()
            cm.close_connection(cm.replica_test_db_connection,
                                Databases.TEST_DB, DataNodeType)


def get_version(cur):
    """ Connects to the postgres database and gets the current postgres version

    Args:
        cur (connection.cursor: The postgres db connection cursor
    """
    # get the postgres version
    LoggingManager.logger.info('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    LoggingManager.logger.info(db_version)


def is_host_primary_data_pod():
    """ Determine if the container is running on a
    primary or replica data pod.

    Returns:
        bool: True if Primary
    """
    config.load_incluster_config()
    kube = client.CoreV1Api()
    ns = os.getenv('NAMESPACE')
    host = os.getenv('HOSTNAME')

    primary_label = 'postgres-operator.crunchydata.com/role=master'
    primary_pods = kube.list_namespaced_pod(namespace=ns,
                                            label_selector=primary_label)
    for pod in primary_pods.items:
        if pod.metadata.name == host:
            return True
    return False


def does_postgres_cluster_have_replicas():
    """ Determine if the container is running replica data pods

    Returns:
        bool: True if Replica
    """
    config.load_incluster_config()
    kube = client.CoreV1Api()
    ns = os.getenv('NAMESPACE')

    replica_label = 'postgres-operator.crunchydata.com/role=replica'
    replica_pods = kube.list_namespaced_pod(namespace=ns,
                                            label_selector=replica_label)
    if replica_pods.items is not None:
        for pod in replica_pods.items:
            if pod is not None:
                return True
    return False


# entry point
if __name__ == '__main__':
    run_tests()
    while True:
        time.sleep(1)
