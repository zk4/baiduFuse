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
        'st_ino':0,
        'st_dev':0,
        'st_mode':0,    # this is a trick point where write file and read file conflict
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
        logger.info(colored("- fuse 4 cloud driver -", 'red'))
        self.buffer =Cache('./cache/buffer-batchmeta')
        self.dir_buffer =Cache('./cache/dir_buffer-buffer-batchmeta')

        self.attr_requesting = Cache('./cache/attr-requesting')
        self.mainArgs = mainArgs

        self.traversed_folder = Cache('./cache/traversed-folder')
        self.disk = PCS(self.mainArgs)

        self.createLock = Lock()
        self.attrLock = Lock()

        self.writing_files={}
        self.downloading_files = {}

        logger.info(f'mainArgs:{mainArgs}')

        q = json.loads(self.disk.quota())

        # only request once 
        try:
            self.total_size =q['quota'] 
            self.used =q['used']
        except Exception as e:
            self.total_size =100000000000
            self.used =0
            logger.exception(e)
            logger.debug(f'con`t load quota api, fall back to default')

        self.avail =self.total_size -self.used

        if mainArgs.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(colored("- debug mode -", 'red'))
            logger.debug(colored("- cach would not be the same after restart -", 'red'))
            self.buffer =Cache('./cache/buffer-batchmeta'+str(time.time()))
            self.dir_buffer =Cache('./cache/dir_buffer-buffer-batchmeta'+str(time.time()))
            self.traversed_folder = Cache('./cache/traversed-folder'+str(time.time()))
            self._readDirAsync("/",2,dirReaderDaemon)
        else:
            logger.setLevel(logging.INFO)

            # update all folder  in other thread
            self._readDirAsync("/",mainArgs.preload_level,dirReaderDaemon)

    @staticmethod
    def add_write_permission(st,  permission = 'u'):
        """Add `w` (`write`) permission to specified targets."""
        mode_map = {
            'u': stat.S_IWUSR,
            'g': stat.S_IWGRP,
            'o': stat.S_IWOTH,
            'a': stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH,
        }
        logger.info(f'-------------------{type(stat.S_IWUSR)} ,{type(st["st_mode"])}')
        for t in permission:
            st['st_mode'] |= mode_map[t]

        return st

    def _baidu_file_attr_convert(self, path,file_info):
        foo = fileAttr.copy()
        try:
            foo['st_ctime'] =file_info['local_ctime'] if 'local_ctime' in file_info  else file_info['ctime'] 
            foo['st_mtime'] = file_info['local_mtime'] if 'local_mtime' in file_info  else file_info['mtime'] 
            foo['st_mode'] = 16877 if file_info['isdir'] else 36279
            foo['st_nlink'] = 2 if file_info['isdir'] else 1
            foo['st_size'] = int(file_info['size']) if 'size' in file_info else 0
            self.buffer[path] = foo
        except Exception as e:
            logger.debug(f'======================')
            logger.debug(f'add buffer error {e},{path}:{file_info}')

    def _del_file_from_buffer(self,path):
        self.buffer.pop(path)

    def _getRootAttr(self):
        path ="/"
        if path in self.buffer:
            return self.buffer[path]

        logger.debug(f'net root: {path}')
        jdata = json.loads(self.disk.meta([path]))

        f = fileAttr.copy()
        f["st_mode"]=16877
        f["st_nlink"]=2
        if 'error_code' in jdata and jdata["error_code"]!=0:
            logger.debug(f"error_code:{jdata}")
#             logger.info(f'{error_map[str(jdata["error_code"])]} args: {path}')
            self.buffer.set(path, f, expire=60)
            return f
            
        if "list" not in jdata or len(jdata["list"])==0:
            logger.debug(f"{path} not list :{jdata}")
            self.buffer.set(path, f, expire=60)
            return f

        file_info = jdata["list"][0]
        self._baidu_file_attr_convert(path,file_info)
        return file_info


    @funcLog
    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incompatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''
        if path in self.writing_files:
            return self.writing_files[path]

        if path.split("/")[-1].startswith("."):
            raise FuseOSError(errno.ENOENT)
        
        # special handle root Attr
        if path=="/":
            return self._getRootAttr()

        parentDir = os.path.dirname(path)
        if parentDir not in self.dir_buffer:
            self._readDir(parentDir,1)

        if path in self.buffer:
            return self.buffer[path]

        raise FuseOSError(errno.ENOENT)



    @funcLog
    def truncate(self, path, length, fh=None):
        self.unlink(path)
        self.create(path,None)
        self.writing_files[path]["uploading_tmp"].truncate(length)

    
    def _readDirAsync(self,path,depth,p):
       p.submit(self._readDir,path,depth,p)

    def _readDir(self,path,depth=2,threadPool=pool):
        if path not in self.traversed_folder :
            self.traversed_folder.set(path,b'1',expire=self.mainArgs.cache_timeout)
            logger.debug(f'net dir {depth} - {path} ')
            try:
                foo = json.loads(self.disk.list_files(path))

                files = ['.', '..']
                if 'error_code' in foo and foo["error_code"]!=0:
                    logger.info(f'{error_map[str(foo["error_code"])]} args: {path}')
                if "list" not in foo:
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

    @funcLog
    def readdir(self, path, offset):
        self._readDirAsync(path,1,pool)
        if path in self.dir_buffer:
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
    def updateCache(self,path,newValue):
        '''
        add     updateCache(path,value)
        delete  updateCache(path,None)
        udpate  updateCache(path,value)
        
        '''
        pass

    def updateCacheKeyOnly(self,old, new):
        '''
        delete     updateCacheKeyOnly(old,None)
        add/update updateCacheKeyOnly(old,new) 
        '''
        try:
            old_parent_dir   = os.path.dirname(old)
            old_name  = os.path.basename(old)
            if not new:
                oldCache = self.dir_buffer.get(old_parent_dir)
                # remove 
                if oldCache:
                    if old_name in oldCache:
                        oldCache.remove(old_name)
                        self.dir_buffer[old_parent_dir] = oldCache
                    if old in self.buffer:
                        self.buffer.pop(old)
                else:
                    pass
            else:
                print("updateCache",old,new)
                oldCache = self.dir_buffer[old_parent_dir]
                new_parent_dir   = os.path.dirname(new)
                if old_name in oldCache:
                    # dir old remove 
                    oldCache.remove(old_name)
                    self.dir_buffer[old_parent_dir]=oldCache
                    # dir new add
                    newfilename  = new[new.rfind("/")+1:]
                    newCache=self.dir_buffer.get( new_parent_dir,[] )
                    newCache.append(newfilename)
                    self.dir_buffer[new_parent_dir]=newCache

                if old in self.buffer:
                    old_info = self.buffer.pop(old)
                    self.buffer[new] = old_info
        except Exception as e :
            logger.info(e)

    def updateDir(self,old,new):
        pass

    def unlink(self, path):
        ''' 
        will only delete file
        '''
        print("unlink .....................")
        
        self.disk.delete([path])
        self.updateCacheKeyOnly(path,None)

    def rmdir(self, path):
        '''
        will only delete directory
        '''

        self.disk.delete([path])
        self.updateCacheKeyOnly(path,None)
    
    def access(self, path, amode):
        return 0

    def rename(self, old, new):
        '''
        will effect dir and file
        '''
        logger.info(f'rename {old}, {new}')
        self.disk.rename(old,new)
        self.updateCacheKeyOnly(old,new)

    @funcLog
    def mkdir(self, path, mode):
        logger.info(f'making dir {path}')
        
        r = json.loads(self.disk.mkdir(path))
        
        if 'error_code' in r:
            logger.info(f'{r}')
            logger.info(f'{error_map[str(r["error_code"])]} args: {path}, response:{r}')
            return 


        directory = path[:path.rfind("/")]
        filename  = path[path.rfind("/")+1:]

        cache = None
        if directory in self.dir_buffer:
            cache = self.dir_buffer[directory]
            cache.append(filename)
        self.dir_buffer[directory]=cache

        
        self._baidu_file_attr_convert(path,r)

 
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
                r =json.loads(self.disk.upload(uploading_tmp.name,path))
                logger.info(f'================================={r}')

                self.writing_files[path]['uploading_tmp'].close()
#                 if path in self.buffer:
#                     del self.buffer[path]

                if path in self.writing_files:
                    del self.writing_files[path]

                # why ? prevent accidently read file when uploading still in progress
                if path in self.downloading_files:
                    del self.downloading_files[path]
                

		# update file 
                self._baidu_file_attr_convert(path,r)

                # update parent dir
                parentDir = os.path.dirname(path)
                filename  = path[path.rfind("/")+1:]

                if  parentDir in self.dir_buffer:
                    parentDirCache = self.dir_buffer[parentDir]
                    parentDirCache.append(filename)
                    self.dir_buffer[parentDir]=parentDirCache
                    logger.info(f'{self.dir_buffer[parentDir]}')
                  

                
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
        return {'f_bavail': int((self.avail)/4096), 'f_bfree': int((self.avail)/4096),  # 相同的值  block
                'f_favail': 4290675908, 'f_ffree': 4290675908,  # 相同的值  node
                'f_bsize': 104857,  # perferd value 
        'f_blocks': int(self.total_size/8),  'f_files': 4294967279, 'f_flag': 0, 'f_frsize': 4096, 'f_namemax': 255}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
             formatter_class=argparse.RawDescriptionHelpFormatter,
             description=f'''

{ colored("There are two entries", 'red') }
x.py  # this is the main entry, for developer, you know what you are doing. 

  python3 x.py --help

x.sh  # this is the one for noobie. Just use it. Don`t ask why.


  chmod 777 x.sh  &&  ./x.sh 

{ colored("Encrption", 'red') }
mountDisk --> fuse (encrpt) --> cloud 

mountDisk <-- fuse (decrpt) <-- cloud
Don`t change your key while there are already encrpyted file on cloud

    
''',
    )
    parser.add_argument("-m",'--mount', type=str, required=True, help='local mount point, default is ../mnt2 in x.sh')
    parser.add_argument("-k",'--key', type=str,default="123",required=False, help='specifiy encrpyt key, any length of string, will use it hash code')
    parser.add_argument("-b",'--BDUSS', type=str, required=False, help='By default, BDUSS  will be fetched from Chrome Browser automatically,but you can specifiy it manually')
    parser.add_argument("-pl",'--preload_level', type=int, required=False, default=10, help='how many dir level do you wnat to preload')
    parser.add_argument("-d",'--debug', action='store_true',  help='debug mode')
    parser.add_argument("-ct",'--cache_timeout', type=int, required=False, default=60, help='how many seconds will folder structure cache timeout')

    mainArgs = parser.parse_args()

    FUSE(CloudFS(mainArgs),mainArgs.mount,foreground=True,nonempty=False,async_read=True,raw_fi=True)
