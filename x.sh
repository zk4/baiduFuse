#!/bin/bash
# kill local 
ps aux | grep "[m]nt2" | awk {'print $2'} |xargs kill -9 

# make requirements.txt
preqs --force .  &

diskutil unmount force  ../mnt2

/bin/rm -rdf ./tmp

python3 x.py  ../mnt2

# mpv -v  --cache-secs 7 mnt2/4.mp4
