
## feature 
- support any local application!  use cloud driver as local driver.
- read dir in async mode. (You may see empty dir,but with actual fiels on cloud, that is because some file manager cache dir structure(rancher) when dir data is still on the way back from cloud, you need to get around this by yourself.the best solution is: Do not use ranger,use fff nnn)
- net scheduler is optimized for local read



![demo](https://github.com/zk4/baiduFuse/blob/master/img/d.gif)


## cloud driver support
- [x] 百度盘 
 - support read , delete, mv(rename) , highly optimized for media stream.
 - auto fetch credential from Chrome browser

Patch the other cloud dirver is super easy. Check cloud/baidu.py. Make a pull request.
## usage 
1. install python 3 
1. install dependencies `pip install -r requirements.txt`
1. login in http://pan.baidu.com with **chrome browser** (for the credential to fetch )
2. open fuse in shell
    ``` bash
    chmod 777 x.sh
    ./x.sh
    ```

## todo 
- [ ] improvment: when close local application, too slow.
- [ ] improvment: reduce local disk size,( evict, download in memory)
- [x] feature: support write to cloud ( on `write` branch)
  - [ ] improvment: when uploading, file flicks in finder on mac 
  - [ ] bug: upload file not update cache 
  - [x] bug: upload file not openable in current session
    - [ ] why open the file so fast after uploading an file?
  - [ ] bug: mutli files upload results a lot of dotted copy file on mac
  - [x] improvment: mac uploading icon not rotating
  - [x] improvment: upload file in other thread:  no need 
- [ ] bug: display true disk meta data
  



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
Write file is a little bit tricky. you can`t get source file name, but only source bytes
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
