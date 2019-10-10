
# feature 
- Support all disk manipulating with baidu cloud,including read,delete,mkdir,cp,mv,etc, highly optimized for reading. Try opening any file , even a big file. You shall see the magic.
- Read dir in async mode. (You may see empty dir,but with actual fiels on cloud, that is because some file manager cache dir structure(rancher) when dir data is still on the way back from cloud, you need to get around this by yourself.the best solution is: Do not use ranger,use fff nnn)
- Auto fetch credential from Chrome browser
- ! support local encrpyt,default key is `123`, steps:
  - add prefix `enc.` to  the local file name, ex   `1.mp4 -> enc.1.mp4`
  - move enc.1.mp4  to mounted baidu disk
  - enc.1.mp4 is only reasonable from mounted baidu disk, and is not when downloaded from baidu official client.

![arch](https://github.com/zk4/baiduFuse/blob/master/img/arch2.jpg)



# usage 
1. install python 3 
1. install dependencies `pip install -r requirements.txt`
1. login in http://pan.baidu.com with **chrome browser** (for the credential to fetch )
2. open fuse in shell
    ``` bash
    chmod 777 x.sh
    ./x.sh
    ```

![demo](https://github.com/zk4/baiduFuse/blob/master/img/d.gif)

# dev 
``` bash
# some dev tools, just for convenience. You could skip this,then you need to config the dev enviroment yourself
brew install watchexec 
pip install pipreqs

make dev 

# run test 
make test 

# create requirements.txt 
make dist 
```
# todo 
- [ ] improvment!!: reduce local disk size,( maybe download in memory)
- [ ] why open the file so fast after uploading an file?
- [ ] improvment: display true disk meta data
- [ ] improvment: when write with finder on mac, a lot of garbage file occurs with `.` or `_`  in the name prefix 
- [x] encrpytion on the fly! 
   Your file would be safer on any cloud. With a fast method to encrpt the file, you won't even notice it exists. The safety is not that storng, but enough for baidu censership.
- [ ] make encrpytion verisoned.
- [ ] add expried time to cache?
- [ ] improvment!! overwrite file. 
- [ ] encrpyt file already on cloud
# tips  
## mpv (ftp on fuse)
you can make a ftp server on moutned disk, but there is a catchy when pay media file with mpv. see the below.It is not a bug of this project.
https://github.com/mpv-player/mpv/issues/5449

make a demo server
``` bash
cd  /mnt/
python -m pyftpdlib
# play video (mpv version better than 0.21)
mpv    --cache=no  ftp://192.168.1.15:2121/2.mkv
mpv    --cache=no ftp://192.168.1.15:2121/锦绣良缘粤语Gotv/锦绣良缘19.mkv 
```

# help 

``` bash 
python3 x.py --help
```
