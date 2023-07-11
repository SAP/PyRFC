# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

"""pyrfc package."""

import importlib.metadata
import os
from contextlib import suppress

__version__ = importlib.metadata.version("pyrfc")
__version_info__ = tuple(__version__.split("."))

if os.name == "nt":
    # add SAP NWRFC SDK to DLL pth
    with suppress(Exception):
        os.add_dll_directory(os.path.join(os.environ["SAPNWRFC_HOME"], "lib"))

from pyrfc._exception import (
    ABAPApplicationError,
    ABAPRuntimeError,
    CommunicationError,
    ExternalApplicationError,
    ExternalAuthorizationError,
    ExternalRuntimeError,
    LogonError,
    RFCError,
    RFCLibError,
)

try:
    from pyrfc._cyrfc import (
        RCStatus,
        Connection,
        ConnectionParameters,
        Decimal,
        FunctionDescription,
        RfcFieldType,
        RfcParameterDirection,
        Server,
        Throughput,
        TypeDescription,
        UnitCallType,
        UnitState,
        cancel_connection,
        get_nwrfclib_version,
        language_iso_to_sap,
        language_sap_to_iso,
        reload_ini_file,
        set_cryptolib_path,
        set_ini_file_directory,
        set_locale_radix,
    )
except Exception as ex:
    # PyRFC module could not be loaded
    print(ex)

__author__ = "SAP SE"
__email__ = "srdjan.boskovic@sap.com"
