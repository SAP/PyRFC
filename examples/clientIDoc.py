# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import pyrfc
from pyrfc import ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError

from ConfigParser import ConfigParser
import sys


def initial_screen():
    choice = 9
    while choice not in (1, 2, 3, 4, 0):
        print (u"\nPlease select one of the following choices:")
        print (u"\t1:\t Send a new IDoc (bgRFC, type 'T')")
        print (u"\t2:\t Send a new IDoc (bgRFC, type 'Q')")
        print (u"\t3:\t Send a new IDoc (tRFC)")
        print (u"\t4:\t Send a new IDoc (qRFC)")
        # print(u"\t2: Display current pending IDocs")
        print (u"\t0:\t Exit")
        var = raw_input(u"Enter choice: ")
        try:
            choice = int(var)
        except ValueError:
            choice = 0
    return choice


def get_idoc_desc(idoc_id):
    idoc_control = {
        u"TABNAM": u"EDI_DC40",
        u"MANDT": u"000",
        u"DOCNUM": u"{0:016d}".format(idoc_id),
        u"DIRECT": u"2",
        u"IDOCTYP": u"TXTRAW01",
        u"MESTYP": u"TXTRAW",
        u"SNDPRT": u"LS",
        u"SNDPRN": u"SPJ_DEMO",
        u"RCVPRT": u"LS",
        u"RCVPRN": u"T90CLNT090",
    }
    idoc_data_dicts = []
    for i in range(1, idoc_id + 1):
        idoc_data = {
            u"SEGNAM": u"E1TXTRW",
            u"MANDT": u"000",
            u"DOCNUM": u"{0:016d}".format(idoc_id),
            u"SEGNUM": u"{0:06d}".format(i),
            u"SDATA": u"Some chars with a - {} - number!".format(idoc_id + i),
        }
        idoc_data_dicts.append(idoc_data)
    return {u"IDOC_CONTROL_REC_40": [idoc_control], u"IDOC_DATA_REC_40": idoc_data_dicts}


def main():
    config = ConfigParser()
    config.read("sapnwrfc.cfg")
    params_connection = config._sections["connection"]

    idoc_id = 1

    try:
        connection = pyrfc.Connection(**params_connection)
        while True:
            choice = initial_screen()
            if 1 <= choice <= 4:  # Create and send a new iDoc
                idoc = get_idoc_desc(idoc_id)
                print u" - Created iDoc with idoc_id = {}".format(idoc_id)
                idoc_id += 1
                if choice < 3:  # bgRFC
                    unit = connection.initialize_unit()
                    print u" - (bgRFC) Using unit id = {}".format(unit["id"])
                else:  # t/qRFC
                    unit = connection.initialize_unit(background=False)
                    print u" - (t/qRFC) Using unit id = {}".format(unit["id"])
                if choice == 2:  # bgRFC, type 'Q'
                    queue_input = raw_input(u"Enter queue names (comma separated): ")
                    queue_names = [q.strip() for q in queue_input.split(",")]
                    connection.fill_and_submit_unit(
                        unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)], queue_names=queue_names
                    )
                elif choice == 4:  # qRFC
                    queue_input = raw_input(u"Enter queue name: ")
                    queue = queue_input.strip()
                    connection.fill_and_submit_unit(
                        unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)], queue_names=[queue]
                    )
                else:
                    connection.fill_and_submit_unit(unit, [(u"IDOC_INBOUND_ASYNCHRONOUS", idoc)])
                print u" - Unit filled and submitted."
                connection.confirm_unit(unit)
                print u" - Unit confirmed and destroyed."
            else:
                print u" Bye..."
                break
        connection.close()

    except CommunicationError:
        print u"Could not connect to server."
        raise
    except LogonError:
        print u"Could not log in. Wrong credentials?"
        raise
    except (ABAPApplicationError, ABAPRuntimeError):
        print u"An error occurred."
        raise


if __name__ == "__main__":
    main()
