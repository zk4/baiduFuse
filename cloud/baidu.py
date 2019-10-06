#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from log import logger,funcLog
import requests
import json
import browser_cookie3
cj = browser_cookie3.chrome(domain_name='baidu.com')

session = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=3,pool_connections = 50, pool_maxsize = 200)
session.mount('http://', a)
session.mount('https://', a)

class PCS():
    def __init__(self,*args, **kw):
        self.app_id="266719"
        self.user_agent="netdisk;8.3.1;android-android"
        self.BDUSS = None
        for cookie in cj:
           if cookie.name =='BDUSS':
               self.BDUSS=cookie.value
        if not self.BDUSS:
            print("no bdus")
            sys.exit()
        self.header={'User-Agent': self.user_agent,'cookie':"BDUSS="+   self.BDUSS}

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

    def upload(self,dirname,tmp_file,base_name):
        logger.info("upload")

    def getRestUrl(self,url):
        return "https://pcs.baidu.com/rest/2.0/pcs/file?method=download&app_id="+self.app_id+"&path="+url

    def mkdir(self,path):
        url = "http://pcs.baidu.com/rest/2.0/pcs/file"
        querystring = {"app_id":self.app_id,"method":"mkdir","path":path}
        headers = {
            'host': "pcs.baidu.com",
            'User-Agent':self.user_agent,
            'cookie': "BDUSS="+self.BDUSS
            }
        response = requests.request("POST", url,  headers=headers, params=querystring)
        print(response.text)
