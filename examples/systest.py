# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sysconfig

print("From sysconfig:")
for k in "Py_DEBUG", "WITH_PYMALLOC", "Py_UNICODE_SIZE":
    try:
        print(k + ": " + repr(sysconfig.get_config_var(k)))
    except Exception as ex:
        print("Error getting %s" % k)

print("From headers:")
h_file = sysconfig.get_config_h_filename()
conf_vars = sysconfig.parse_config_h(open(h_file))
for k in "Py_DEBUG", "WITH_PYMALLOC", "Py_UNICODE_SIZE":
    try:
        print(k + ": " + repr(conf_vars[k]))
    except Exception as ex:
        print("Error getting %s" % k)
