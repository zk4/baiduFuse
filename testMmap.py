import mmap
import os

def createMmap(filename,size, access=mmap.ACCESS_WRITE):
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

with open("test.data","wb") as f:
    f.seek(999)
    f.write(b'0')

m = createMmap("test.data",1000)
m[3:3+2]=b"he"


