import os
def test_rename():
    testFile = "/Users/zk/git/pythonPrj/mnt2/test/export2Mysql.py"
    os.rename(testFile,testFile+".new")
    assert os.path.exists(testFile+".new")
    os.rename(testFile+".new",testFile)
    assert os.path.exists(testFile)

