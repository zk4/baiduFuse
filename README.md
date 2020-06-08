
> 百度 rest 接口基本不可用了. 这个项目基于 rest, 所以读文件基本废了. 时不时会抽风. 有个新思路, 正在研究中. 欢迎讨论 [链接](https://github.com/zk4/baiduFuse/issues?q=is%3Aissue+is%3Aopen+label%3A%E6%96%B0%E7%89%88%E6%9C%AC%E8%AE%A8%E8%AE%BA)

这个项目让你可以挂载百度磁盘。
<!-- vim-markdown-toc GFM -->

* [特性](#feature)
* [使用方法](#usage)
* [开发](#dev)
* [待办](#todo)
* [小技巧](#tips)
  * [mpv (ftp on fuse)](#mpv-ftp-on-fuse)
* [帮助](#help)


<!-- vim-markdown-toc -->
# 特性
- 支持所有的百度盘磁盘操作。
  包括文件、文件夹的增删改，对读做了优化，即使打开远程一个非常大的文件，只要你本地的应用程序支持异步加载。你可以飞快的打开文件。
- 文件夹以异步读取。
  你有可能会在本地看到空文件夹，但你知道在云端文件夹里是有内容的。这是因为，有一些文件管理器会缓存你的文件夹结构，比如finder，ranger 之类的，刷新一下就好
- 自动从 chrome 获取权限。
- 支持本地加密。默认密码为 `123`。 可以通过 -k 参数指定密码.
  步骤:
  - 将你想要加密的**本地文件**（还没上传云端的），文件名前面加上`enc.`, ex   `1.mp4 -> enc.1.mp4`
  - 将 enc.1.mp4  移动到你挂载的本地磁盘里
  - 通过挂载本地磁盘读取 enc.1.mp4 将会自动解密，但如果你通过百度官方客户端下载文件时，你会发现打不开。

![arch](https://github.com/zk4/baiduFuse/blob/master/img/arch2.jpg)



# 使用方法 
- 安装 python 3 
- 安装依赖 `pip install -r requirements.txt`
- 安装 fuselib， 因为 mac 是我的开发环境，最没问题的就是 mac 版，其他版本只能说理论没问题。
  - (Mac)    https://osxfuse.github.io/
  - (Linux)    https://osxfuse.github.io/  
     ```bash
     拿 centos 举例
      yum install fuse fuse-devel
     ```
  - (Windows)  https://github.com/billziss-gh/winfsp

- 通过 **chrome** 浏览器登陆自动拿权限  http://pan.baidu.com
- 进入 shell
  -  mac 平台
    ``` bash
    chmod 777 x.sh
    ./x.sh
    ```

  -  windows 平台 - 还是有很多 bug，通过 chrome 拿 BDUSS 可能会有权限问题,你可以手动指定，BDUSS 怎么拿可以自己网上搜一下哈。 
  ``` bat
  python x.py -m 'mnt2' -k 123 -d -b  <BDUSS>
  ```

![demo](https://github.com/zk4/baiduFuse/blob/master/img/d.gif)

# 开发 
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
# 待办 
- [ ] improvment!!: reduce local disk size,( maybe download in memory)
- [ ] improvment: when write with finder on mac, a lot of garbage file occurs with `.` or `_`  in the name prefix 
- [ ] make encrpytion verisoned.
- [ ] add expried time to cache?
- [ ] encrpyt file already on cloud
- [ ] auto version update, I may change data structure. Cache will not be compatiable 
- [ ] when using finder on Mac, handle the finder default request folder specially, make it configruable
- [ ] support fast move
- [ ] support LVM for multipal cloud disk. 
# tips  
## mpv (ftp on fuse)
you can make a ftp server on moutned disk, but there is a catchy when play media file with mpv. see the below.It is not a bug of this project.
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
 
