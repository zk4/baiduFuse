class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__

class CancelledError(BaseException):
    def __init__(self, msg):
        BaseException.__init__(self, msg)

# 百度 8 秒
class Baidu8Secs(Exception):
    def __init__(self,msg=""):
        BaseException.__init__(self, "百度 8 秒! "+msg)