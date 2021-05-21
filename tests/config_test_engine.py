# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

###########################
# test_engine.py setup
user_engine = user
passwd_engine = passwd

params_engine = {
    "ashost": ashost,
    "client": client,
    "saprouter": saprouter,
    "sysnr": sysnr,
}

config_engine = {
    "connection.poolsize": "30",
    "connection.precreate": "1",
    "connection.reset_on_return": "true",
    "connection.ashost": ashost,
    "connection.client": client,
    "connection.saprouter": saprouter,
    "connection.sysnr": sysnr,
    "connection.lang": "de",  # TODO: Should this be here?
}
