
## feature 
- Support all disk manipulating with baidu cloud,including read,delete,mkdir,cp,mv,etc, highly optimized for reading. Try opening any file , even a big file. You shall see the magic.
- Read dir in async mode. (You may see empty dir,but with actual fiels on cloud, that is because some file manager cache dir structure(rancher) when dir data is still on the way back from cloud, you need to get around this by yourself.the best solution is: Do not use ranger,use fff nnn)
- Auto fetch credential from Chrome browser
- ! support local encrpyt,default key is `123`, steps:
  - add prefix `enc.` to  the local file name, ex   `1.mp4 -> enc.1.mp4`
  - move enc.1.mp4  to mounted baidu disk
  - enc.1.mp4 is only reasonable from mounted baidu disk, and is not when downloaded from baidu official client.

![arch](https://github.com/zk4/baiduFuse/blob/master/img/arch2.jpg)



## usage 
1. install python 3 
1. install dependencies `pip install -r requirements.txt`
1. login in http://pan.baidu.com with **chrome browser** (for the credential to fetch )
2. open fuse in shell
    ``` bash
    chmod 777 x.sh
    ./x.sh
    ```

![demo](https://github.com/zk4/baiduFuse/blob/master/img/d.gif)

## todo 
- [ ] improvment!!: reduce local disk size,( maybe download in memory)
- [ ] why open the file so fast after uploading an file?
- [ ] improvment: display true disk meta data
- [ ] improvment: when write with finder on mac, a lot of garbage file occurs with `.` or `_`  in the name prefix 
- [x] encrpyt on the fly! 
   this would be an exciting feature,you file would be safer on any cloud. I will try to use a fast method to encrpt the file . 
- [ ] No response reading from net will drop the read operation. This should be configurable, now it is fixed value 10 seconds.
- [ ] add expried time to cache?
## tips  
### mpv (ftp on fuse)
https://github.com/mpv-player/mpv/issues/5449

demo server
``` bash
cd  /mnt/
python -m pyftpdlib
# play video (mpv version better than 0.21)
mpv    --cache=no  ftp://192.168.1.15:2121/2.mkv
mpv    --cache=no ftp://192.168.1.15:2121/锦绣良缘粤语Gotv/锦绣良缘19.mkv 
```


## write file (beta)
Write file is a little bit tricky to implement in fuse. you can`t get source file name in fuse, but only source bytes. so a temp file is needed to be an mediator.
-  statfs 
   to confirm disk free size is avaiable 
-  create  
   normally create a file with open function, differs from open api in fuse interface which opens an existing file  
-  getattr 
   mainly check permission, and other file info 
-  write 
   will be called multipal times, write source bytes to remote 
-  flush 
   will be called once
-  release
   will be called once


## reference 
just for myself reference
- [intro](https://www.stavros.io/posts/python-fuse-filesystem/)
- [intro 2](http://www.maastaar.net/fuse/linux/filesystem/c/2016/05/21/writing-a-simple-filesystem-using-fuse/)
- [stackoverflow](https://stackoverflow.com/questions/15604191/fuse-detailed-documentation)
- [how-to-mount-and-manage-non-native-file-systems-in-os-x-with-fuse](https://www.macworld.com/article/2855038/how-to-mount-and-manage-non-native-file-systems-in-os-x-with-fuse.html)
- [reference project ](https://github.com/joe42/CloudFusion)
- [ly0 github](https://github.com/ly0/baidu-fuse)
