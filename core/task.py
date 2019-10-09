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
from core.log import logger,funcLog
from core.scheduler import handle,q,session
from core.custom_exceptions import Baidu8Secs
from utils.utils import notification

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
            if i >= len(task.block_infos):
                break

            block_info =task.block_infos[i]
            
            if block_info["status"] is  None: 
                block_info["status"]="ing"                       
                q.put((handle,[block_info,task],1))

    def __init__(self,url,mainArgs,path,cloud):

        self.mainArgs = mainArgs
        saved_path = "./tmp"+path
        if not os.path.exists(os.path.dirname(saved_path)):
            try:
                os.makedirs(os.path.dirname(saved_path))
            except OSError as exc: 
                # Guard against race condition
                # don`t use lock as possiable as you can
                pass         
        # almost all the files need to read fast , other wise the app will frozen or exit 
#         previewableExts={ "mkv","mpv","mp3","mp4","flv","ts","mov","avi","aac","flac","asf","rma","rmvb", \
#                 "rm","ogg","mpeg","vob","m4a","wma","wmv","3gp","zip","rar","tar","7z","pdf","doc","docx","xls","xlsx","dmg" }

        # if you only copy from cloud,then put the file extension in this set,it will down load blazing fast
        nonPreviewAbleExts ={"chunk"}
        self.isPreviewAble=True
        if saved_path.split(".")[-1].lower()  in nonPreviewAbleExts:
            self.isPreviewAble=False
            logger.debug(f"{saved_path} is chunable")
        self.path = path
        self.url= url
        self.saved_path = saved_path
        self.cloud = cloud
        self.user_headers=cloud.getHeader()
        self.part_size = 65536*4
        self.block_infos =[]
        self.current_file_size = 0
        self.file_size =0
        self.terminating = False
        self.mmap = None
        self.part_count=None

    def get_url(self):
        return self.url

    def is_terminating(self):
        return self.terminating

    def get_mmap(self):
        return self.mmap

    def get_cache(self,offset,size):
        try:
            r = self.get_block_range(offset,size)
            c = self.block_infos[r[0]]
            start = time.time()

            maxWaitRound = 10
            curRound = 0
            while True:
                if  r[0] == r[1]:
                    if c["cur"]+c["start"]>=(size+offset):
                        return self.mmap[offset:offset+size]
                    else:
                        with c["m"]:
                            c["m"].wait(1)
                else:
                    alldone = True
                    for i in range(r[0],r[1]+1):
                        if self.block_infos[i]["status"] != "done":
                            alldone=False
                            with self.block_infos[i]["m"]:
                                self.block_infos[i]["m"].wait(1)
                    if alldone:
                        return self.mmap[offset:offset+size]

                q.put((Task.createHelperThread,[r[0],r[1],self],1))
                end = time.time()
                # no response for 10 secs, just drop it 
                # TODO this  shoud be configurable
                if end-start>10:
                    return None
                curRound+=1
#                 print("wait ",curRound)

        except Exception as e:
            # logger.debug(f'index:{r[0]},block len:{len(self.block_infos)},path: {self.saved_path}')
            # logger.exception(e) 
            pass


        return None

    def get_block_range(self,offset,size):
        start_idx = offset // self.part_size 
        end_idx = (size + offset) // self.part_size
        return [start_idx,end_idx]


    def start(self): 
        size_retries = 5
        cur_size_retries=0
        while True:
            r = self.cloud.meta2(self.path)
            if "list" in r:
                for l in r["list"]:
                    self.file_size +=l["size"]
                break
            cur_size_retries+=1
            if cur_size_retries > size_retries:
                print(r)
                raise BaseException("得不到 size")

        print("file size ------",self.file_size)
        # try: 
        #     self.file_size = int(r.headers["content-length"]) 
        #     if 'Location' in r.headers and 'issuecdn' in r.headers['Location']:
        #         notification(self.saved_path[self.saved_path.rfind("/")+1:],"文件已变 8 秒~")
        #         raise Baidu8Secs(self.saved_path)
        # except Exception as e : 
        #     raise e  
                  
        self.part_count = math.ceil(self.file_size / self.part_size)

        with open(self.saved_path, "wb")  as fp:
            fp.seek(self.file_size)
            fp.write(b'\0')
             
        self.mmap = Task.createMmap(self.saved_path,self.file_size)
        self.create_range()
        # pre start task to get data 
        if self.isPreviewAble:
            q.put((Task.createHelperThread,[0,8 if 8 < self.part_count else self.part_count-1 ,self],1))
            #  request the end for a little bit 
#             q.put((createHelperThread,[self.part_count-3 if ( self.part_count-3 ) > 0   else self.part_count-1 ,self.part_count-1,self],1))
        else:
            q.put((Task.createHelperThread,[0,400 if 400 < self.part_count else self.part_count-1 ,self],1))
      

    def create_range(self):
        start = 0
        size = self.part_size

        while start < self.file_size:
            if start+size> self.file_size:
                size = self.file_size - start
            self.block_infos.append({"status":None,"start":start,"size":size,"cur":0,"m":threading.Condition() })
            if size == self.file_size - start:
                break
            start += self.part_size

    def terminate(self):
        self.terminating = True
