from pyrfc import Connection

import pickle

client = Connection(dest="MME")

fd = client.get_function_description("BAPI_USER_GET_DETAIL")

print(fd)
