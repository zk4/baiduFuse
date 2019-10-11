import os
import time
def test_rename():
    testFile = "/Users/zk/git/pythonPrj/mnt2/1.zip.chunk"
    # with open(testFile,"w+") as f:
    #     f.write('0')

    os.rename(testFile,testFile+".new")
    assert os.path.exists(testFile+".new")

    os.rename(testFile+".new",testFile)
    assert os.path.exists(testFile)

def test_file_write_and_read_and_rm():
    testFile = "/Users/zk/git/pythonPrj/mnt2/test/"+str(int(time.time()))+".txt"
    with open(testFile,"w+") as f:
        f.write('2')

    with open(testFile,"r") as f:
        assert f.read() =="2"

    assert os.path.exists(testFile)

    os.remove(testFile)

    assert not os.path.exists(testFile)

def test_dir_mk_and_rm():
    testDir = "/Users/zk/git/pythonPrj/mnt2/test/"+str(int(time.time()))+"/"
    os.makedirs(testDir)

    assert os.path.exists(testDir)
    os.rmdir(testDir)

# not support yet
# def d_test_over_write():
#     testFile = "/Users/zk/git/pythonPrj/mnt2/test/"+str(int(time.time()))+".txt"
#     with open(testFile,"w+") as f:
#         f.write('0')

#     with open(testFile,"w") as f:
#         f.write('2')

#     with open(testFile,"r") as f:
#         assert f.readline() =="2"
