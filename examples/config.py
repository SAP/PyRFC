# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

from os import path
from configparser import ConfigParser

cp = ConfigParser()
cp.read(path.join(path.dirname(path.abspath(__file__)), "pyrfc.cfg"))

sections = cp.sections()
print(sections)
# ['p7019s16', 'coevi51', 'coe_he_66', 'gateway', 'connection_e1q']
coevi51_params = dict(cp.items("coevi51"))
print(coevi51_params)


def get_error(ex):
    error = {}
    ex_type_full = str(type(ex))
    print(ex_type_full)
    # error["type"] = ex_type_full[ex_type_full.rfind(".") + 1 : ex_type_full.rfind("'")]
    error["code"] = ex.code if hasattr(ex, "code") else "<None>"
    error["key"] = ex.key if hasattr(ex, "key") else "<None>"
    error["message"] = ex.message.split("\n")
    error["msg_class"] = ex.msg_class if hasattr(ex, "msg_class") else "<None>"
    error["msg_type"] = ex.msg_type if hasattr(ex, "msg_type") else "<None>"
    error["msg_number"] = ex.msg_number if hasattr(ex, "msg_number") else "<None>"
    error["msg_v1"] = ex.msg_v1 if hasattr(ex, "msg_v1") else "<None>"
    return error
