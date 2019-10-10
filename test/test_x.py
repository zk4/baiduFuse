#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import time
import hashlib

# def sha256sum(filename):
#     h  = hashlib.sha256()
#     b  = bytearray(128*1024)
#     mv = memoryview(b)
#     with open(filename, 'rb', buffering=0) as f:
#         for n in iter(lambda : f.readinto(mv), 0):
#             h.update(mv[:n])
#     return h.hexdigest()


# def test_open_file():
#     with open("../mnt2/demo.txt","r") as f:
#         assert "01234567890abcd" == f.readline()

# def test_read_binary_perf():
#     start_time = time.time()
#     with open("../mnt2/1.zip.chunk","rb") as f:
#         while True:
#             buffer = f.read(65536)
#             if not buffer:
#                 break
#     stop_time = time.time()
#     diff = stop_time - start_time
#     print(diff, "s")

