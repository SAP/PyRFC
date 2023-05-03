from pyrfc import Connection

with Connection(dest="MME") as client:
    print(client.get_function_description("BAPI_USER_GET_DETAIL"))
