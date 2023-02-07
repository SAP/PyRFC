import os
from pyrfc import Server, set_ini_file_directory
from threading import Thread

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


# server authorisation check


def my_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)


def myCheckFunction(rfcHandle, identifier, cls=None):
    print("myCheckFunction", rfcHandle, identifier)
    return 3


def myCommitFunction(rfcHandle, identifier, cls=None):
    print("myCommitFunction", rfcHandle, identifier)
    return 2


server1 = Server({"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False})

server1.bgrfc_init("SID", {"check": myCheckFunction, "commit": myCommitFunction})

server1.test()

# server2 = Server({"dest": "gatewayqm7"}, {"dest": "QM7"}, {"port": 8081, "server_log": False})
# Server.bgrfc_init({"commit": myCommitFunction})
# server2.test()
