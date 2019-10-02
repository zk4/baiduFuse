#coding: utf-8

from concurrent.futures  import ThreadPoolExecutor as Pool
import time
pool = Pool(15)


def func(args):
    print(args)


pool.submit(func,1)
pool.submit(func,2)
pool.submit(func,3)






