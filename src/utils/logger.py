import logging


def create_logger(name):
    logging.basicConfig(filename='./utils/rpa_challenge.log', level=logging.INFO)
    logger = logging.getLogger(name)
    logger.info('Started Rpa Challenge process...')
