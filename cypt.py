import sys
import random

def demo():
    if len(sys.argv) != 4:
        print("Usage: encdec2.py longintkey [path]filename1 [path]filename2")
        sys.exit()  
    bytw = bytearray()
    random.seed(int(sys.argv[1])) # key
    f1 = open( sys.argv[2], "rb")
    bytearr = f1.read ()
    f2 = open( sys.argv[3], "wb" )
    for i in range(len(bytearr)):
        bytw[0] = bytearr[i] ^ random.randint(0, 255)
        f2.write(bytw)
    f1.close()
    f2.close()


def cipher(data,offset,size,intkey):
    bytw = bytearray()
    b = bytearray(1)
    random.seed(intkey) # key
    for i in range(offset,size):
        b[0]=  data[i] ^ random.randint(0, 255)
        bytw.extend(b)
    return bytw


def encryt():
    f1 = open( "./test.md", "rb")
    bytearr = f1.read ()
    wrote = cipher(bytearr,0,3,123)
    f2 = open("./test.md.e" , "wb" )
    f2.write(wrote)
    f2.write(bytearr[3:])
    f2.close()
f1 = open( "./test.md.e", "rb")
b = f1.read ()
bytearr = bytearray(b)
bytearr[7]=ord('A')
wrote = cipher(bytearr,0,3,123)
f2 = open("./test.md.o" , "wb" )
f2.write(wrote)
f2.write(bytearr[3:])
f2.close()
