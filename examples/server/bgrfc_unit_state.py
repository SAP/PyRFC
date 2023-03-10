import sys
from pyrfc import Connection, RFCError

c = Connection(dest=sys.argv[1])

print(c.get_unit_state({"id": sys.argv[2], "background": True, "queued": True}))

c.close()
