import os
from pyrfc import Server, set_ini_file_directory
from threading import Thread

# server functions


def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


def my_bapi_user(request_context=None, USERNAME=""):
    print("bapi user invoked")
    print("request_context", request_context)
    print(f"USERNAME: {USERNAME}")

    return {"USERNAME": USERNAME, "MESSAGE": "Python server here"}


# server authorisation check


def my_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)


def server1_serve():
    # create server for ABAP system ABC
    server = Server({"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False})
    print(server.get_server_attributes())

    # expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
    server.add_function("STFC_CONNECTION", my_stfc_connection)

    # start server
    server.serve()


def server2_serve():
    # create server for ABAP system XYZ
    server = Server({"dest": "gateway"}, {"dest": "QM7"}, {"port": 8081, "server_log": False})
    print(server.get_server_attributes())

    # expose python function my_bapi_user as ABAP function BAPI_USER_GET_DETAIL, to be called by ABAP system
    server.add_function("BAPI_USER_GET_DETAIL", my_bapi_user)

    # start server
    server.serve()


# start servers

server1_thread = Thread(target=server1_serve)
server1_thread.start()
print("Server1 started")

server2_thread = Thread(target=server2_serve)
server2_thread.start()
print("Server2 started")

input("Press Enter to stop server1...")

server1_thread.join()

input("Press Enter to stop server2...")
server2_thread.join()
