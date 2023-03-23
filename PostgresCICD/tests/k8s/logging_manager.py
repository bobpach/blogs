"""Contains the LoggingManager class
"""
import logging
import sys


class LoggingManager():
    """Provides a logger that logs to a file, stderr and stdout
    """
    # create logger with 'postgres_tester'
    logger = logging.getLogger('postgres_tester')
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - \
        %(levelname)s - %(message)s')

    # create file handler
    # TODO: Move into the /pgdata/*/log dir in the pod pvc
    fh = logging.FileHandler('postgres_tester.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create a stream handler for stdout
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # create a stream handler for stderr
    eh = logging.StreamHandler(stream=sys.stderr)
    eh.setLevel(logging.ERROR)
    eh.setFormatter(formatter)
    logger.addHandler(eh)

    def remove_handlers(logger):
        for handler in logger.handlers:
            handler.close()
            logger.removeFilter(handler)
