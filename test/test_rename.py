import os
def test_rename():
    testFile = "/Users/zk/git/pythonPrj/mnt2/1.zip.chunk"
    # with open(testFile,"w+") as f:
    #     f.write('0')

    os.rename(testFile,testFile+".new")
    assert os.path.exists(testFile+".new")

    os.rename(testFile+".new",testFile)
    assert os.path.exists(testFile)

def test_mv_rm():
    testFile = "/Users/zk/git/pythonPrj/mnt2/1.zip.chunk"
    # with open(testFile,"w+") as f:
    #     f.write('0')

    os.rename(testFile,testFile+".new")
    assert os.path.exists(testFile+".new")

    os.rename(testFile+".new",testFile)
    assert os.path.exists(testFile)
