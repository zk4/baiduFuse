import argparse
from termcolor import colored
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
parser.add_argument("-p",'--proxy', action='store_true',default=False,  help='auto proxy at 127.0.0.1:18888 for debug')
parser.add_argument("-ct",'--cache_timeout', type=int, required=False, default=60, help='how many seconds will folder structure cache timeout')


mainArgs = parser.parse_args()

proxy_on ={}

if mainArgs.proxy:
    http_proxy  = "http://127.0.0.1:18888"
    proxyDict = { 
        "http"  : http_proxy,
        "https" : http_proxy,
        "ftp"   : http_proxy
    }
    proxy_on ={
        "verify":False,
        "proxies":proxyDict
    }

