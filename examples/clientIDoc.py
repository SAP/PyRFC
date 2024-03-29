# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0


import pyrfc
from pyrfc import ABAPApplicationError, ABAPRuntimeError, CommunicationError, LogonError


def initial_screen():
    choice = 9
    while choice not in [1, 2, 3, 4, 0]:
        print("\nPlease select one of the following choices:")
        print("\t1:\t Send a new IDoc (bgRFC, type 'T')")
        print("\t2:\t Send a new IDoc (bgRFC, type 'Q')")
        print("\t3:\t Send a new IDoc (tRFC)")
        print("\t4:\t Send a new IDoc (qRFC)")
        # print("\t2: Display current pending IDocs")
        print("\t0:\t Exit")
        try:
            choice = int(input("Enter choice: "))
        except ValueError:
            choice = 0
    return choice


def get_idoc_desc(idoc_id):
    idoc_control = {
        "TABNAM": "EDI_DC40",
        "MANDT": "000",
        "DOCNUM": "{0:016d}".format(idoc_id),
        "DIRECT": "2",
        "IDOCTYP": "TXTRAW01",
        "MESTYP": "TXTRAW",
        "SNDPRT": "LS",
        "SNDPRN": "SPJ_DEMO",
        "RCVPRT": "LS",
        "RCVPRN": "T90CLNT090",
    }
    idoc_data_dicts = []
    for idx in range(1, idoc_id + 1):
        idoc_data = {
            "SEGNAM": "E1TXTRW",
            "MANDT": "000",
            "DOCNUM": "{0:016d}".format(idoc_id),
            "SEGNUM": "{0:06d}".format(idx),
            "SDATA": f"Some chars with a - {idoc_id + idx} - number!",
        }
        idoc_data_dicts.append(idoc_data)
    return {
        "IDOC_CONTROL_REC_40": [idoc_control],
        "IDOC_DATA_REC_40": idoc_data_dicts,
    }


def main():
    params_connection = {"dest": "MME"}

    idoc_id = 1

    try:
        connection = pyrfc.Connection(**params_connection)
        print(connection.alive)
        while True:
            choice = initial_screen()
            if 1 <= choice <= 4:  # Create and send a new iDoc
                idoc = get_idoc_desc(idoc_id)
                print(f" - Created iDoc with idoc_id = {idoc_id}")
                idoc_id += 1
                if choice < 3:  # bgRFC
                    unit = connection.initialize_unit()
                    print(f" - (bgRFC) Using unit id = {unit['id']}")
                else:  # t/qRFC
                    unit = connection.initialize_unit(background=False)
                    print(f" - (t/qRFC) Using unit id = {unit['id']}")
                if choice == 2:  # bgRFC, type 'Q'
                    queue_input = input("Enter queue names (comma separated): ")
                    queue_names = [qi.strip() for qi in queue_input.split(",")]
                    connection.fill_and_submit_unit(
                        unit,
                        [("IDOC_INBOUND_ASYNCHRONOUS", idoc)],
                        queue_names=queue_names,
                    )
                elif choice == 4:  # qRFC
                    queue_input = input("Enter queue name: ")
                    queue = queue_input.strip()
                    connection.fill_and_submit_unit(
                        unit,
                        [("IDOC_INBOUND_ASYNCHRONOUS", idoc)],
                        queue_names=[queue],
                    )
                else:
                    connection.fill_and_submit_unit(
                        unit,
                        [("IDOC_INBOUND_ASYNCHRONOUS", idoc)],
                    )
                print(" - Unit filled and submitted.")
                connection.confirm_unit(unit)
                print(" - Unit confirmed and destroyed.")
            else:
                print(" Bye...")
                break
        connection.close()

    except CommunicationError:
        print("Could not connect to server.")
        raise
    except LogonError:
        print("Could not log in. Wrong credentials?")
        raise
    except (
        ABAPApplicationError,
        ABAPRuntimeError,
    ):
        print("An error occurred.")
        raise


if __name__ == "__main__":
    main()
