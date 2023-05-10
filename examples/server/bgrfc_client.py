# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from pyrfc import Connection

client = Connection(dest=sys.argv[1])

unit = client.initialize_unit()

name = "BGRFC_TEST_OUTIN"
counter = "00001"

client.fill_and_submit_unit(
    unit,
    [("STFC_WRITE_TO_TCPIC", {"TCPICDAT": [f"{name:20}{counter:20}{unit['id']:32}"]})],
    queue_names=["RFCSDK_QUEUE_IN"],
    attributes={"lock": 1},
)

print(unit, client.get_unit_state(unit))

input("Press Enter ...\n")  # noqa WPS110

print(unit, client.get_unit_state(unit))

client.close()
