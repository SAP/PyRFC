from pyrfc import Server
from threading import Thread


# server function
def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc connection invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


# server authorisation check
def my_auth_check(func_name=False, request_context=None):
    if request_context is None:
        request_context = {}
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


# start server
def launch_server():
    # create server for ABAP system ABC
    server = Server(
        {"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False}
    )
    print(server.get_server_attributes())

    # expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
    server.add_function("STFC_CONNECTION", my_stfc_connection)

    # start server
    server.serve()

    # get server attributes
    print(server.get_server_attributes())


server_thread = Thread(target=launch_server)
server_thread.start()

input("Press Enter to stop server...")

# stop server
server_thread.join()
print("Server  stoped")
