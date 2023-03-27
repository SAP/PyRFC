import sys
from backends import BACKEND
from pyrfc import Connection, Server, TIDStatus, RCStatus, TIDCallType
from tlog import TLog

backend_dest = sys.argv[1]

tlog = TLog()

tlog.clear()

def stfc_write_to_tcpic(request_context, RESTART_QNAME="", TCPICDAT=[]):
    try:
        context = request_context['server_context']
        tid = context['unit_identifier']['id'] if 'unit_identifier' in context else None
        print("server function: stfc_write_to_tcpic", "tid:", tid, "call:", TIDCallType.synchronous.value, context)

        if context["call_type"] != TIDCallType.synchronous:
            # Obtain the database connection that was opened for the
            # current TID context.tid in the onCheckTID handler.
            pass

        # Implement functionality of function module MY_FUNCTION_MODULE, if any.
        # print(f"RESTART_QNAME: {RESTART_QNAME}")
        print("TCPICDAT:", TCPICDAT)

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

        if context["call_type"] != TIDCallType.synchronous:
            # Store the data received in funcHandle as well as any results
            # computed in the business functionality of the FM (if any)
            # via the DB connection obtained above.
            # Optionally, if you want to make status tracking and forensic analysis
            # in case of an error easier, you can update the TID’s status to EXECUTED
            # in this step.
            if tid is not None:
                tlog.write(tid, TIDStatus.executed, "stfc_write_to_tcpic")
        return RCStatus.OK
    except Exception as ex:
        print("Error in stfc_write_to_tcpic", ex)
        return RCStatus.RFC_EXTERNAL_FAILURE


def on_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    # print("request_context", request_context)
    return RCStatus.OK

def onCheckFunction(rfcHandle, unit_identifier):
    # section 5.5.1 pg 76 of SAP NWRFC SDK Programming Guide 7.50
    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE
    tid = unit_identifier["id"]
    tlog_record = tlog[tid]
    if tlog_record is None:
        # Create TID record
        tlog_record = tlog.write(tid, TIDStatus.created)
    print("::onCheck", f"handle {rfcHandle} tid {tid} status {tlog_record['status']}")
    if tlog_record["status"] in [TIDStatus.created.name, TIDStatus.rolled_back.name]:
        return RCStatus.OK
    else:
        return RCStatus.RFC_EXECUTED

def onCommitFunction(rfcHandle, unit_identifier):
    print("::onCommit", f"handle {rfcHandle} unit {unit_identifier}")
    tid = unit_identifier["id"]
    tlog.write(tid, TIDStatus.committed)

    # StoreRC rc;
    # printfU(cU("Committing TID %s\n"), tid);
    # rc = setTIDStatus((RFC_TID)tid, Status_Committed, NULL);
    # Obtain the database connection that was opened for the current TID tid in the onCheckTID handler.
    # if (rc == RC_OK) {
    # Perform a COMMIT WORK on the DB connection and close it. // If the COMMIT WORK failed, set the TID status back to
    # Rolled Back, and then return RFC_EXTERNAL_FAILURE, so that // the backend will retry the LUW.
    # else {
    # If we cannot access the TID store at this time, we should // not commit the transaction to the database,
    # because the // status in our status component may still be Created,
    # and the backend may retry the transaction at a later time, // leading to a duplicate.
    # Perform a ROLLBACK WORK on the DB connection and close it.
    # return RFC_EXTERNAL_FAILURE; }
    # return RFC_OK;

    return RCStatus.OK

def onConfirmFunction(rfcHandle, unit_identifier):
    print("::onConfirm", rfcHandle, "unit", unit_identifier)

    tid = unit_identifier["id"]
    tlog.write(tid, TIDStatus.confirmed)
    return RCStatus.OK

def onRollbackFunction(rfcHandle, unit_identifier):
    print("::onRollback", rfcHandle, "unit", unit_identifier)

    # Obtain the database connection that was opened for the
    # current TID tid in the onCheckTID handler.
    # Perform a ROLLBACK WORK on that connection and close it.

    tid = unit_identifier["id"]
    tlog.write(tid, TIDStatus.rolled_back)

    return RCStatus.RFC_OK


def onGetStateFunction(rfcHandle, unit_identifier):
    # section 5.6.3 pg 84 of SAP NWRFC SDK Programming Guide 7.50
    print("::onGetState", rfcHandle, "unit", unit_identifier)

    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE

    tid = unit_identifier["id"]
    tlog_record = tlog[tid]
    if tlog_record is None:
        return RCStatus.RFC_NOT_FOUND
    return RCStatus(tlog_record['status'])

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

tlog.dump()
