import ujson as json
import sys
sys.path.append("..")

from cogs.utils.path import path

p = path()

print("Please Wait...")
with open(p + "/json/stats.json", "w") as s:
    stats = {
        'servers': {},
        'users': {}
    }

    json.dump(stats, s, indent=4)
    print("Created Stats JSON")

print("Done.")
