# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# import from internal modules that they could be directly imported from
# the pyrfc package

# Set DLL path, per https://docs.python.org/3.8/whatsnew/3.8.html#bpo-36085-whatsnew

import os
from .version import __version_info__, __version__

if os.name == "nt":
    try:
        os.add_dll_directory(os.path.join(os.environ["SAPNWRFC_HOME"], "lib"))
    except Exception:
        pass

from ._exception import (
    RFCError,
    RFCLibError,
    CommunicationError,
    LogonError,
    ABAPApplicationError,
    ABAPRuntimeError,
    ExternalAuthorizationError,
    ExternalApplicationError,
    ExternalRuntimeError,
)

try:
    from ._cyrfc import (
        RfcParameterDirection,
        RfcFieldType,
        get_nwrfclib_version,
        py_to_string,
        string_to_py,
        reload_ini_file,
        set_ini_file_directory,
        set_cryptolib_path,
        set_locale_radix,
        language_iso_to_sap,
        language_sap_to_iso,
        cancel_connection,
        Connection,
        Decimal,
        Throughput,
        TypeDescription,
        FunctionDescription,
        Server,
        UnitCallType,
        UnitState,
        RCStatus,
        ConnectionParameters,
    )
except ModuleNotFoundError as ex:
    if "'src.pyrfc._cyrfc'" in ex.msg:
        # is ok, call from setup.py build
        pass
    else:
        raise ex

__author__ = "SAP SE"
__email__ = "srdjan.boskovic@sap.com"
