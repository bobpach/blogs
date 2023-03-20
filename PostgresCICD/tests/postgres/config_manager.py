"""Contains ConfigManager Class

    Raises:
        Exception: database.ini parsing error for postgresql
        Exception: database.ini parsing error for testpostgresql

    Returns:
       dict: Dictionary containing postgres connection string values
"""
from configparser import ConfigParser


class ConfigManager:
    """The ConfigManager Class

        Raises:
            Exception: database.ini parsing error for postgresql
            Exception: database.ini parsing error for testpostgresql

        Returns:
            dict: Dictionary containing postgres connection string values
    """

    def get_postgres_config(self):

        _filename = '/Users/robertpacheco/blogs/PostgresCICD\
/tests/postgres/database.ini'
        _section = 'postgresql'

        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(_filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(_section):
            params = parser.items(_section)
            for param in params:
                db[param[0]] = param[1]
        else:
            err = ('Section {0} not found in the {1} file')
            raise Exception(err.format(_section, _filename))

        return db

    def get_test_db_config(self):

        _filename = '/Users/robertpacheco/blogs/PostgresCICD\
/tests/postgres/database.ini'
        _section = 'testpostgresql'

        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(_filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(_section):
            params = parser.items(_section)
            for param in params:
                db[param[0]] = param[1]
        else:
            err = ('Section {0} not found in the {1} file')
            raise Exception(err.format(_section, _filename))

        return db
