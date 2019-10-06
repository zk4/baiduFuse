import logging
import sys

def funcLog(func):
    def wrapper(*args, **kw):
        if "/test/" in args[1] :
            print(func.__name__,*args[1:])
        ret= func(*args, **kw)
        return ret 
    return wrapper



logger = logging.getLogger('cloud-fuse')
formatter = logging.Formatter(
        '%(filename)s:%(lineno)d  %(levelname)s -> %(message)s',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



