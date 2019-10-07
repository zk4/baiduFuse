import os

applescript = """
reattach-to-user-namespace osascript -e 'display notification "{}" with title "{}"'
"""

def notification(title="",content=""):
    os.system(applescript.format(content,title))
