# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

"""pyrfc package."""

from contextlib import suppress
import importlib.metadata
import os


__version__ = importlib.metadata.version("pyrfc")
__version_info__ = tuple(__version__.split("."))

if os.name == "nt":
    # add SAP NWRFC SDK to DLL pth
    with suppress(Exception):
        os.add_dll_directory(os.path.join(os.environ["SAPNWRFC_HOME"], "lib"))

from pyrfc._exception import (  # noqa F401
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

from pyrfc._cyrfc import (  # noqa F401
    get_nwrfclib_version,
    reload_ini_file,
    set_ini_file_directory,
    set_cryptolib_path,
    set_locale_radix,
    language_iso_to_sap,
    language_sap_to_iso,
    cancel_connection,
    Connection,
    ConnectionParameters,
    Decimal,
    Throughput,
    TypeDescription,
    FunctionDescription,
    Server,
    UnitCallType,
    UnitState,
    RCStatus,
    RfcParameterDirection,
    RfcFieldType,
)

__author__ = "SAP SE"
__email__ = "srdjan.boskovic@sap.com"
