# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from backends import BACKEND
from pyrfc import RCStatus, Server, UnitCallType, UnitState
from tlog import TLog

backend_dest = sys.argv[1]

tlog = TLog()

# clear the log
tlog.remove()


def stfc_write_to_tcpic(request_context, RESTART_QNAME="", TCPICDAT=[]):
    try:
        context = request_context["server_context"]
        tid = context["unit_identifier"]["id"] if "unit_identifier" in context else None
        print(
            "server function: stfc_write_to_tcpic",
            "tid:",
            tid,
            "call:",
            UnitCallType.synchronous.value,
            context,
        )

        # if context["call_type"] != UnitCallType.synchronous:
        #     # Obtain the database connection that was opened for the
        #     # current TID context.tid in the onCheckTID handler.

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

        if context["call_type"] != UnitCallType.synchronous:  # SIM102
            # Store the data received in funcHandle as well as any results
            # computed in the business functionality of the FM (if any)
            # via the DB connection obtained above.
            # Optionally, if you want to make status tracking and forensic analysis
            # in case of an error easier, you can update the TID`s status to EXECUTED
            # in this step.
            if tid is not None:
                tlog.write(tid, UnitState.executed, "stfc_write_to_tcpic")
        return RCStatus.OK
    except Exception as ex:
        print("Error in stfc_write_to_tcpic", ex)
        return RCStatus.RFC_EXTERNAL_FAILURE


def on_auth_check(func_name=False, request_context=None):
    if request_context is None:
        request_context = {}
    print(f"authorization check for '{func_name}'")
    # print("request_context", request_context)
    return RCStatus.OK


def onCheckFunction(
    rfcHandle,
    unit_identifier,
):
    # section 5.5.1 pg 76 of SAP NWRFC SDK Programming Guide 7.50
    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE
    tid = unit_identifier["id"]
    tlog_record = tlog[tid]
    if tlog_record is None:
        # Create TID record
        tlog_record = tlog.write(tid, UnitState.created)
    print(
        "bgRFC:onCheck",
        f"handle {rfcHandle} tid {tid} status {tlog_record['status']}",
    )
    if tlog_record["status"] in [UnitState.created.name, UnitState.rolled_back.name]:
        return RCStatus.OK
    else:
        return RCStatus.RFC_EXECUTED


def onCommitFunction(rfcHandle, unit_identifier):
    # section 5.5.3 pg 79 of SAP NWRFC SDK Programming Guide 7.50
    print("bgRFC:onCommit handle", rfcHandle, "unit", unit_identifier)

    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE
    tid = unit_identifier["id"]
    tlog.write(tid, UnitState.committed)

    return RCStatus.OK


def onConfirmFunction(rfcHandle, unit_identifier):
    # section 5.5.4 pg 80 of SAP NWRFC SDK Programming Guide 7.50
    print("bgRFC:onConfirm handle", rfcHandle, "unit", unit_identifier)

    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE

    tid = unit_identifier["id"]
    tlog.write(tid, UnitState.confirmed)
    # or remove tid records from db
    # tlog.remove(tid)

    return RCStatus.OK


def onRollbackFunction(rfcHandle, unit_identifier):
    # section 5.5.3 pg 80 of SAP NWRFC SDK Programming Guide 7.50
    print("bgRFC:onRollback handle", rfcHandle, "unit", unit_identifier)

    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE

    tid = unit_identifier["id"]
    tlog.write(tid, UnitState.rolled_back)

    return RCStatus.RFC_OK


def onGetStateFunction(rfcHandle, unit_identifier):
    # section 5.6.3 pg 84 of SAP NWRFC SDK Programming Guide 7.50
    print("bgRFC:onGetState handle", rfcHandle, "unit", unit_identifier)

    if tlog is None:
        # TLog not available
        return RCStatus.RFC_EXTERNAL_FAILURE

    tid = unit_identifier["id"]
    tlog_record = tlog[tid]
    if tlog_record is None:
        return RCStatus.RFC_NOT_FOUND
    return RCStatus(tlog_record["status"])


# create server


server = Server(*BACKEND[backend_dest])
print(server.get_server_attributes())

try:
    # expose python function stfc_write_to_tcpic as ABAP function STFC_WRITE_TO_TCPIC,
    # to be called by ABAP system
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

    input("Press Enter key to stop server...\n")  # WPS110

    # stop server and database
    server.stop()

finally:
    # clean-up the server
    server.close()

tlog.dump()
