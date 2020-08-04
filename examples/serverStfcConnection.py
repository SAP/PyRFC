# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

from pyrfc import Server, Connection

from configparser import ConfigParser
import signal
import sys


config = ConfigParser()
config.read("sapnwrfc.cfg")

# Callback function
def my_stfc_connection(request_context, REQUTEXT=""):
    return {
        "ECHOTEXT": REQUTEXT,
        "RESPTEXT": u"Python server here. Connection attributes are: "
        u"User '{user}' from system '{sysId}', client '{client}', "
        u"host '{partnerHost}'".format(**request_context["connection_attributes"]),
    }


# Open a connection for retrieving the metadata of 'STFC_CONNECTION'
params_connection = config._sections["connection"]
print(params_connection)

conn = Connection(**params_connection)


func_desc_stfc_connection = conn.get_function_description("STFC_CONNECTION")
print(func_desc_stfc_connection)

# Instantiate server with gateway information for registering, and
# install a function.
params_gateway = config._sections["gateway"]
server = Server(**params_gateway)
server.install_function(func_desc_stfc_connection, my_stfc_connection)
print("--- Server registration and serving ---")
server.serve(20)

