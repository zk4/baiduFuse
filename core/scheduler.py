#!/usr/bin/python
# -*- coding: utf-8 -*-

from concurrent.futures  import ThreadPoolExecutor as Pool
import queue
import requests 
import threading
import logging
from core.log import get_my_logger,funcLog

logger = get_my_logger(__name__)
logger.setLevel(logging.DEBUG)

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
    m =task.get_mmap()
    r = task.get_bytes({ 'Range': "bytes={0}-{1}" .format(start, start+size-1)})
    istart=start
    if not r.ok:
        logger.debug(f'{r},{r.text}')
        cache["error"]=True
        return 

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
                print("--->",istart,istart+dataLen,len(data),"/",task.get_file_size())
                logger.info(e)

            finally:
                if task.is_terminating():
                    return
            istart = istart + dataLen
    cache['status'] = "done"
    with cache["m"]:
        cache["m"].notifyAll()

q                  = queue.Queue()
threads            = []
num_worker_threads = 25

session = requests.Session()
a       = requests.adapters.HTTPAdapter(max_retries = 3,pool_connections = num_worker_threads*2, pool_maxsize = num_worker_threads*3)
session.mount('http://', a)
session.mount('https://', a)

for i in range(num_worker_threads):
    t = threading.Thread(target=target,daemon=True)
    t.start()
    threads.append(t)

