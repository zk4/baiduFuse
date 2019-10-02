import os
import time

key = "../mnt2/testkey.txt"
def test_is_mounted():
    assert os.path.exists(key)
    if not os.path.exists("../mnt2/test"):
        os.makedirs("../mnt2/test")

def test_file_write_and_rename_and_rm():
    testFile = "../mnt2/test/"+str(int(time.time()))+".txt"
    with open(testFile,"w+") as f:
        f.write('2')

    os.rename(testFile,testFile+".new")
    assert os.path.exists(testFile+".new")

    with open(testFile+".new","r") as f:
        assert f.read()=="2"
    os.rename(testFile+".new",testFile)
    assert os.path.exists(testFile)

    os.remove(testFile)

    assert not os.path.exists(testFile)

def test_key_content():
    with open(key,"r") as f:
        assert f.read() =="123456\n\n"

def test_file_write_and_read_and_rm():
    testFile = "../mnt2/test/"+str(int(time.time()))+".txt"
    with open(testFile,"w+") as f:
        f.write('2')

    with open(testFile,"r") as f:
        assert f.read() =="2"

    assert os.path.exists(testFile)

    os.remove(testFile)

    assert not os.path.exists(testFile)

def test_dir_mk_and_rm():
    testDir = "../mnt2/test/"+str(int(time.time()))+"/"
    os.makedirs(testDir)

    assert os.path.exists(testDir)
    os.rmdir(testDir)

# not support yet
def test_over_write():
    testFile = "../mnt2/test/"+str(int(time.time()))+".txt"
    with open(testFile,"w+") as f:
        f.write('10')

    with open(testFile,"r") as f:
        assert f.readline() =="10"
        
    with open(testFile,"w") as f:
        f.write('2')

    with open(testFile,"r") as f:
        assert f.readline() =="2"
    print('here..............')

