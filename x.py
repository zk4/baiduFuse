#!/usr/bin/python
# -*- coding: utf-8 -*-

import stat
import errno
import os
import sys
import math
import json

from diskcache import Cache
from io import BytesIO
try:
    import _find_fuse_parts
except ImportError:
    pass
import logging
from log import funcLog,logger
import time

from fuse import FUSE, FuseOSError, Operations

from termcolor import colored
from colorama import Fore, Back, Style, init
from concurrent.futures  import ThreadPoolExecutor as Pool

from cloud.baidu import PCS 
from core.task  import Task


dirReaderDaemon = Pool(1)
pool = Pool(5)

logger.setLevel(logging.INFO)

class NoSuchRowException(Exception):
    pass

class NoUniqueValueException(Exception):
    pass

class File():
    def __init__(self):
        self.dict = {'bd_fsid':0,
                    'bd_blocklist':0,
                    'bd_md5':0,
                    'st_mode':0,
                    'st_ino':0,
                    'st_dev':0,
                    'st_nlink':0,
                    'st_uid':0,
                    'st_gid':0,
                    'st_size':0,
                    'st_atime':0,
                    'st_mtime':0,
                    'st_ctime':0}
    def __getitem__(self, item):
        return self.dict[item]
    def __setitem__(self, key, value):
        self.dict[key] = value
    def __str__(self):
        return self.dict.__repr__()
    def __repr__(self):
        return self.dict.__repr__()
    def getDict(self):
        return self.dict


class CloudFS(Operations):
    '''Baidu netdisk filesystem'''

    def __init__(self,  *args, **kw):
        self.buffer = Cache('./cache/buffer')
        self.dir_buffer = Cache('./cache/dir_buffer')
        self.file_cache = Cache('./cache/file_cache')

        self.traversed_folder = {}
        self.disk = PCS()

        self.downloading_files = {}
        # update all folder  inother thread
        dirReaderDaemon.submit(self.readdirAsync,"/",100,dirReaderDaemon)  

    def unlink(self, path):
        self.disk.delete([path])


    def _add_file_to_buffer(self, path,file_info):
        foo = File()
        foo['st_ctime'] = file_info['local_ctime']
        foo['st_mtime'] = file_info['local_mtime']
        foo['st_mode'] = (stat.S_IFDIR | 0x777) if file_info['isdir'] \
            else (stat.S_IFREG | 0x777)
        foo['st_nlink'] = 2 if file_info['isdir'] else 1
        foo['st_size'] = file_info['size']
        self.buffer[path] = foo

    def emptyFileBuffer(self,path):
        foo = File()
        foo['st_ctime'] = 1391274570
        foo['st_mtime'] = 1391274570
        foo['st_mode'] =   (stat.S_IFDIR | 0x777)
        foo['st_nlink'] =  1
        foo['st_size'] = 1
        return foo

    def _del_file_from_buffer(self,path):
        self.buffer.pop(path)


    def getattr(self, path, fh=None):
        
        if path.split("/")[-1].startswith("."):
            raise FuseOSError(errno.ENOENT)
            
        if  path not in self.buffer:
            jdata = json.loads(self.disk.meta([path]))
       
            if 'info' not in jdata:
                raise FuseOSError(errno.ENOENT)
            if jdata['errno'] != 0:
                raise FuseOSError(errno.ENOENT)

            file_info = jdata['info'][0]
            self._add_file_to_buffer(path,file_info)
            st = self.buffer[path].getDict()
            return st
        else:
            return self.buffer[path].getDict()


    def readdirAsync(self,path,depth=2,threadPool=pool):
        try:
            foo = json.loads(self.disk.list_files(path))
        except Exception as s:
            logger.exception(s)

        files = ['.', '..']
        abs_files = []
        if 'errno' in foo:
            logger.error("maybe token is not right, try re login http://pan.baidu.com in Chrome")
        if "list" not in foo:
            logger.info("no list")
            return 


        for file in foo['list']:
            if file['server_filename'].startswith("."):
                continue
            files.append(file['server_filename'])
            abs_files.append(file['path'])
            logger.debug(file['path'])
 
        file_num = len(abs_files)
        group = int(math.ceil(file_num / 100.0))
        logger.debug(f"group: {group}")
        logger.debug(f"abs_files: {abs_files}")
        for i in range(group):
            obj = [f for n,f in enumerate(abs_files) if n % group == i] #一组数据
            while 1:
                try:
                    ret = json.loads(self.disk.meta(obj))
                    logger.debug(f'{ret}')
                    break
                except:
                    logger.info('error')
            for file_info in ret['info']:
                logger.debug(file_info)
                self._add_file_to_buffer(file_info['path'],file_info)
                if depth >0:
                    depth-=1
                    if file_info['isdir']:
                        if file_info['path'] not in self.traversed_folder:
                            self.traversed_folder[path] = True
                            threadPool.submit(self.readdirAsync,file_info['path'],depth,threadPool)  
        self.dir_buffer[path]=files


    
    def readdir(self, path, offset):
#         if path not in self.traversed_folder:
        self.traversed_folder[path] = True
        pool.submit(self.readdirAsync,path,2,pool)  
        if path  in self.dir_buffer:
            for r in self.dir_buffer[path]:
                yield r
        else:
            files = ['.', '..']
            for r in files:
                yield r

    def open(self, path, flags):
        # method does not have thread race problem, open by one thread only
        try:
            if path not in self.downloading_files:
                tmp = "./tmp"+path
                if path not in self.downloading_files:
                    if not os.path.exists(os.path.dirname(tmp)):
                        try:
                            os.makedirs(os.path.dirname(tmp))
                        except OSError as exc: 
                            # Guard against race condition
                            # don`t use lock as possiable as you can
                            pass
                url = self.disk.getRestUrl(path)
                x= Task(url,tmp,self.disk.getHeader())
                x.start()
                self.downloading_files[path] = x
        except Exception as e :
            logger.exception(e)
        return 0

    def release(self, path, fh):
        # method does not have thread race problem, release by one thread only
        if path in self.downloading_files:
#             self.downloading_files[path].terminate()
#             del self.downloading_files[path]
#             tmp = "./tmp"+path
#             logger.info("delete tmp:", tmp)
#             os.remove(tmp)
            pass


    def read(self, path, size, offset, fh):
        x = self.downloading_files[path]
        d = x.get_cache(offset,size)
        if not d :
            return None
        return d


    access = None
    statfs = None

if __name__ == '__main__':
    logger.info(colored("- fuse 4 cloud driver -", 'red'))
    FUSE(CloudFS(),sys.argv[1],foreground=True,nonempty=False,async_read=True)
