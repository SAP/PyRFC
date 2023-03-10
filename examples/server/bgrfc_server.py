import sys
from backends import BACKEND
from pyrfc import Connection, Server
from threading import Thread

backend_dest = sys.argv[1]

# client connection

client = Connection(dest=backend_dest)

# server functions


def stfc_write_to_tcpic(request_context=None, RESTART_QNAME="", TCPICDAT=[]):
    print("stfc_write_to_tcpic")
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


def on_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


def onCheckFunction(rfcHandle, unit_identifier):
    print("onCheck", rfcHandle, unit_identifier)
    return 0


def onCommitFunction(rfcHandle, unit_identifier):
    print("onCommit", rfcHandle, unit_identifier)
    return 0


def onRollbackFunction(rfcHandle, unit_identifier):
    print("onRollback", rfcHandle, unit_identifier)
    return 0


def onConfirmFunction(rfcHandle, unit_identifier):
    print("onConfirm", rfcHandle, unit_identifier)
    return 0


def onGetStateFunction(rfcHandle, unit_identifier):
    print("onGetState", rfcHandle, unit_identifier)
    return 0


def server_serve(sid):
    server = Server(*BACKEND[sid])
    print(server.get_server_attributes())

    server.add_function("STFC_WRITE_TO_TCPIC", stfc_write_to_tcpic)

    server.bgrfc_init(
        sid,
        {
            "check": onCheckFunction,
            "commit": onCommitFunction,
            "rollback": onRollbackFunction,
            "confirm": onConfirmFunction,
            "getState": onGetStateFunction,
        },
    )

    # start server
    server.serve()


# start server

server_thread = Thread(target=server_serve(backend_dest))
server_thread.start()

input("Press Enter key to stop server...\n")

server_thread.join()
