# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata
import os

__version__ = importlib.metadata.version("xtest_sapnwrfc")
__version_info__ = tuple(__version__.split("."))

if os.name == "nt":
    # Set DLL path, per https://docs.python.org/3.8/whatsnew/3.8.html#bpo-36085-whatsnew
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

from ._utils import py_to_string, string_to_py

from ._cyrfc import (
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
    RfcFieldType
)

__author__ = "SAP SE"
__email__ = "srdjan.boskovic@sap.com"
