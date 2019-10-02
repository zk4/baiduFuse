import logging
import sys

def get_my_logger(name):
#     formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    formatter = logging.Formatter(fmt='%(module)s:%(lineno)d - %(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

logger = get_my_logger(__name__)
logger.setLevel(logging.DEBUG)

def funcLog(func):
    def wrapper(*args, **kw):
        ret= func(*args, **kw)
#         logger.debug(f'{func.__name__},{args[1]} => {ret}')
#         logger.debug(f'{func.__name__},{args[1]} => {ret}')
        return ret 
    return wrapper




