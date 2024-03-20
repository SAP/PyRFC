from time import sleep

from pyrfc import Connection, RCStatus, Server


def stfc_write_to_tcpic(request_context=None, RESTART_QNAME="", TCPICDAT=[]):
    context = (
        {"error": "No request context"}
        if request_context is None
        else request_context["server_context"]
    )
    print("[js] python function: stfc_write_to_tcpic", f"context {context}")
    return {"TCPICDAT": TCPICDAT}


def onCheckTransaction(rfcHandle, tid):
    print("[js] onCheckTransaction", rfcHandle, tid)
    return RCStatus.OK


def onCommitTransaction(rfcHandle, tid):
    print("[js] onCommitTransaction", rfcHandle, tid)
    return RCStatus.OK


def onConfirmTransaction(rfcHandle, tid):
    print("[js] onConfirmTransaction", rfcHandle, tid)
    return RCStatus.OK


def onRollbackTransaction(rfcHandle, tid):
    print("[js] onRollbackTransaction", rfcHandle, tid)
    return RCStatus.OK


def authenticationHandler(function_name, server_context=None):
    print(f"[js] authentication for {function_name}, context {server_context}")
    return RCStatus.OK


def authorizationHandler(rfcHandle=None, securityAttributes=None):
    print(f"[js] authorization for {rfcHandle}, security attr {securityAttributes}")
    return RCStatus.OK


# Create server
server = Server(
    server_params={"dest": "MME_GATEWAY"},
    client_params={"dest": "MME"},
    config={
        "authentication_check": authenticationHandler,
        "authorization_check": authorizationHandler,
        "check_date": False,
        "check_time": False,
        "server_log": True,
    },
)

# ABAP function used to send IDocs via tRFC/qRFC
server.add_function("STFC_WRITE_TO_TCPIC", stfc_write_to_tcpic)

# Register the RFC transaction handlers.
server.transaction_rfc_init(
    sysId="MME",
    transactionHandler={
        "check": onCheckTransaction,
        "commit": onCommitTransaction,
        "rollback": onRollbackTransaction,
        "confirm": onConfirmTransaction,
    },
)

try:
    # Start server
    server.start()

    # Get server attributes
    print(server.get_server_attributes())

    # Check transaction handlers
    # print(server.transaction_handlers)
    # print(server.transaction_handlers_count)

    # call RSARFCT0
    client = Connection(dest="MME")
    ncall = client.call("ZSERVER_TEST_TRFC", NCALL="00001")["EV_NCALL"]
    print("queues sent", ncall)
    client.close()

    # receive queues from abap system
    sleep(5)

except Exception as ex:
    print(ex)

finally:
    # Shutdown server
    server.close()
