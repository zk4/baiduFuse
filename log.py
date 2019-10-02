import logging
import sys

def funcLog(func):
    def wrapper(*args, **kw):
        print(func.__name__,*args[1:])
        return func(*args, **kw)
    return wrapper



logger = logging.getLogger('cloud-fuse')
formatter = logging.Formatter(
        '%(filename)s:%(lineno)d %(threadName)s %(levelname)s -> %(message)s',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



