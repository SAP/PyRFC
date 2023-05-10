# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from pyrfc import Connection, RFCError

client = Connection(dest=sys.argv[1], config={"timeout": 5})

try:
    # 10 seconds long RFC call cancelled after 5 seconds
    # because of timeout set at connection level, for all RFC calls
    client.call(
        "RFC_PING_AND_WAIT",
        SECONDS=10,
    )
except RFCError as ex:
    print(ex.code, ex.key, ex.message)
    # 7 RFC_CANCELED Connection was canceled: 5067486720. New handle: 4806705664
