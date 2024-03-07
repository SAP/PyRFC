from pyrfc import RCStatus, Server


def handle_rfc(request_context=None, RESTART_QNAME="", TCPICDAT=[]):
    context = (
        {"error": "No request context"}
        if request_context is None
        else request_context["server_context"]
    )
    print("Python function: stfc_write_to_tcpic", f"context {context}")
    return {"TCPICDAT": TCPICDAT}


def onCheckTransaction(rfcHandle, tid):
    print("Executed onCheckTransaction Python function", rfcHandle, tid)
    return RCStatus.OK


def onCommitTransaction(rfcHandle, tid):
    print("Executed  onCommitTransaction Python function", rfcHandle, tid)
    return RCStatus.OK


def onConfirmTransaction(rfcHandle, tid):
    print("Executed onConfirmTransaction Python function", rfcHandle, tid)
    return RCStatus.OK


def onRollbackTransaction(rfcHandle, tid):
    print("Executed onRollbackTransaction Python function", rfcHandle, tid)
    return RCStatus.OK


# Create server


server = Server(
    server_params={"dest": "MME_GATEWAY"},
    client_params={"dest": "MME"},
    config={"check_date": False, "check_time": False, "server_log": True},
)

# ABAP function used to send IDocs via tRFC/qRFC
server.add_function("STFC_WRITE_TO_TCPIC", handle_rfc)

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
    # print(server.get_server_attributes())

    # Check transaction handlers
    # print(server.transaction_handlers)
    # print(server.transaction_handlers_count)

    input("Press Enter to stop server...\n")

    server.stop()
except Exception as ex:
    print(ex)

finally:
    # Shutdown server
    server.close()
