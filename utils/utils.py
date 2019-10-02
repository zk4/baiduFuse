import os
from sys import platform


applescript = """
reattach-to-user-namespace osascript -e 'display notification "{}" with title "{}"'
"""

def notification(title="",content=""):
    if platform == "darwin":
        os.system(applescript.format(content,title))
