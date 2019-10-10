import logging
import sys

def funcLog(func):
    def wrapper(*args, **kw):
        print(func.__name__,*args[1:])
        ret= func(*args, **kw)
        return ret 
    return wrapper



def get_my_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
