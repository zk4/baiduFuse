#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import sys
import random

def cipher(data,offset,size,key):
    bytw = bytearray(data)
    b = bytearray(1)
    random.seed(key) # key
    for i in range(offset,size):
        b[0]=  data[i] ^ random.randint(0, 255)
        bytw[i] = ord(b)
    return bytw
