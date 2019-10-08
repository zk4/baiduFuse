#!/usr/bin/python
# -*- coding: utf-8 -*-

from concurrent.futures  import ThreadPoolExecutor as Pool
import queue
import requests 
import threading
import logging
from log import logger,funcLog

def target():
  while True:
      try:
        tries = 1
        f, args,tries = q.get()
        f(*args)
      except Exception as e:
          logger.info(e)
          tries = tries+1

          if tries < 10:
              logger.warn("retry times:"+ str(tries))
              q.put((f,args,tries))

def handle(cache,task): 
    start=cache["start"]
    size=cache["size"]
    url=task.url
    user_headers=task.user_headers
    saved_path=task.saved_path
    m =task.mmap
    
    headers={ 'Range': "bytes={0}-{1}" .format(start, start+size-1), **user_headers}
    r = session.get(url,allow_redirects=True, headers=headers, stream=True) 

    istart=start

    block_size = 102400
    wrote =0
    for data in r.iter_content(block_size):
        if data:
            dataLen = len(data)
            try:
                m[istart:istart+dataLen]=data
                cache["cur"]=cache["cur"]+dataLen
                wrote += dataLen
                with cache["m"]:
                    if wrote >= 65536:
                        wrote = 0
                        cache["m"].notifyAll()

            except Exception as e:
                logger.info(e)

            finally:
                if task.terminating:
                    return
            istart = istart + dataLen
    cache['status'] = "done"
    with cache["m"]:
        cache["m"].notifyAll()

q                  = queue.Queue()
threads            = []
num_worker_threads = 250

session = requests.Session()
a       = requests.adapters.HTTPAdapter(max_retries = 3,pool_connections = num_worker_threads*2, pool_maxsize = num_worker_threads*3)
session.mount('http://', a)
session.mount('https://', a)

for i in range(num_worker_threads):
    t = threading.Thread(target=target,daemon=True)
    t.start()
    threads.append(t)

