#!/bin/bash
ps aux | grep "[m]nt2" | awk {'print $2'} |xargs kill -9 

diskutil unmount force  ../mnt2
/bin/rm -rdf ./tmp
python x.py  ../mnt2

# mpv -v  --cache-secs 7 mnt2/4.mp4
