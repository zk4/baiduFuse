import requests
import json
import io
class CancelledError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__

class BufferReader(io.BytesIO):
    def __init__(self, buf=b'',
                 callback=None,
                 cb_args=(),
                 cb_kwargs={}):
        self._callback = callback
        self._cb_args = cb_args
        self._cb_kwargs = cb_kwargs
        self._progress = 0
        self._len = len(buf)
        io.BytesIO.__init__(self, buf)

    def __len__(self):
        return self._len

    def read(self, n=-1):
        chunk = io.BytesIO.read(self, n)
        self._progress += int(len(chunk))
        self._cb_kwargs.update({
            'size'    : self._len,
            'progress': self._progress
        })
        if self._callback:
            try:
                self._callback(*self._cb_args, **self._cb_kwargs)
            except: # catches exception from the callback
                raise CancelledError('The upload was cancelled.')
        return chunk


def progress(size=None, progress=None):
    print("{0} / {1}".format(size, progress))
BDUSS = ""
import browser_cookie3
cj = browser_cookie3.chrome(domain_name='baidu.com')
for cookie in cj:
    if cookie.name =='BDUSS':
        BDUSS=cookie.value
print(BDUSS)
user_agent="netdisk;8.3.1;android-android"
app_id= 266719

def upload(path):
    url = "http://pcs.baidu.com/rest/2.0/pcs/file"
    querystring = {"app_id":"266719","method":"upload","type":"tmpfile"}
    files = {"myFileUpl": ("name", open(path, 'rb').read())}

    (data, ctype) = requests.packages.urllib3.filepost.encode_multipart_formdata(files)      

    body = BufferReader(data, progress)
    headers = {
        'host': "pcs.baidu.com",
        'User-Agent':user_agent,
        'cookie': "BDUSS="+BDUSS,
        'Content-Type':ctype
        }
 
    response = requests.request("POST", url,data=body , headers=headers, params=querystring)
    return json.loads(response.text)["md5"]


def createSuperFile(blocklist,path):
    url = "http://pcs.baidu.com/rest/2.0/pcs/file"
    querystring = {"app_id":app_id,"method":"createsuperfile","ondup":"newcopy","path":path}
    formatPaths = json.dumps(list(map(lambda p : p, blocklist)))
    payload = "--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942\nContent-Disposition: form-data; name=\"param\"\n\n{\"block_list\":"+formatPaths+"}\n--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942--\n"

    payload = payload.encode('utf-8')
    headers = {
        'host': "pcs.baidu.com",
        'User-Agent':user_agent,
        'Content-Type': "multipart/form-data; boundary=a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942",
        'cookie': "BDUSS="+BDUSS
    }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

path ="/Users/zk/Downloads/o.mp4"
md5 = upload(path)
createSuperFile([md5],"/test/ooo.py")

