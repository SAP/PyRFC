# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sysconfig

print("From sysconfig:")
for key in (
    "Py_DEBUG",
    "WITH_PYMALLOC",
    "Py_UNICODE_SIZE",
):
    try:
        print(key + ": " + repr(sysconfig.get_config_var(key)))
    except Exception as ex:
        print(
            "Error getting %s" % key,
            ex,
        )

print("From headers:")
h_file = sysconfig.get_config_h_filename()
with open(
    h_file,
    "r",
) as file:
    conf_vars = sysconfig.parse_config_h(file)
for key in (
    "Py_DEBUG",
    "WITH_PYMALLOC",
    "Py_UNICODE_SIZE",
):
    try:
        print(key + ": " + repr(conf_vars[key]))
    except Exception as ex:
        print(
            "Error getting %s" % key,
            ex,
        )
