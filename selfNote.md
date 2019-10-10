
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
kk-  release
   will be called once



# reference 
just for myself reference
- [intro](https://www.stavros.io/posts/python-fuse-filesystem/)
- [intro 2](http://www.maastaar.net/fuse/linux/filesystem/c/2016/05/21/writing-a-simple-filesystem-using-fuse/)
- [stackoverflow](https://stackoverflow.com/questions/15604191/fuse-detailed-documentation)
- [how-to-mount-and-manage-non-native-file-systems-in-os-x-with-fuse](https://www.macworld.com/article/2855038/how-to-mount-and-manage-non-native-file-systems-in-os-x-with-fuse.html)
- [reference project ](https://github.com/joe42/CloudFusion)
- [ly0 github](https://github.com/ly0/baidu-fuse)

