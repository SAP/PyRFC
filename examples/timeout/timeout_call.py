# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pyrfc import Connection, RFCError

client = Connection(dest=sys.argv[1], config={"timeout": 20})

try:
    # 10 seconds long RFC call, cancelled after 5 seconds,
    # despite 15 seconds timeout at connection level
    client.call(
        "RFC_PING_AND_WAIT",
        options={"timeout": 5},
        SECONDS=10,
    )
except RFCError as ex:
    print(ex.code, ex.key, ex.message)
    # 7 RFC_CANCELED Connection was canceled: 5059097088. New handle: 4798322688
