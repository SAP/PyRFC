import os
from pyrfc import Server, set_ini_file_directory

# server function
def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


# server authorisation check
def my_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)

# create server instance
server = Server(
    {"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False}
)

# expose python function my_stfc_connection as ABAP function STFC_CONNECTION, that ABAP server can call
server.add_function("STFC_CONNECTION", my_stfc_connection)

# start server
server.serve()

# server = Server({"dest": "gateway"}, {"dest": "MME"}, {"auth_check": my_auth_check, "server_log": True})
