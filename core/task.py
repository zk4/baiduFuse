#!/usr/bin/python
# -*- coding: utf-8 -*-
 

import requests 
import math 
import time
import traceback
import os
import threading
import mmap
import logging
from log import logger,funcLog
from core.scheduler import handle,q,session
from core.custom_exceptions import Baidu8Secs

logger.setLevel(logging.DEBUG)



class Task(object):
    @staticmethod
    def createMmap(filename,size, access=mmap.ACCESS_WRITE):
        fd = os.open(filename, os.O_RDWR)
        return mmap.mmap(fd, size, access=access)


    @staticmethod
    def createHelperThread(startIdx,endIdx,task):
        isPreviewAble = task.isPreviewAble
        preDownloadPart = 30 if isPreviewAble else 30
        for i in range(startIdx,endIdx+preDownloadPart):
            if i >= len(task.cache):
                break

            cache =task.cache[i]
            
            if cache["status"] is  None: 
                cache["status"]="ing"                       
                q.put((handle,[cache,task],1))

    def __init__(self,url,saved_path,headers=None):

         
#         logger.debug(saved_path)
        # almost all the files need to read fast , other wise the app will frozen or exit 

#         previewableExts={ "mkv","mpv","mp3","mp4","flv","ts","mov","avi","aac","flac","asf","rma","rmvb", \
#                 "rm","ogg","mpeg","vob","m4a","wma","wmv","3gp","zip","rar","tar","7z","pdf","doc","docx","xls","xlsx","dmg" }

        # if you only copy from cloud,then put the file extension in this set,it will down load blazing fast
        nonPreviewAbleExts ={"chunk"}
        self.isPreviewAble=True
        if saved_path.split(".")[-1].lower()  in nonPreviewAbleExts:
            self.isPreviewAble=False
            logger.debug(f"{saved_path} is chunable")

        self.url= url
        self.saved_path = saved_path
        self.user_headers=headers

        self.part_size = 65536*4

        self.cache =[]
        self.current_file_size = 0
        self.file_size =0
        self.terminating = False
        self.m = None
        self.part_count=None
#         self.condition = threading.Condition()
        


    def get_cache(self,offset,size):
        try:
            r = self.get_block_range(offset,size)
            c = self.cache[r[0]]
            start = time.time()

            maxWaitRound = 10
            curRound = 0
            while True:
                if  r[0] == r[1]:
                    if c["cur"]+c["start"]>=(size+offset):
                        # tiny data
#                         logger.info(f"tiny data found,{self.saved_path} - {c} ")
                        return self.m[offset:offset+size]
                    else:
                        with c["m"]:
                            c["m"].wait(1)
                else:
                    alldone = True
                    for i in range(r[0],r[1]+1):
                        if self.cache[i]["status"] != "done":
                            alldone=False
                            with self.cache[i]["m"]:
                                self.cache[i]["m"].wait(1)

                    if alldone:
#                         logger.info(f'range - {r}')
                        return self.m[offset:offset+size]


                
                q.put((Task.createHelperThread,[r[0],r[1],self],1))
                end = time.time()
                # no response for 10 secs, just drop it 
                if end-start>10:
                    return None
                curRound+=1
#                 logger.debug(f"wait for {curRound}")
#                 with self.condition:
#                     self.condition.wait(1)

        except Exception as e:
            logger.debug(f'{r[0]},{len(self.cache)},{self.saved_path}')
            logger.exception(e) 


        return None

    def get_block_range(self,offset,size):
        start_idx = offset // self.part_size 
        end_idx = (size + offset) // self.part_size
        return [start_idx,end_idx]


    def start(self): 
        r = session.head(self.url,headers={ **self.user_headers}) 

        try: 
            self.file_size = int(r.headers["content-length"]) 
            if 'Location' in r.headers and 'issuecdn' in r.headers['Location']:
                raise Baidu8Secs(self.saved_path)
        except Exception as e : 
            raise e 
                
        self.part_count = math.ceil(self.file_size / self.part_size)

        with open(self.saved_path, "wb")  as fp:
            fp.seek(self.file_size)
            fp.write(b'\0')
            
        self.m = Task.createMmap(self.saved_path,self.file_size)
        self.create_range()
        # pre start task to get data 
        if self.isPreviewAble:
            q.put((Task.createHelperThread,[0,8 if 8 < self.part_count else self.part_count-1 ,self],1))
#             q.put((createHelperThread,[self.part_count-3 if ( self.part_count-3 ) > 0   else self.part_count-1 ,self.part_count-1,self],1))
        else:
            q.put((Task.createHelperThread,[0,400 if 400 < self.part_count else self.part_count-1 ,self],1))
      

    def create_range(self):
        start = 0
        size = self.part_size

        while start < self.file_size:
            if start+size> self.file_size:
                size = self.file_size - start
            self.cache.append({"status":None,"start":start,"size":size,"cur":0,"m":threading.Condition() })
            if size == self.file_size - start:
                break
            start += self.part_size

    def terminate(self):
        self.terminating = True
