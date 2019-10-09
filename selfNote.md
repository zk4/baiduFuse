
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

