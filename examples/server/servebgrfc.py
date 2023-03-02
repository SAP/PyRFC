import os
from pyrfc import Server, set_ini_file_directory
from threading import Thread

SERVER = {
    "ALX": [{"dest": "ALX_GATEWAY"}, {"dest": "ALX"}, {"port": 8081, "server_log": False}],
    "QM7": [{"dest": "gatewayqm7"}, {"dest": "QM7"}, {"port": 8081, "server_log": False}],
    "MME": [{"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False}]
}

# server functions


def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc connection invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


def my_stfc_structure(request_context=None, IMPORTSTRUCT={}, RFCTABLE=[]):
    print("stfc structure invoked")
    print("request_context", request_context)
    ECHOSTRUCT = IMPORTSTRUCT
    if len(RFCTABLE) == 0:
        RFCTABLE = [ECHOSTRUCT]
    RESPTEXT = f"Python server response: {ECHOSTRUCT['RFCINT1']}, table rows: {len(RFCTABLE)}"
    print(f"ECHOSTRUCT: {ECHOSTRUCT}")
    print(f"RFCTABLE: {RFCTABLE}")
    print(f"RESPTEXT: {RESPTEXT}")

    return {"ECHOSTRUCT": ECHOSTRUCT, "RFCTABLE": RFCTABLE, "RESPTEXT": RESPTEXT}

def my_stfc_write_to_tcpic(request_context=None, RESTART_QNAME="", TCPICDAT=[]):
    print("my_stfc_write_to_tcpic")
    print("request_context", request_context)
    print(f"RFCTABLE: {RESTART_QNAME}")
    print(f"TCPICDAT: {TCPICDAT}")

    return {"TCPICDAT": TCPICDAT}


# server authorisation check


def my_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)


def myCheckFunction(rfcHandle, unit_identifier):
    print("myCheckFunction", rfcHandle, unit_identifier)
    return 3


def myCommitFunction(rfcHandle, unit_identifier):
    print("myCommitFunction", rfcHandle, unit_identifier)
    return 2


def server_serve(sid="SID"):
    server = Server(*SERVER[sid])
    print(server.get_server_attributes())

    server.add_function("STFC_CONNECTION", my_stfc_connection)
    server.add_function("STFC_WRITE_TO_TCPIC", my_stfc_write_to_tcpic)

    # start server
    server.serve()


# start server

server_thread = Thread(target=server_serve("ALX"))
server_thread.start()

input("Press Enter to stop server...")

server_thread.join()
