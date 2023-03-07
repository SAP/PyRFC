import os
from pyrfc import Connection, Server, set_ini_file_directory
from threading import Thread

SERVER = {
    "ALX": [{"dest": "ALX_GATEWAY"}, {"dest": "ALX"}, {"port": 8081, "server_log": False}],
    "QM7": [{"dest": "gatewayqm7"}, {"dest": "QM7"}, {"port": 8081, "server_log": False}],
    "MME": [{"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False}],
}

# client connection

client = Connection(dest="MME")

# server functions


def my_stfc_write_to_tcpic(request_context=None, RESTART_QNAME="", TCPICDAT=[]):
    print("my_stfc_write_to_tcpic")
    # print("request_context", request_context)
    print(f"RESTART_QNAME: {RESTART_QNAME}")
    print(f"TCPICDAT: {TCPICDAT}")

    try:
        unit = client.initialize_unit()

        print("unit:", unit)
        client.fill_and_submit_unit(
            unit,
            [("STFC_WRITE_TO_TCPIC", {"TCPICDAT": TCPICDAT})],
            queue_names=["RFCSDK_QUEUE_IN"],
            attributes={"lock": 1},
        )

    except Exception as ex:
        print(ex)
    return {"TCPICDAT": TCPICDAT}


def my_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


def myCheckFunction(rfcHandle, unit_identifier):
    print("myCheck", rfcHandle, unit_identifier)
    return 0


def myCommitFunction(rfcHandle, unit_identifier):
    print("myCommit", rfcHandle, unit_identifier)
    return 0


def myRollbackFunction(rfcHandle, unit_identifier):
    print("myRollback", rfcHandle, unit_identifier)
    return 0


def myConfirmFunction(rfcHandle, unit_identifier):
    print("myConfirm", rfcHandle, unit_identifier)
    return 0


def myGetStateFunction(rfcHandle, unit_identifier):
    print("myGetState", rfcHandle, unit_identifier)
    return 0


# dir_path = os.path.dirname(os.path.realpath(__file__))
# set_ini_file_directory(dir_path)


def server_serve(sid):
    server = Server(*SERVER[sid])
    print(server.get_server_attributes())

    server.add_function("STFC_WRITE_TO_TCPIC", my_stfc_write_to_tcpic)

    server.bgrfc_init(
        sid,
        {
            "check": myCheckFunction,
            "commit": myCommitFunction,
            "rollback": myRollbackFunction,
            "confirm": myConfirmFunction,
            "getState": myGetStateFunction,
        },
    )

    # start server
    server.serve()


# start server

server_thread = Thread(target=server_serve("ALX"))
server_thread.start()

input("Press Enter to stop server...\n")

server_thread.join()
