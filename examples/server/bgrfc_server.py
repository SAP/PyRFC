import sys
from backends import BACKEND
from pyrfc import Connection, Server, TIDStatus, RCStatus, TIDCallType
from dbtid import ServerDB

backend_dest = sys.argv[1]

db = ServerDB()

def stfc_write_to_tcpic(request_context, RESTART_QNAME="", TCPICDAT=[]):
    context = request_context['server_context']
    tid = context['unit_identifier']['id'] if 'unit_identifier' in context else None
    print("server function handler: stfc_write_to_tcpic", tid, context)

    if context["call_type"] != TIDCallType['synchronous']:
        # Obtain the database connection that was opened for the
        # current TID context.tid in the onCheckTID handler.
        pass

    # Implement functionality of function module MY_FUNCTION_MODULE, if any.
    # print(f"RESTART_QNAME: {RESTART_QNAME}")
    print(f"TCPICDAT: {TCPICDAT}")

    # try:
    #     unit = client.initialize_unit()
    #     print("unit:", unit)
    #     client.fill_and_submit_unit(
    #         unit,
    #         [("STFC_WRITE_TO_TCPIC", {"TCPICDAT": TCPICDAT})],
    #         queue_names=["RFCSDK_QUEUE_IN"],
    #         attributes={"lock": 1},
    #     )
    # except Exception as ex:
    #     print(ex)

    if context["call_type"] != TIDCallType['synchronous']:
        # Store the data received in funcHandle as well as any results
        # computed in the business functionality of the FM (if any)
        # via the DB connection obtained above.
        # Optionally, if you want to make status tracking and forensic analysis
        # in case of an error easier, you can update the TID’s status to EXECUTED
        # in this step.
        if tid is not None:
            db.set_tid_status(tid, TIDStatus['executed'], "stfc_write_to_tcpic")

    return {"TCPICDAT": TCPICDAT}


def on_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    # print("request_context", request_context)
    return RCStatus['OK']


def onCheckFunction(rfcHandle, unit_identifier):
    # section 5.5.1 pg 76 of SAP NWRFC SDK Programming Guide 7.50
    if db is None:
        return RCStatus.RFC_EXTERNAL_FAILURE
    tid = unit_identifier["id"]
    if tid not in db:
        # Create TID record
        db.set_tid_status(tid, TIDStatus['created'])
        return RCStatus['OK']
    tid_status = db[tid]
    print(":onCheck:", f"handle {rfcHandle} tid {tid} status {tid_status}")
    if tid_status["status"] in [TIDStatus['created'], TIDStatus['rolled_back']]:
        return RCStatus['OK']
    else:
        return RCStatus['RFC_EXECUTED']

def onCommitFunction(rfcHandle, unit_identifier):
    print("bgRFC:onCommit", f"handle {rfcHandle} tid {unit_identifier}")

    # StoreRC rc;
    # printfU(cU("Committing TID %s\n"), tid);
    # rc = setTIDStatus((RFC_TID)tid, Status_Committed, NULL);
    #  Obtain the database connection that was opened for the // current TID tid in the onCheckTID handler.
    # if (rc == RC_OK) {
    # Perform a COMMIT WORK on the DB connection and close it. // If the COMMIT WORK failed, set the TID status back to
    # Rolled Back, and then return RFC_EXTERNAL_FAILURE, so that // the backend will retry the LUW.
    # else {
    # If we cannot access the TID store at this time, we should // not commit the transaction to the database, because the // status in our status component may still be Created,
    # and the backend may retry the transaction at a later time, // leading to a duplicate.
    # Perform a ROLLBACK WORK on the DB connection and close it.
    # return RFC_EXTERNAL_FAILURE; }
    # return RFC_OK;

    return 0


def onRollbackFunction(rfcHandle, unit_identifier):
    print("bgRFC:onRollback", rfcHandle, unit_identifier)
    print(f"Rolling back TID {unit_identifier['id']}")

    # Obtain the database connection that was opened for the
    # current TID tid in the onCheckTID handler.
    # Perform a ROLLBACK WORK on that connection and close it.
    # setTIDStatus(tid, Status_RolledBack, NULL);
    return 0  # RFC_OK;

def onConfirmFunction(rfcHandle, unit_identifier):
    print("bgRFC:onConfirm", rfcHandle, unit_identifier)
    return 0


def onGetStateFunction(rfcHandle, unit_identifier):
    print("bgRFC:onGetState", rfcHandle, unit_identifier)
    return 0


# create server
server = Server(*BACKEND[backend_dest])

print(server.get_server_attributes())

# expose python function stfc_write_to_tcpic as ABAP function STFC_WRITE_TO_TCPIC, to be called by ABAP system
server.add_function("STFC_WRITE_TO_TCPIC", stfc_write_to_tcpic)

# register bgRFC handlers
server.bgrfc_init(
    backend_dest,
    {
        "check": onCheckFunction,
        "commit": onCommitFunction,
        "rollback": onRollbackFunction,
        "confirm": onConfirmFunction,
        "getState": onGetStateFunction,
    },
)

# start server
server.start()

input("Press Enter key to stop server...\n")

# stop server and database
server.stop()

db.close()
