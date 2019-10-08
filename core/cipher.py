#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import sys
import random

def cipher(data,offset,size,intkey):
    bytw = bytearray()
    b = bytearray(1)
    random.seed(intkey) # key
    for i in range(offset,size):
        b[0]=  data[i] ^ random.randint(0, 255)
        bytw.extend(b)
    return bytw
