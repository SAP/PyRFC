# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from pyrfc import Connection

with Connection(dest=sys.argv[1]) as client:
    print(
        client.get_unit_state(
            {
                "id": sys.argv[2],
                "background": True,
                "queued": True,
            }
        )
    )

    client.close()
