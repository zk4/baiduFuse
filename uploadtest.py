import requests
import json
# with open('report.xls', 'rb') as f:
#     r = requests.post('http://httpbin.org/post', files={'report.xls': f})

BDUSS=""
user_agent="netdisk;8.3.1;android-android"
app_id= 266719

def upload(path):
    url = "http://pcs.baidu.com/rest/2.0/pcs/file"
    querystring = {"app_id":"266719","method":"upload","type":"tmpfile"}
    headers = {
        'host': "pcs.baidu.com",
        'User-Agent':user_agent,
        'cookie': "BDUSS="+BDUSS
        }
    with open(path,"rb") as f:
        response = requests.request("POST", url,files={path:f} , headers=headers, params=querystring)
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

md5 = upload("./demotest.py")
createSuperFile([md5],"/test/hhhhhhhhhhhhhhhhhhhhhhhhhh.py")
