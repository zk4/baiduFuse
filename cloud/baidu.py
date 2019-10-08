#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from core.log import logger,funcLog
import requests
import json
from core.autoBDUSS import getBDUSS,cj
from core.progress_requests import BufferReader, progress
import urllib.parse


session = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=3,pool_connections = 50, pool_maxsize = 200)
session.mount('http://', a)
session.mount('https://', a)

class PCS():
    def __init__(self,*args, **kw):
        self.app_id="266719"
        self.user_agent="netdisk;8.3.1;android-android"
        self.host = "pcs.baidu.com"
        self.BDUSS = getBDUSS()
        self.header={
            'User-Agent': self.user_agent,
            'cookie':"BDUSS="+   self.BDUSS,
            'User-Agent':self.user_agent,
            'host': "pcs.baidu.com",
            'Accept-Encoding':"gzip"
            }

    def delete(self,paths):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"method":"delete"}
        formatPaths = json.dumps(list(map(lambda p : {"path":p}, paths)))
        payload = "--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942\nContent-Disposition: form-data; name=\"param\"\n\n{\"list\":"+formatPaths+"}\n--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942--\n"

        payload = payload.encode('utf-8')
        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'Content-Type': "multipart/form-data; boundary=a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942",
            'cookie': "BDUSS="+self.BDUSS
        }
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)


    def list_files(self,path):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"by":"name","limit":"0-2147483647","method":"list","order":"asc","path":path}
        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'cookie': "BDUSS="+self.BDUSS
        }


        response = session.get(url, headers=headers, params=querystring)

        return response.text
    def meta2(self,path):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"

        querystring = {"app_id":self.app_id,"method":"meta"}
        # formatPaths = json.dumps(list(map(lambda p : p, fileList)))
        payload = "--96d1a91af576910cff0eeb87d943084349f801009e3622e00043d269d22d\nContent-Disposition: form-data; name=\"param\"\n\n{\"list\":[{\"path\":\""+path+"\"}]}\n--96d1a91af576910cff0eeb87d943084349f801009e3622e00043d269d22d--\n"

        payload = payload.encode('utf-8')
        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'Content-Type': "multipart/form-data; boundary=96d1a91af576910cff0eeb87d943084349f801009e3622e00043d269d22d",
            'Cookie': "BDUSS="+self.BDUSS,
        }


        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        
        r= json.loads(response.text)

        return r
    def meta(self,file_list):
        url = "http://pan.baidu.com/api/filemetas"
        data = {'target': json.dumps(file_list)}
        querystring = {"dlink":"0","blocks":"0","method":"filemetas"}
        headers = {
            'host': "pan.baidu.com",
            'accept': "application/json, text/javascript, text/html, */*; q=0.01",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            'accept-language': "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
            'referer': "http://pan.baidu.com/disk/home",
            'x-requested-with': "XMLHttpRequest",
            'content-type': "application/x-www-form-urlencoded"
        }

        try:
            response = session.post( url,cookies=cj, data=data, headers=headers, params=querystring)
        except Exception as e:
            logger.info(e)
            return '[]' 
        return response.text
    
    def getHeader(self):
        return self.header

    def rename(self, old, new):
        logger.info("rename")
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"method":"move"}
        formatPaths = '[{"from":"'+old+'","to":"'+new+'"}]'
        payload = "--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942\nContent-Disposition: form-data; name=\"param\"\n\n{\"list\":"+formatPaths+"}\n--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942--\n"
        payload = payload.encode('utf-8')

        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'Content-Type': "multipart/form-data; boundary=a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942",
            'cookie': "BDUSS="+self.BDUSS
        }
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)


    def upload(self,localPath,cloudPath):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"method":"upload","type":"tmpfile"}
        files = {"myFileUpl": ("name", open(localPath, 'rb').read())}

        (data, ctype) = requests.packages.urllib3.filepost.encode_multipart_formdata(files)
        body = BufferReader(data, progress)

        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'cookie': "BDUSS="+self.BDUSS,
            'Content-Type':ctype
            }

        response = requests.request("POST", url,data=body , headers=headers, params=querystring)
        md5 =  json.loads(response.text)["md5"]
        return self.createSuperFile([md5],cloudPath)


    def createSuperFile(self,blocklist,path):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"method":"createsuperfile","ondup":"newcopy","path":path}
        formatPaths = json.dumps(list(map(lambda p : p, blocklist)))
        payload = "--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942\nContent-Disposition: form-data; name=\"param\"\n\n{\"block_list\":"+formatPaths+"}\n--a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942--\n"

        payload = payload.encode('utf-8')
        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'Content-Type': "multipart/form-data; boundary=a3e249a7d481640c2215fe9bd04ad69c196dd9a116c0354d94e27ddda942",
            'cookie': "BDUSS="+self.BDUSS
        }
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        return response.text 

    def getRestUrl(self,url):
        return "https://pcs.baidu.com/rest/2.0/pcs/file?method=download&app_id="+self.app_id+"&path="+urllib.parse.quote(url,safe="")

    def mkdir(self,path):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"method":"mkdir","path":path}
        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'cookie': "BDUSS="+self.BDUSS
            }
        response = requests.request("POST", url,  headers=headers, params=querystring)

    def quota(self):
        url = "http://pcs.baidu.com/rest/2.0/pcs/quota"
        querystring = {"app_id":self.app_id,"method":"info"}
        headers = {
            'Host': self.host,
            'User-Agent': self.user_agent,
            'Cookie': "BDUSS="+self.BDUSS,
            'cache-control': "no-cache"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

