#!/usr/bin/python
# -*- coding: utf-8 -*-

import stat
import errno
import os
import sys
import math
import json
import time
import time
import tempfile
import argparse
from diskcache import Cache
from io import BytesIO
import logging
try:
    import _find_fuse_parts
except ImportError:
    pass
from fuse import FUSE, FuseOSError, Operations
from termcolor import colored
from colorama import Fore, Back, Style, init
from concurrent.futures  import ThreadPoolExecutor as Pool
from threading import Lock


from cloud.baidu import PCS 
from cloud.baidu_error import error_map 
from core.task  import Task
from core.custom_exceptions import *
from core.cipher import cipher

encrpted_length = 512

dirReaderDaemon = Pool(30)
pool = Pool(5)
attrPool=Pool(5)
uploadDaemon = Pool(10)

from core.log import funcLog,get_my_logger
logger = get_my_logger(__name__)

fileAttr={          
        'bd_fsid':0,
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
        'st_ctime':0
        }
class CloudFS(Operations):
    '''Baidu netdisk filesystem'''

    def __init__(self,mainArgs,  *args, **kw):
        self.buffer =Cache('./cache/buffer-batchmeta')
        self.dir_buffer =Cache('./cache/dir_buffer-buffer-batchmeta')

        self.attr_requesting = Cache('./cache/attr-requesting')
        self.mainArgs = mainArgs

        self.traversed_folder ={}# Cache('./cache/traversed-folder')
        self.disk = PCS(self.mainArgs)

        self.createLock = Lock()
        self.attrLock = Lock()

        self.writing_files={}
        self.downloading_files = {}


        if mainArgs.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(colored("- debug mode -", 'red'))
            logger.debug(colored("- cach would not be the same after restart -", 'red'))
            self.buffer =Cache('./cache/buffer-batchmeta'+str(time.time()))
            self.dir_buffer =Cache('./cache/dir_buffer-buffer-batchmeta'+str(time.time()))
            self.traversed_folder = Cache('./cache/traversed-folder'+str(time.time()))

        # update all folder  in other thread
        self._readDirAsync("/",3,dirReaderDaemon)


    def _baidu_file_attr_convert(self, path,file_info):
        foo = fileAttr.copy()
        foo['st_ctime'] = file_info['local_ctime']
        foo['st_mtime'] = file_info['local_mtime']
        foo['st_mode'] =  (stat.S_IFDIR | foo['st_mode'])  if file_info['isdir'] else ( stat.S_IFREG | foo['st_mode'] )
        foo['st_nlink'] = 2 if file_info['isdir'] else 1
        foo['st_size'] = file_info['size']
        self.buffer[path] = foo

    def _del_file_from_buffer(self,path):
        self.buffer.pop(path)

    def _getRootAttr(self,path):
        if path in self.buffer:
            return self.buffer[path]

        logger.debug(f'net root: {path}')
        jdata = json.loads(self.disk.meta([path]))

        if 'error_code' in jdata:
            logger.debug(f"error_code:{jdata}")
#             logger.info(f'{error_map[str(jdata["error_code"])]} args: {path}')
            self.buffer.set(path, fileAttr.copy(), expire=60)
            return fileAttr
            
        if "list" not in jdata or len(jdata["list"])==0:
            logger.debug(f"not list :{jdata}")
            self.buffer.set(path, fileAttr.copy(), expire=60)
            return fileAttr

        file_info = jdata["list"][0]
        self._baidu_file_attr_convert(path,file_info)
        return file_info


#     @funcLog
    def getattr(self, path, fh=None):
        if path in self.writing_files:
            return self.writing_files[path]

        if path.split("/")[-1].startswith("."):
            raise FuseOSError(errno.ENOENT)
        
        # special handle root Attr
        if path=="/":
            return self._getRootAttr(path)

        parentDir = os.path.dirname(path)
        if parentDir not in self.dir_buffer:
            self._readDir(parentDir,1)
        return  self.buffer.get(path,fileAttr.copy())


        # this path should handled in block mode,otherwise the mount point won`t show in finder disk but only  mount folder
        if "/" == path:
            with self.attrLock:
                return self.buffer.get("/")
            
        # request for new attr from cloud anyway
        if path not in self.attr_requesting:
            if path not in self.buffer:
                self.attr_requesting.set(path, True, expire=60)
                attrPool.submit(self._getRootAttr,path)

        return self.buffer.get(path,fileAttr)


    def _readDirAsync(self,path,depth,p):
       p.submit(self._readDir,path,depth,p)

    def _readDir(self,path,depth=2,threadPool=pool):
        if path not in self.traversed_folder and path not in self.dir_buffer:
            self.traversed_folder.set(path,b'1',expire=60)
            logger.debug(f'net dir  {depth} - {path} -')
            try:
                foo = json.loads(self.disk.list_files(path))

                files = ['.', '..']
                if 'error_code' in foo:
                    logger.info(f'{error_map[str(foo["error_code"])]} args: {path}')
                if "list" not in foo:
                    logger.info(f"{path}: no list")
                    return 

                depth-=1
                for file in foo['list']:
                    if file['server_filename'].startswith("."):
                        continue
                    files.append(file['server_filename'])
            #                 logger.debug(f'{file}')
                    self._baidu_file_attr_convert(file['path'],file)
                    if depth >0:
                        if file['isdir']:
                            self._readDirAsync(file['path'],depth,threadPool)
#                             self._readDir(file['path'],depth,threadPool)

                self.dir_buffer[path]=files

            except Exception as s:
                logger.exception(s)

#     @funcLog
    def readdir(self, path, offset):
        logger.debug(f'read dir ')
        self._readDirAsync(path,1,pool)
        if path  in self.dir_buffer:
            for r in self.dir_buffer[path]:
                yield r
        else:
            files = ['.', '..']
            for r in files:
                yield r

    
    # @funcLog
    def open(self, path, flags):
        if path  in self.writing_files:
            return 0
        # method does not have thread race problem, open by one thread only
        try:
            if path not in self.downloading_files:
                url = self.disk.getRestUrl(path)
                x= Task(url,mainArgs,path,self.disk)
                x.start()
                self.downloading_files[path] = x
        except Baidu8Secs as e:
            logger.exception(e)
        except Exception as e :
            logger.exception(e)
        return 0




    def read(self, path, size, offset, fh):
        x = self.downloading_files[path]
        if x:
            data = x.get_cache(offset,size)
            
            filename  = path[path.rfind("/")+1:]
            if filename.startswith("enc."):
                if offset ==0  :
                    if data and len(data)> encrpted_length:
                        data = bytes(cipher(data,0,encrpted_length,self.mainArgs.key))
                    else:
                        print("decrpt failed!")
            return data
            
        raise FuseOSError(errno.EIO)
    def updateCahe(self,old, new):
        directory = old[:old.rfind("/")]
        filename  = old[old.rfind("/")+1:]
        if len(directory) == 0:
            directory="/"
        if not new:
            oldCache = self.dir_buffer[directory]
            if filename in oldCache:
                oldCache.remove(filename)
                self.dir_buffer[directory] = oldCache
            if old in self.buffer:
                self.buffer.pop(old)
        else:
            oldCache = self.dir_buffer[directory]
            if filename in oldCache:
                oldCache.remove(filename)
                newfilename  = new[new.rfind("/")+1:]
                oldCache.append(newfilename)
                self.dir_buffer[directory]=oldCache
            if old in self.buffer:
                old_info = self.buffer.pop(old)
                self.buffer[new] = old_info

    def unlink(self, path):
        self.disk.delete([path])
        self.updateCahe(path,None)

    
    def access(self, path, amode):
        return 0

    def rmdir(self, path):
        self.disk.delete([path])
        self.updateCahe(path,None)

    def rename(self, old, new):
        self.disk.rename(old,new)
        self.updateCahe(old,new)

#     @funcLog
    def mkdir(self, path, mode):
        directory = path[:path.rfind("/")]
        filename  = path[path.rfind("/")+1:]
        
        cache = self.dir_buffer[directory]
        cache.append(filename)
        self.dir_buffer[directory]=cache
        self.disk.mkdir(path)

 
    @funcLog
    def create(self, path, mode,fh=None):
        logger.debug(f'create {path}')
        with self.createLock:
            if path not in self.writing_files:
                attr =fileAttr.copy()
                t = time.time()

                attr['uploading_tmp'] = tempfile.NamedTemporaryFile('wb')
                attr['st_mode'] =attr['st_mode']  | stat.S_IFREG |stat.S_ISUID | stat.S_ISGID

                self.writing_files[path] = attr
            else:
                logger.debug(f'{path} is writing on, wait another turn..')
        return 0

    def flush(self, path, fh):
        with self.createLock:
            if path in self.writing_files:
                self.writing_files[path]["uploading_tmp"].flush()
        return 0

   
    def release(self, path, fh):
        with self.createLock:
            if path in self.writing_files:
                uploading_tmp=self.writing_files[path]['uploading_tmp']
                self.disk.upload(uploading_tmp.name,path)
                self.writing_files[path]['uploading_tmp'].close()

                if path in self.writing_files:
                    del self.writing_files[path]

                # why ? prevent accidently read file when uploading still in progress
                if path in self.downloading_files:
                    del self.downloading_files[path]
                
                print("released",path)
                return  
        # method does not have thread race problem, release by one thread only
        if path in self.downloading_files:
#             self.downloading_files[path].terminate()
#             del self.downloading_files[path]
#             uploading_tmp = "./uploading_tmp"+path
#             logger.info("delete uploading_tmp:", uploading_tmp)
#             os.remove(uploading_tmp)
            pass

    def write(self, path, data, offset, fp):
        
        filename  = path[path.rfind("/")+1:]
        if filename.startswith("enc."):
            if offset == 0  and data and  len(data) > encrpted_length:
                data = bytes(cipher(data,0,encrpted_length,self.mainArgs.key))
    
        length = len(data)
        self.writing_files[path]["st_size"] += length
        self.writing_files[path]["uploading_tmp"].write(data)
       
        return length


    def chmod(self, path, mode):
        pass

    def statfs(self, path):
        # TODO read from cloud disk 
        return {'f_bavail': int(85533433401/4096), 'f_bfree': int(85533433401/4096),  # 相同的值  block
                'f_favail': 4290675908, 'f_ffree': 4290675908,  # 相同的值  node
                'f_bsize': 104857,  # perferd value 
        'f_blocks': int(5611374772224/8),  'f_files': 4294967279, 'f_flag': 0, 'f_frsize': 4096, 'f_namemax': 255}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
             formatter_class=argparse.RawDescriptionHelpFormatter,
             description='''
Ex: 
    # chmod 777 x.sh  &&  ./x.sh 


Encrption:
mountDisk --> fuse (encrpt) --> cloud 
mountDisk <-- fuse (decrpt) <-- cloud

Don`t change your key while there are already encrpyted file on cloud

    
''',
    )
    parser.add_argument("-m",'--mount', type=str, required=True, help='local mount point, default is ../mnt2 in x.sh')
    parser.add_argument("-k",'--key', type=str,default="123",required=False, help='specifiy encrpyt key, any length of string, will use it hash code')
    parser.add_argument("-b",'--BDUSS', type=str, required=False, help='By default, BDUSS  will be fetched from Chrome Browser automatically,but you can specifiy it manually')
    parser.add_argument("-d",'--debug', action='store_true',  help='debug mode')
    logger.info(colored("- fuse 4 cloud driver -", 'red'))

    mainArgs = parser.parse_args()

    FUSE(CloudFS(mainArgs),mainArgs.mount,foreground=True,nonempty=False,async_read=True,raw_fi=True)
