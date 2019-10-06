
import json
blocklist = ["1","2"]
formatPaths = json.dumps(list(map(lambda p : p, blocklist)))
print(formatPaths)
