# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

from pyrfc import Connection

with Connection(dest="MME") as client:
    print(client.get_function_description("BAPI_USER_GET_DETAIL"))
