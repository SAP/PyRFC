import sys
from pyrfc import Server, ExternalRuntimeError, ABAPRuntimeError, ABAPApplicationError
from threading import Thread
from backends import BACKEND

backend_dest = sys.argv[1]

errorInfo = {
    "code": 4, "key": "Function not supported",
    "message": "",
    "msg_class": "SR", "msg_type": "A", "msg_number": "006",
    "msg_v1": "",
    "msg_v2": "",
    "msg_v3": "",
    "msg_v4": ""
}

def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc connection invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    raise ExternalRuntimeError(**errorInfo)
    # raise ABAPRuntimeError(**errorInfo)
    # raise ABAPApplicationError(**errorInfo)

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}

def server_serve(sid):
    server = Server(*BACKEND[sid])
    print(server.get_server_attributes())

    # expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
    server.add_function("STFC_CONNECTION", my_stfc_connection)

    # start server
    server.serve()

# start server

server_thread = Thread(target=server_serve(backend_dest))
server_thread.start()
print("Server started")

input("Press Enter to stop server...")

server_thread.join()
