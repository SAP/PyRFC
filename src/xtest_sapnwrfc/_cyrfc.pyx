# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

""" The _pyrfc C-extension module """

from libc.stdlib cimport malloc, free
from libc.stdint cimport uintptr_t
from collections.abc import Iterable
from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum, auto
from locale import localeconv
from os.path import isfile, join
from sys import exc_info, platform
import socket
from threading import Thread, Timer

from . csapnwrfc cimport *
from . _exception import *
from . _utils import enum_names, enum_values


################################################################################
# Configuration options
################################################################################

# configuration bitmasks, internal use
_MASK_DTIME = 0x01
_MASK_RETURN_IMPORT_PARAMS = 0x02
_MASK_RSTRIP = 0x04

_LOCALE_RADIX = localeconv()["decimal_point"]

################################################################################
# Enumerators, external and internal use
################################################################################


# RFC parameter direction
class RfcParameterDirection(Enum):
    RFC_IMPORT = RFC_DIRECTION.RFC_IMPORT
    RFC_EXPORT = RFC_DIRECTION.RFC_EXPORT
    RFC_CHANGING = RFC_DIRECTION.RFC_CHANGING
    RFC_TABLES = RFC_DIRECTION.RFC_TABLES


# RFC field type
class RfcFieldType(Enum):
    RFCTYPE_CHAR = RFCTYPE.RFCTYPE_CHAR
    RFCTYPE_DATE = RFCTYPE.RFCTYPE_DATE
    RFCTYPE_BCD = RFCTYPE.RFCTYPE_BCD
    RFCTYPE_TIME = RFCTYPE.RFCTYPE_TIME
    RFCTYPE_BYTE = RFCTYPE.RFCTYPE_BYTE
    RFCTYPE_TABLE = RFCTYPE.RFCTYPE_TABLE
    RFCTYPE_NUM = RFCTYPE.RFCTYPE_NUM
    RFCTYPE_FLOAT = RFCTYPE.RFCTYPE_FLOAT
    RFCTYPE_INT = RFCTYPE.RFCTYPE_INT
    RFCTYPE_INT2 = RFCTYPE.RFCTYPE_INT2
    RFCTYPE_INT1 = RFCTYPE.RFCTYPE_INT1
    RFCTYPE_NULL = RFCTYPE.RFCTYPE_NULL
    RFCTYPE_ABAPOBJECT = RFCTYPE.RFCTYPE_ABAPOBJECT
    RFCTYPE_STRUCTURE = RFCTYPE.RFCTYPE_STRUCTURE
    RFCTYPE_DECF16 = RFCTYPE.RFCTYPE_DECF16
    RFCTYPE_DECF34 = RFCTYPE.RFCTYPE_DECF34
    RFCTYPE_XMLDATA = RFCTYPE.RFCTYPE_XMLDATA
    RFCTYPE_STRING = RFCTYPE.RFCTYPE_STRING
    RFCTYPE_XSTRING = RFCTYPE.RFCTYPE_XSTRING
    RFCTYPE_INT8 = RFCTYPE.RFCTYPE_INT8
    RFCTYPE_UTCLONG = RFCTYPE.RFCTYPE_UTCLONG
    RFCTYPE_UTCSECOND = RFCTYPE.RFCTYPE_UTCSECOND
    RFCTYPE_UTCMINUTE = RFCTYPE.RFCTYPE_UTCMINUTE
    RFCTYPE_DTDAY = RFCTYPE.RFCTYPE_DTDAY
    RFCTYPE_DTWEEK = RFCTYPE.RFCTYPE_DTWEEK
    RFCTYPE_DTMONTH = RFCTYPE.RFCTYPE_DTMONTH
    RFCTYPE_TSECOND = RFCTYPE.RFCTYPE_TSECOND
    RFCTYPE_TMINUTE = RFCTYPE.RFCTYPE_TMINUTE
    RFCTYPE_CDAY = RFCTYPE.RFCTYPE_CDAY


# bgRFC unit state
class UnitState(Enum):
    not_found = RFC_UNIT_STATE.RFC_UNIT_NOT_FOUND
    in_process = RFC_UNIT_STATE.RFC_UNIT_IN_PROCESS
    committed = RFC_UNIT_STATE.RFC_UNIT_COMMITTED
    rolled_back = RFC_UNIT_STATE.RFC_UNIT_ROLLED_BACK
    confirmed = RFC_UNIT_STATE.RFC_UNIT_CONFIRMED
    created = auto()
    executed = auto()


# bgRFC status
class RCStatus(Enum):
    OK = RFC_RC.RFC_OK
    RFC_NOT_FOUND = RFC_RC.RFC_NOT_FOUND
    RFC_EXTERNAL_FAILURE = RFC_RC.RFC_EXTERNAL_FAILURE
    RFC_EXECUTED = RFC_RC.RFC_EXECUTED


# bgRFCunit call type
class UnitCallType(Enum):
    synchronous = RFC_CALL_TYPE.RFC_SYNCHRONOUS
    transactional = RFC_CALL_TYPE.RFC_TRANSACTIONAL
    queued = RFC_CALL_TYPE.RFC_QUEUED
    background_unit = RFC_CALL_TYPE.RFC_BACKGROUND_UNIT

################################################################################
# NW RFC SDK FUNCTIONALITY
################################################################################


def get_nwrfclib_version():
    """Get SAP NW RFC Lib version
    :returns: tuple of major, minor and patch level and OS platform
    """
    cdef unsigned major = 0
    cdef unsigned minor = 0
    cdef unsigned patchlevel = 0
    RfcGetVersion(&major, &minor, &patchlevel)
    return {'major': major, 'minor': minor, 'patchLevel': patchlevel, 'platform': platform}


def set_ini_file_directory(path_name):
    """Sets the directory in which to search for the sapnwrfc.ini file

    :param path_name: Directory in which to search for the sapnwrfc.ini file.
    :type path_name: string

    :return: nothing, raises an error
    """
    if type(path_name) is not str:
        raise TypeError('sapnwrfc.ini path is not a string:', path_name)
    cdef RFC_ERROR_INFO errorInfo
    cdef SAP_UC pathName [512]
    if not isfile(join(path_name, "sapnwrfc.ini")):
        raise TypeError('sapnwrfc.ini not found in:', path_name)
    pathName = fillString(path_name)
    cdef RFC_RC rc = RfcSetIniPath(pathName, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)


def reload_ini_file():
    """Reloads the contents of the sapnwrfc.ini file into memory.

    Searches the directory given by ``RfcSetIniPath()`` (or the current working directory)
    for the file sapnwrfc.ini and loads its contents into memory. Reloading the sapnwrfc.ini
    file is only necessary after the file has been manually edited.
    If you want to use a sapnwrfc.ini file in a different location, consider using ``RfcSetIniPath()``.

    Note: If a file with the name ``sapnwrfc.ini`` does not exist in the given directory,
    this is not considered an error! Default settings are used in this case.

    :return: nothing, raises an error
    """
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_RC rc = RfcReloadIniFile (&errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)


def language_iso_to_sap(lang_iso):
    """Language code conversion of ISO code to SAP code.

    :param lang_iso: Language ISO code
    :type lang_iso: string

    :return: SAP language code of char 1 type

    :raises: :exc:`~pyrfc.RFCError` or a subclass
                if ISO to SAP code conversion fails.
    """
    cdef SAP_UC *uclang_iso = fillString(lang_iso)
    cdef SAP_UC uclang_sap[8]
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_RC rc = RfcLanguageIsoToSap(uclang_iso, uclang_sap, &errorInfo)
    free(uclang_iso)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    return wrapString(uclang_sap, 1)


def language_sap_to_iso(lang_sap):
    """Language code conversion of SAP code to ISO code.

    :param lang_sap: Language SAP code
    :type lang_sap: string

    :return: ISO language code

    :raises: :exc:`~pyrfc.RFCError` or a subclass
                if SAP to ISO code conversion fails.
    """
    cdef SAP_UC *uclang_sap = fillString(lang_sap)
    cdef SAP_UC uclang_iso[16]
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_RC rc = RfcLanguageSapToIso(uclang_sap, uclang_iso, &errorInfo)
    free(uclang_sap)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    return wrapString(uclang_iso, 2)


def set_cryptolib_path(path_name):
    """Sets the absolute path to the sapcrypto library to enable TLS encryption via Websocket Rfc.

    The parameter path_name needs also to contain the name of the library.
    This function has the same effect as the sapnwrfc.ini parameter TLS_SAPCRYPTOLIB.
    This API cannot reset a new path to the library during runtime. Once set, the path is definitive.

    :param path_name: Absolute path to crypto library
    :type path_name: string

    :return: nothing, raises an error
    """
    if type(path_name) is not str:
        raise TypeError('sapnwrfc.ini path is not a string:', path_name)
    cdef RFC_ERROR_INFO errorInfo
    cdef SAP_UC pathName [512]
    if not isfile(path_name):
        raise TypeError('Crypto library not found:', path_name)
    pathName = fillString(path_name)
    cdef RFC_RC rc = RfcLoadCryptoLibrary(pathName, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)


def set_locale_radix(value=None):
    """Sets the locale radix for decimal conversions.

    :param value: Locale radix like ``.`` or ``,``
    :type path_name: string

    :return: New radix set
    """
    global _LOCALE_RADIX
    if value is None:
        value = localeconv()['decimal_point']
    _LOCALE_RADIX = value
    return _LOCALE_RADIX


cdef _cancel_connection(client_connection):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    if client_connection.handle is not None:
        rc = RfcCancel(<RFC_CONNECTION_HANDLE><uintptr_t>client_connection.handle, &errorInfo)
        if rc != RFC_OK or errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)


def cancel_connection(client_connection):
    """Immediately cancels the RFC call which is currently being called over the given RFC connection
    and closes the connection. Can be used only on an RFC client connection.

    RFC call cancellation with timeout can be done automatically, without using this method explicitely.
    The ``timeout`` option can be at connection level, when creating connection instance, or at RFC call level, as
    RFC ``Connection.call()`` option. Either way, the connection will be cancelled if RFC call takes longer than ``timeout`` seconds.

    :param client_connection: RFC client connection instance to be cancelled
    :type client_connection: Connection

    :raises: :exc:`~pyrfc.RFCError` or a subclass
                thereof if the connection cannot be cancelled cleanly.
    """
    Thread(target=_cancel_connection, args=(client_connection,)).start()


################################################################################
# CONNECTION PARAMETERS
################################################################################


cdef class ConnectionParameters:
    """Connection parameters instance in SAP unicode format

    :param args: Connection parameters like ASHOST="ABC" etc
    :type args: positional

    :returns: Nothing
    """
    cdef unsigned _params_count
    cdef RFC_CONNECTION_PARAMETER *_params

    def __cinit__(self, **params):
        self._params_count = <unsigned> len(params)
        if self._params_count < 1:
            raise RFCError("Connection parameters missing")
        self._params = <RFC_CONNECTION_PARAMETER*> malloc(self._params_count * sizeof(RFC_CONNECTION_PARAMETER))
        cdef int i = 0
        for name, value in params.iteritems():
            self._params[i].name = fillString(name)
            self._params[i].value = fillString(value)
            i += 1

    def __del__(self):
        self._free()

    def _free(self):
        if self._params_count > 0:
            for i in range(self._params_count):
                free(<SAP_UC*>self._params[i].name)
                free(<SAP_UC*> self._params[i].value)
            free(self._params)
            self._params_count = 0

################################################################################
# Type Description
################################################################################


class TypeDescription(object):
    """ A type description

    This class wraps the RFC_TYPE_DESC_HANDLE as e.g. contained in
    a parameter description of a function description.

    :param name: Name of the type.
    :param nuc_length: Length of the type in non unicode systems.
    :param uc_length: Length of the type in unicode systems.

    *Attributes and methods*

    **name**
        The name of the function.

    **nuc_length**
        The length in bytes if chars are non unicode.

    **uc_length**
        The length in bytes if chars are unicode.

    **fields**
        The fields as a list of dicts.

    """
    def __init__(self, name, nuc_length, uc_length):
        self.fields = []
        if len(name)<1 or len(name)>30:
            raise TypeError(f"field 'name' (string) '{name}' should be from 1-30 chars.")
        for int_field in [nuc_length, uc_length]:
            if type(int_field) not in [int, long]:
                raise TypeError(f"field '{name}' length '{int_field}' must be of type integer")
        self.name = name
        self.nuc_length = nuc_length
        self.uc_length = uc_length

    def add_field(self, name, field_type, nuc_length, uc_length, nuc_offset,
                  uc_offset, decimals=0, type_description=None):
        """ Adds a field to the type description.

        :param name: Field name
        :type name: string (30)
        :param field_type: RfcFieldType enum name
        :type field_type: string
        :param nuc_length: NUC length
        :type nuc_length: int
        :param uc_length: UC length
        :type uc_length: int
        :param nuc_offset: NUC offset.
        :type nuc_offset: int
        :param uc_offset: UC offset.
        :type uc_offset: int
        :param decimals: Decimals (default=0)
        :type decimals: int
        :param type_description: An object of class TypeDescription or None (default=None)
        :type type_description: object of class TypeDescription
        """
        if len(name)<1:
            return None
        if len(name)>30:
            raise TypeError(f"field 'name' (string) '{name}' should be from 1-30 chars.")
        if field_type not in enum_names(RfcFieldType):
            raise TypeError(f"'field_type' (string) '{field_type}' must be in {enum_names(RfcFieldType)}")
        for int_field in [nuc_length, nuc_offset, uc_length, uc_offset]:
            if not isinstance(int_field, (int, long)):
                raise TypeError(f"field '{name}' length '{int_field}' must be of type integer")
        self.fields.append({
            'name': name,
            'field_type': field_type,
            'nuc_length': nuc_length,
            'nuc_offset': nuc_offset,
            'uc_length': uc_length,
            'uc_offset': uc_offset,
            'decimals': decimals,
            'type_description': type_description
        })

    def __repr__(self):
        return f"<TypeDescription '{self.name}' with {len(self.fields)} " \
            f"fields (n/uclength={self.nuc_length}/{self.uc_length})>"

################################################################################
# Function Description
################################################################################


class FunctionDescription(object):
    """ A function description

    This class wraps the RFC_FUNCTION_DESC_HANDLE as e.g. returned by
    RfcGetFunctionDesc() and used for server functionality.

    .. WARNING::

        Actually, the function description does not support exceptions
        (cf. RfcAddException() etc.)

    :param name: Name of the function.


    *Attributes and methods*

    **name**
        The name of the function.

    **parameters**
        The parameters as a list of dicts.

    """
    def __init__(self, name):
        self.name = name
        self.parameters = []

    def add_parameter(self, name, parameter_type, direction, nuc_length,
                      uc_length, decimals=0, default_value="", parameter_text="",
                      optional=False, type_description=None):
        """ Adds a parameter to the function description.

        :param name: Parameter name
        :type name: string (30)
        :param parameter_type: RfcFieldType enum name
        :type parameter_type: string
        :param direction: RfcParameterDirection enum name
        :type direction: string
        :param nuc_length: NUC length
        :type nuc_length: int
        :param uc_length: UC length
        :type uc_length: int
        :param decimals: Decimals (default=0)
        :type decimals: int
        :param default_value: Default value (default="")
        :type default_value: string (30)
        :param parameter_text: Parameter text (default="")
        :type parameter_text: string (79)
        :param optional: Is the parameter optional (default=False)
        :type optional: bool
        :param type_description: An object of class TypeDescription or None (default=None)
        :type type_description: object of class TypeDescription
        """
        if len(name)<1 or len(name)>30:
            raise TypeError(f"field 'name' (string) {name} should be from 1-30 chars.")
        if parameter_type not in enum_names(RfcFieldType):
            raise TypeError(f"'parameter_type' (string) '{parameter_type}' must be in {enum_names(RfcFieldType)}")
        if direction not in enum_names(RfcParameterDirection):
            raise TypeError(f"'direction' (string) '{direction}' must be in '{enum_names(RfcParameterDirection)}'")
        if len(default_value)>30:
            raise TypeError(f"'default_value' (string) '{default_value}' must not exceed 30 chars.")
        if len(parameter_text)>79:
            raise TypeError("'parameter_text' (string) '{parameter_text}' must not exceed 79 chars.")
        self.parameters.append({
            'name': name,
            'parameter_type': parameter_type,
            'direction': direction,
            'nuc_length': nuc_length,
            'uc_length': uc_length,
            'decimals': decimals,
            'default_value': default_value,
            'parameter_text': parameter_text,
            'optional': optional,
            'type_description': type_description
        })

    def __repr__(self):
        return f"<FunctionDescription '{self.name}' with {len(self.parameters)} params>"

# NOTES ON ERROR HANDLING
# If an error occurs within a connection object, the error may - depending
# on the error code - affect the status of the connection object.
# Therefore, the _error() method is called instead of raising the error
# directly.
# However, updating the connection status is not possible in the
# fill/wrap-functions, as there is no connection object available. But this
# should not be a problem as we do not expect connection-affecting errors if
# no connection is present.
#
# NOTES ON NOGIL:
# NW RFC Lib function call may take a while (e.g. invoking RFC),
# other threads may be blocked meanwhile. To avoid this, some statements
# calling NW RFC Lib functions are executed within a "with nogil:" block,
# thereby releasing the Python global interpreter lock (GIL).

################################################################################
# CLIENT CONNECTION
################################################################################


cdef class Connection:
    """ A connection to an SAP backend system

    Instantiating an :class:`pyrfc.Connection` object will
    automatically attempt to open a connection the SAP backend.

    :param config: Configuration of the client connection, valid for all RFC calls of given connection. Allowed keys are:

           * ``dtime``
             ABAP DATE and TIME strings are returned as Python datetime date and time objects,
             instead of ABAP date and time strings (default is False)

           * ``rstrip``
             right strips strings returned from RFC call (default is True)

           * ``return_import_params``
             importing parameters are returned by the RFC call (default is False)

           * ``timeout``
             Cancel connection if ongoing RFC calls takes longer than ``timeout`` seconds.
             Timeout can be also set as option for particular RFC call, overriding timeout set at connection level.

             Examples: https://github.com/SAP/PyRFC/tree/main/examples/timeout


    :type config: dict or None (default)

    :param params: SAP connection parameters. The parameters consist of
           ``client``, ``user``, ``passwd``, ``lang``, ``trace``
           and additionally one of

           * Direct application server logon: ``ashost``, ``sysnr``.
           * Logon with load balancing: ``mshost``, ``msserv``, ``sysid``,
             ``group``.
             ``msserv`` is needed only, if the service of the message server
             is not defined as sapms<SYSID> in /etc/services.
           * When logging on with SNC, ``user`` and ``passwd`` are to be replaced by
             ``snc_qop``, ``snc_myname``, ``snc_partnername``, and optionally
             ``snc_lib``.
             (If ``snc_lib`` is not specified, the RFC library uses the "global" GSS library
             defined via environment variable SNC_LIB.)
    :type params: Keyword parameters

    :raises: :exc:`~pyrfc.RFCError` or a subclass
             thereof if the connection attempt fails.
    """
    cdef unsigned __bconfig
    cdef public dict __config
    cdef bint active_transaction
    cdef bint active_unit
    cdef RFC_CONNECTION_HANDLE _handle
    cdef RFC_TRANSACTION_HANDLE _tHandle
    cdef RFC_UNIT_HANDLE _uHandle
    cdef ConnectionParameters _connection

    @property
    def version(self):
        """Get SAP NW RFC SDK and PyRFC binding versions
        :returns: SAP NW RFC SDK major, minor, patch level and PyRFC binding version
        """
        cdef unsigned major = 0
        cdef unsigned minor = 0
        cdef unsigned patchlevel = 0
        RfcGetVersion(&major, &minor, &patchlevel)
        return {'major': major, 'minor': minor, 'patchLevel': patchlevel, 'platform': platform}

    @property
    def options(self):
        """Client connection configuration

        :getter: Client connection options
        :setter: Set when new connection object created
        :type: dict
        """
        return self.__config

    @property
    def handle(self):
        """Get client connection handle

        :getter: Client connection handle
        :type: uintptr_t
        """
        return <uintptr_t>self._handle if self._handle is not NULL else None

    @property
    def alive(self):
        """Conection alive property

        :getter: True when alive
        :type: boolean
        """
        return self._handle != NULL

    def __init__(self, config=None, **params):
        # check and set connection configuration
        config = config or {}
        for k in config:
            if k not in['dtime', 'return_import_params', 'rstrip', 'timeout']:
                raise RFCError(f"Connection configuration option '{k}' is not supported")
        self.__config = {}
        self.__config['dtime'] = config.get('dtime', False)
        self.__config['return_import_params'] = config.get('return_import_params', False)
        self.__config['rstrip'] = config.get('rstrip', True)
        self.__config['timeout'] = config.get('timeout', None)

        # set internal configuration
        self.__bconfig = 0
        if self.__config['dtime']:
            self.__bconfig |= _MASK_DTIME
        if self.__config['return_import_params']:
            self.__bconfig |= _MASK_RETURN_IMPORT_PARAMS
        if self.__config['rstrip']:
            self.__bconfig |= _MASK_RSTRIP

        self._connection = ConnectionParameters(**params)
        self._handle = NULL
        self.active_transaction = False
        self.active_unit = False
        self._open()

    def free(self):
        """ Explicitly free connection parameters and close the connection.

        Note that this is usually required because the object destruction
        can be delayed by the garbage collection and problems may occur
        when too many connections are opened.
        """
        self.__del__()

    def __del__(self):
        self._close()
        self._connection._free()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Although the _close() method is also called in the destructor, the
        # explicit call assures the immediate closing to the connection.
        self._close()

    def open(self):
        """ Open client the connection

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection cannot be opened.
        """
        self._open()

    def reopen(self):
        """ Re-open client the connection

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection cannot be re-opened.
        """
        self._reopen()

    def close(self):
        """ Close the connection

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection cannot be closed cleanly.
        """
        self._close()

    def cancel(self):
        """ Cancels the ongoing RFC call using `~pyrfc.cancel_connection()` function

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection cannot be cancelled cleanly.
        """
        cancel_connection(self)

    def __bool__(self):
        return self.alive

    cdef _reopen(self):
        self._close()
        self._open()

    cdef _open(self):
        cdef RFC_ERROR_INFO errorInfo
        with nogil:
            self._handle = RfcOpenConnection(self._connection._params, self._connection._params_count, &errorInfo)
        if not self._handle:
            self._error(&errorInfo)

    def _close(self):
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        if self._handle != NULL:
            rc = RfcCloseConnection(self._handle, &errorInfo)
            self._handle = NULL
            if rc != RFC_OK:
                self._error(&errorInfo)

    cdef _error(self, RFC_ERROR_INFO* errorInfo):
        """
        Error treatment of a connection.

        :param errorInfo: the errorInfo data given in a RFC that returned an RC > 0.
        :return: nothing, raises an error
        """
        # Set alive=false if the error is in a certain group
        # Before, the alive=false setting depended on the error code. However, the group seems more robust here.
        # errorInfo.code in
        #   RFC_COMMUNICATION_FAILURE, RFC_ABAP_MESSAGE, RFC_ABAP_RUNTIME_FAILURE,
        #   RFC_INVALID_HANDLE, RFC_NOT_FOUND, RFC_INVALID_PARAMETER:
        # if errorInfo.group in (ABAP_RUNTIME_FAILURE, LOGON_FAILURE, COMMUNICATION_FAILURE, EXTERNAL_RUNTIME_FAILURE):
        #    self.alive = False

        raise wrapError(errorInfo)

    def ping(self):
        """ Send a RFC Ping through the current connection

        Returns nothing.

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the RFC Ping fails.
        """
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        rc = RfcPing(self._handle, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)

    def reset_server_context(self):
        """ Resets the SAP server context ("user context / ABAP session context")
        associated with the given client connection, but does not close the connection

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof in case resetting the server context fails.
                 (Better close the connection in that case.).
                 :exc:`sapnwrf2.CommunicationError` if no conversion
                 was found for the
        """

        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        rc = RfcResetServerContext(self._handle, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)

    def get_connection_attributes(self):
        """ Get connection details

        :returns: Mapping of connection information keys:

            * active_unit: True if there is a filled and submitted unit w/o being confirmed or destroyed.
            * dest: RFC destination
            * host: Own host name
            * partnerHost: Partner host name
            * sysNumber: R/3 system number
            * sysId: R/3 system ID
            * client: Client ("Mandant")
            * user: User
            * language: Language
            * trace: Trace level (0-3)
            * isoLanguage: 2-byte ISO-Language
            * codepage: Own code page
            * partnerCodepage: Partner code page
            * rfcRole: C/S: RFC Client / RFC Server
            * type: 2/3/E/R: R/2,R/3,Ext,Reg.Ext
            * partnerType: 2/3/E/R: R/2,R/3,Ext,Reg.Ext
            * rel: My system release
            * partnerRe: Partner system release
            * kernelRel: Partner kernel release
            * cpicConvId: CPI-C Conversation ID
            * progName: Name calling APAB program (report, module pool)
            * partnerBytesPerChar: Bytes per char in backend codepage.
            * partnerSystemCodepage: Partner system code page
            * reserved: Reserved for later use

            Note: all values, except ``active_unit`` are right stripped string values.

        :raises: :exc:`~pyrfc.RFCError` or a subclass thereof if the RFC call fails.
        """
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_ATTRIBUTES attributes

        result = {}

        if self.is_valid():
            rc = RfcGetConnectionAttributes(self._handle, &attributes, &errorInfo)
            if rc != RFC_OK:
                self._error(&errorInfo)

            result = wrapConnectionAttributes(attributes)
            result.update({
                'active_unit': self.active_unit or self.active_transaction
            })
        return result

    def is_valid(self):
        """Checks an RFC connection. Can be used to check whether a client/server connection
        has already been closed, or whether the NW RFC library still "considers" the connection
        to be open.

        .. note::
           This does not guarantee that the connection is indeed still alive:
           A firewall may silently have closed the connection without notifying
           the endpoints. If you want to find out, whether the connection is still alive,
           you'll have to use the more expensive RfcPing().

        :returns: boolean
        """
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_INT isValid

        rc = RfcIsConnectionHandleValid(self._handle, &isValid, &errorInfo)

        if rc != RFC_OK or errorInfo.code != RFC_OK:
            return False
        return True

    # def c_handle_test(self, p_handle):
    #     print("p:handle", p_handle)
    #     cdef RFC_CONNECTION_HANDLE c_handle = <RFC_CONNECTION_HANDLE><uintptr_t>p_handle
    #     p_handle2 = <uintptr_t>c_handle
    #     print("p:handle <uintptr_t>", p_handle2)
    #     print("c:handle", "ok" if c_handle - self._handle == 0 else "error")

    def get_function_description(self, func_name):
        """ Returns a function description of a function module.

        :param func_name: Name of the function module whose description
              will be returned.
        :type func_name: string

        :return: A :class:`FunctionDescription` object.
        """
        cdef RFC_ERROR_INFO errorInfo
        funcName = fillString(func_name.upper())
        cdef RFC_FUNCTION_DESC_HANDLE funcDesc = RfcGetFunctionDesc(self._handle, funcName, &errorInfo)
        free(funcName)
        if not funcDesc:
            self._error(&errorInfo)
        return wrapFunctionDescription(funcDesc)

    def call(self, func_name, options=None, **params):
        """ Invokes a remote-enabled function module via RFC.

        :param func_name: Name of the function module that will be invoked.
        :type func_name: string

        :param options: Call options for single remote ABAP function call. Allowed keys:

            - ``not_requested`` Allows to deactivate certain parameters in the function module interface.
              This is particularly useful for BAPIs which have many large tables, the Python client is not interested in.
              Deactivate those, to reduce network traffic and memory consumption in your application considerably.

              This functionality can be used for input and output parameters. If the parameter is an input, no data for
              that parameter will be sent to the backend. If it's an output, the backend will be informed not to return
              data for that parameter.

            - ``timeout`` Cancel RFC connection if ongoing RFC call not completed within ``timeout`` seconds.
              Timeout can be also set as client connection configuration option, in which case is valid for all RFC calls.

              Examples: https://github.com/SAP/PyRFC/tree/main/examples/timeout

        :type options: dictionary

        :param params: Parameter of the function module. All non optional
                IMPORT, CHANGING, and TABLE parameters must be provided.
        :type params: keyword arguments

        :return: Dictionary with all EXPORT, CHANGING, and TABLE parameters.
                 The IMPORT parameters are also given, if :attr:`Connection.config.return_import_params`
                 is set to ``True``.

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the RFC call fails.
        """
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_ERROR_INFO openErrorInfo
        cdef SAP_UC *cName
        if type(func_name) is not str:
            raise RFCError("Remote function module name must be unicode string, received:", func_name, type(func_name))
        cdef SAP_UC *funcName = fillString(func_name)
        if self._handle == NULL:
            raise RFCError(f"Remote function module '{func_name}' invocation rejected because the connection is closed")
        cdef RFC_FUNCTION_DESC_HANDLE funcDesc = RfcGetFunctionDesc(self._handle, funcName, &errorInfo)
        free(funcName)
        if not funcDesc:
            self._error(&errorInfo)
        cdef RFC_FUNCTION_HANDLE funcCont = RfcCreateFunction(funcDesc, &errorInfo)
        if not funcCont:
            self._error(&errorInfo)
        cdef int isActive = 0
        options = options or {}
        try:  # now we have a function module
            if 'not_requested' in options:
                skip_parameters = options['not_requested']
                if type(skip_parameters) is not list:
                    skip_parameters = [skip_parameters]
                for name in skip_parameters:
                    cName = fillString(name)
                    rc = RfcSetParameterActive(funcCont, cName, isActive, &errorInfo)
                    free(cName)
                    if rc != RFC_OK:
                        self._error(&errorInfo)
            # set connection timeout, starts before writing input parameters to container
            cancel_timer = None
            timeout = options.get('timeout', self.__config['timeout'])
            if timeout is not None:
                cancel_timer = Timer(timeout, cancel_connection, (self,))
                cancel_timer.start()
            for name, value in params.iteritems():
                fillFunctionParameter(funcDesc, funcCont, name, value)
            # save old handle for troubleshooting
            with nogil:
                rc = RfcInvoke(self._handle, funcCont, &errorInfo)
            if cancel_timer is not None:
                cancel_timer.cancel()
            # print("invoke:", errorInfo.group, rc, self.handle, self.is_valid())
            if rc != RFC_OK:
                if errorInfo.code in (
                        RFC_COMMUNICATION_FAILURE,
                        RFC_ABAP_RUNTIME_FAILURE,
                        RFC_ABAP_MESSAGE,
                        RFC_EXTERNAL_FAILURE
                    ) or errorInfo.group in (
                        ABAP_RUNTIME_FAILURE,
                        LOGON_FAILURE,
                        COMMUNICATION_FAILURE,
                        EXTERNAL_RUNTIME_FAILURE):
                    # Connection closed, re-open
                    closed_handle = self.handle
                    self._handle = RfcOpenConnection(self._connection._params, self._connection._params_count, &openErrorInfo)
                    if openErrorInfo.code != RFC_OK:
                        self._handle = NULL
                        # Communication error returned as error
                        errorInfo = openErrorInfo
                    elif errorInfo.code == RFC_CANCELED:
                        errorInfo.message = fillString(f"Connection was canceled: {closed_handle}. New handle: {self.handle}")
                self._error(&errorInfo)
            if self.__bconfig & _MASK_RETURN_IMPORT_PARAMS:
                return wrapResult(funcDesc, funcCont, <RFC_DIRECTION> 0, self.__bconfig)
            else:
                return wrapResult(funcDesc, funcCont, RFC_IMPORT, self.__bconfig)
        finally:
            RfcDestroyFunction(funcCont, NULL)

    ##########################################################################
    #  HELPER METHODS

    def type_desc_get(self, type_name):
        """Removes the Type Description from SAP NW RFC Lib cache

        :param type_name: system id (connection parameters sysid)
        :type type_name: string

        :returns: error code
        """
        cdef RFC_ERROR_INFO errorInfo
        typeName = fillString(type_name.upper())
        cdef RFC_TYPE_DESC_HANDLE typeDesc = RfcGetTypeDesc(self._handle, typeName, &errorInfo)
        free(typeName)
        if typeDesc == NULL:
            self._error(&errorInfo)
        return wrapTypeDescription(typeDesc)

    def type_desc_remove(self, sysid, type_name):
        """Removes the Type Description from SAP NW RFC Lib cache

        :param sysid: system id (connection parameters sysid)
        :type sysid: string

        :param type_name: Name of the type to be removed
        :type func_name: string

        :returns: error code
        """
        cdef RFC_ERROR_INFO errorInfo
        sysId = fillString(sysid)
        typeName = fillString(type_name)
        cdef RFC_RC rc = RfcRemoveTypeDesc(sysId, typeName, &errorInfo)
        free(sysId)
        free(typeName)
        if rc != RFC_OK:
            self._error(&errorInfo)
        return rc

    def func_desc_remove(self, sysid, func_name):
        """Removes the Function Description from SAP NW RFC Lib cache

        :param sysid: system id (connection parameters sysid)
        :type sysid: string

        :param func_name: Name of the function module to be removed
        :type func_name: string

        :returns: error code
        """
        cdef RFC_ERROR_INFO errorInfo
        sysId = fillString(sysid)
        funcName = fillString(func_name)
        cdef RFC_RC rc = RfcRemoveFunctionDesc(sysId, funcName, &errorInfo)
        free(sysId)
        free(funcName)
        if rc != RFC_OK:
            self._error(&errorInfo)
        return rc

    ##########################################################################
    #  TRANSACTIONAL / QUEUED RFC

    def _get_transaction_id(self):
        """ Returns a unique 24 char transaction ID (GUID)."""
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_TID tid

        if not self.alive:
            self._open()
        rc = RfcGetTransactionID(self._handle, tid, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)
        return wrapString(tid, RFC_TID_LN)

    def _create_and_submit_transaction(self, transaction_id, calls, queue_name=None):
        # Note: no persistence action is taken of maintaining the arguments (cf. Schmidt, Li (2009c), p. 5ff)
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef SAP_UC* queueName
        cdef RFC_FUNCTION_DESC_HANDLE funcDesc
        cdef RFC_FUNCTION_HANDLE funcCont

        if not self.alive:
            self._open()

        tid = fillString(transaction_id)
        queueName = NULL
        if queue_name:
            queueName = fillString(queue_name)
        self._tHandle = RfcCreateTransaction(self._handle, tid, queueName, &errorInfo)

        if queue_name:
            free(queueName)
        free(tid)
        if self._tHandle == NULL:
            self._error(&errorInfo)
        self.active_transaction = True

        try:
            for func_name, params in calls:
                funcName = fillString(func_name)
                funcDesc = RfcGetFunctionDesc(self._handle, funcName, &errorInfo)
                free(funcName)
                if not funcDesc:
                    self._error(&errorInfo)
                funcCont = RfcCreateFunction(funcDesc, &errorInfo)
                if not funcCont:
                    self._error(&errorInfo)
                try:
                    for name, value in params.iteritems():
                        fillFunctionParameter(funcDesc, funcCont, name, value)
                    # Add RFC call to transaction
                    rc = RfcInvokeInTransaction(self._tHandle, funcCont, &errorInfo)
                    if rc != RFC_OK:
                        self._error(&errorInfo)
                finally:
                    RfcDestroyFunction(funcCont, NULL)
            # execute
            with nogil:
                rc = RfcSubmitTransaction(self._tHandle, &errorInfo)
            if rc != RFC_OK:
                self._error(&errorInfo)

        except RFCError as e:
            # clean up actions
            RfcDestroyTransaction(self._tHandle, NULL)
            raise

    def _destroy_transaction(self):
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        if not self.active_transaction:
            raise RFCError("No transaction handle for this connection available.")
        if not self.alive:
            self._open()
        rc = RfcDestroyTransaction(self._tHandle, &errorInfo)
        self.active_transaction = False
        if rc != RFC_OK:
            self._error(&errorInfo)

    def _confirm_transaction(self):
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        if not self.active_transaction:
            raise RFCError("No transaction handle for this connection available.")
        if not self.alive:
            self._open()
        rc = RfcConfirmTransaction(self._tHandle, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)
        rc = RfcDestroyTransaction(self._tHandle, &errorInfo)
        self.active_transaction = False
        if rc != RFC_OK:
            self._error(&errorInfo)

    ##########################################################################
    #  BACKGROUND RFC

    def _get_unit_id(self):
        """Returns a unique 32 char bgRFC unit ID (GUID)."""
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_UNITID uid

        if not self.alive:
            self._open()
        rc = RfcGetUnitID(self._handle, uid, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)
        return wrapString(uid, RFC_UNITID_LN)

    def _create_and_submit_unit(self, unit_id, calls, queue_names=None, attributes=None):
        # Note: no persistence action is taken of maintaining the arguments (cf. Schmidt, Li (2009c), p. 5ff)
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef int queueNameCount
        # cdef const_SAP_UC_ptr* queueNames
        cdef SAP_UC** queueNames
        cdef RFC_UNIT_ATTRIBUTES unitAttr
        cdef RFC_UNIT_IDENTIFIER uIdentifier
        cdef RFC_FUNCTION_DESC_HANDLE funcDesc
        cdef RFC_FUNCTION_HANDLE funcCont
        cdef SAP_UC* sapuc

        if not self.alive:
            self._open()

        # uid
        uid = fillString(unit_id)
        # queue
        queue_names = queue_names or []
        if len(queue_names) == 0:
            queueNameCount = 0
            queueNames = NULL
        else:
            queueNameCount = int(len(queue_names))
            queueNames = <SAP_UC**> mallocU(queueNameCount * sizeof(SAP_UC*))
            for i, queue_name in enumerate(queue_names):
                queueNames[i] = fillString(queue_name)
        # attributes
        # set default values
        memsetR(&unitAttr, 0, sizeof(RFC_UNIT_ATTRIBUTES))
        memsetR(&uIdentifier, 0, sizeof(RFC_UNIT_IDENTIFIER))
        # unitAttr.kernelTrace = 0       (short) If != 0, the backend will write kernel traces, while executing this unit.
        # unitAttr.satTrace = 0          (short) If != 0, the backend will keep a "history" for this unit.
        # unitAttr.unitHistory = 0       (short) Used only for type Q: If != 0, the unit will be written to the queue, but not processed.
        #                                The unit can then be started manually in the ABAP debugger.
        # unitAttr.lock = 0              (short) Used only for type Q: If != 0, the unit will be written to the queue, but not processed.
        #                                The unit can then be started manually in the ABAP debugger.
        # unitAttr.noCommitCheck = 0	 (short) Per default the backend will check during execution of a unit,
        #                                whether one of the unit's function modules triggers an explicit or implicit COMMIT WORK.
        #                                In this case the unit is aborted with an error, because the transactional
        #                                integrity of this unit cannot be guaranteed.
        #                                By setting "noCommitCheck" to true (!=0), this behavior can be suppressed,
        #                                meaning the unit will be executed anyway,
        #                                even if one of it's function modules "misbehaves" and triggers a COMMIT WORK.
        # unitAttr.user[0] = '\0'        (SAP_UC[12+1]) Sender User (optional). Default is current operating system User.
        # unitAttr.client[0] = '\0'      (SAP_UC[3+1]) Sender Client ("Mandant") (optional). Default is "000".
        # unitAttr.tCode[0] = '\0'       (SAP_UC[20+1]) Sender Transaction Code (optional). Default is "".
        # unitAttr.program[0] = '\0'     (SAP_UC[40+1]) Sender Program (optional). Default is current executable name.
        # unitAttr.hostname[0] = '\0'    (SAP_UC hostname[40+1];
        #                                Sender hostname. Used only when the external program is server.
        #                                In the client case the nwrfclib fills this automatically.
        # unitAttr.sendingDate[0] = '\0' (RFC_DATE sendingDate;
        #                                Sending date in UTC (GMT-0). Used only when the external program is server.
        #                                In the client case the nwrfclib fills this automatically.
        # unitAttr.sendingTime[0] = '\0' (RFC_TIME sendingTime;
        #                                Sending time in UTC (GMT-0). Used only when the external program is server.
        #                                In the client case the nwrfclib fills this automatically.
        if attributes is not None:
            if 'kernel_trace' in attributes:
                unitAttr.kernelTrace = attributes['kernel_trace']
            if 'sat_trace' in attributes:
                unitAttr.satTrace = attributes['sat_trace']
            if 'unit_history' in attributes:
                unitAttr.unitHistory = attributes['unit_history']
            if 'lock' in attributes:
                unitAttr.lock = attributes['lock']
            if 'no_commit_check' in attributes:
                unitAttr.noCommitCheck = attributes['no_commit_check']
            if 'user' in attributes and attributes['user'] is not None:
                # (SAP_UC[12+1]) Sender User (optional). Default is current operating system User.
                sapuc = fillString(attributes['user'][0:12])
                strncpyU(unitAttr.user, sapuc, len(attributes['user'][0:12]) + 1)
                free(sapuc)
            if 'client' in attributes:
                # (SAP_UC[3+1]) Sender Client ("Mandant") (optional). Default is "000".
                sapuc = fillString(attributes['client'][0:3])
                strncpyU(unitAttr.client, sapuc, len(attributes['client'][0:3]) + 1)
                free(sapuc)
            if 't_code' in attributes:
                # (SAP_UC[20+1]) Sender Transaction Code (optional). Default is "".
                sapuc = fillString(attributes['t_code'][0:20])
                strncpyU(unitAttr.tCode, sapuc, len(attributes['t_code'][0:20]) + 1)
                free(sapuc)
            if 'program' in attributes and attributes['program'] is not None:
                # (SAP_UC[40+1]) Sender Program (optional). Default is current executable name.
                sapuc = fillString(attributes['program'][0:40])
                strncpyU(unitAttr.program, sapuc, len(attributes['program'][0:40]) + 1)
                free(sapuc)

        self._uHandle = RfcCreateUnit(self._handle, uid, <const_SAP_UC_ptr*> queueNames, queueNameCount, &unitAttr, &uIdentifier, &errorInfo)

        # queue (deallocate)
        if len(queue_names) > 0:
            for i, queue_name in enumerate(queue_names):
                free(queueNames[i])
            free(queueNames)
        # uid (deallocate)
        free(uid)

        if self._uHandle == NULL:
            self._error(&errorInfo)
        self.active_unit = True

        try:
            for func_name, params in calls:
                funcName = fillString(func_name)
                funcDesc = RfcGetFunctionDesc(self._handle, funcName, &errorInfo)
                free(funcName)
                if not funcDesc:
                    self._error(&errorInfo)
                funcCont = RfcCreateFunction(funcDesc, &errorInfo)
                if not funcCont:
                    self._error(&errorInfo)
                try:
                    for name, value in params.iteritems():
                        fillFunctionParameter(funcDesc, funcCont, name, value)
                    # Add RFC call to unit
                    rc = RfcInvokeInUnit(self._uHandle, funcCont, &errorInfo)
                    if rc != RFC_OK:
                        self._error(&errorInfo)
                finally:
                    RfcDestroyFunction(funcCont, NULL)
            # execute
            print (" Invocation finished. submitting unit.")
            with nogil:
                rc = RfcSubmitUnit(self._uHandle, &errorInfo)
            if rc != RFC_OK:
                self._error(&errorInfo)

        except RFCError as e:
            # clean up actions
            RfcDestroyUnit(self._uHandle, NULL)
            raise

        unit_identifier = wrapUnitIdentifier(uIdentifier)
        return unit_identifier["queued"]

    def _get_unit_state(self, unit):
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_UNIT_IDENTIFIER uIdentifier = fillUnitIdentifier(unit)
        cdef RFC_UNIT_STATE state

        if not self.active_unit:
            raise RFCError("No unit handle for this connection available.")
        if not self.alive:
            self._open()
        rc = RfcGetUnitState(self._handle, &uIdentifier, &state, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)
        if state not in enum_values(UnitState):
            raise RFCError(f"Unit {unit['id']} has invalid state '{state}'")
        return UnitState(state).name

    def _destroy_unit(self):
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        if not self.active_unit:
            raise RFCError("No unit handle for this connection available.")
        if not self.alive:
            self._open()
        rc = RfcDestroyUnit(self._uHandle, &errorInfo)
        self.active_unit = False
        if rc != RFC_OK:
            self._error(&errorInfo)

    def _confirm_unit(self, unit):
        cdef RFC_RC rc
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_UNIT_IDENTIFIER uIdentifier = fillUnitIdentifier(unit)

        if not self.active_unit:
            raise RFCError("No unit handle for this connection available.")
        if not self.alive:
            self._open()
        rc = RfcConfirmUnit(self._handle, &uIdentifier, &errorInfo)
        if rc != RFC_OK:
            self._error(&errorInfo)
        rc = RfcDestroyUnit(self._uHandle, &errorInfo)
        self.active_unit = False
        if rc != RFC_OK:
            self._error(&errorInfo)

    ##########################################################################
    # UNIT RFC

    # a "unit" for the client is a dictionary with up to three key-value pairs:
    # * background - boolean, set on initialize_unit() call
    # * id - string 24 or 32 chars, set on initialize_unit() call
    # * queued - boolean, set on fill_and_submit_unit() call

    def initialize_unit(self, background=True):
        """ Initializes a logical unit of work (LUW), shorthand: unit

        .. warning::

           The background protocol (bgRFC) is not working in the current version.
           Please use only tRFC/qRFC protocols.

        :param background: The bgRFC protocol will be used. If set to False,
               the t/qRFC protocol will be used. Note that the bgRFC protocol
               has extended functionality. Default: True
        :type background: boolean

        :returns: A dictionary describing the unit.
        """
        if background is True:     # use bgRFC
            id = self._get_unit_id()
        elif background is False:  # classic t/qRFC
            id = self._get_transaction_id()
        else:
            raise RFCError("Argument 'background' must be a boolean value.")
        return {'background': background, 'id': id, "queued": False}

    def fill_and_submit_unit(self, unit, calls, queue_names=None, attributes=None):
        """ Fills a unit with one or more RFC and submits it to the backend.

        Fills a unit for this connection, prepare the invocation
        of multiple RFC function modules in it, and submits the unit
        to the backend.

        Afterwards, the unit is still attached to the connection object,
        until confirm_unit() or destroy_unit() is called. Until one of these
        methods are called, no other unit could be filled and submitted.

        :param unit: a unit descriptor as returned by
               :meth:`~pyrfc.Connection.initialize_unit`.
        :param calls: a list of call descriptions. Each call description is a
               tuple that contains the function name as the first element and
               the function arguments in form of a dictionary as the second element.
        :param queue_names:
               If the unit uses the background protocol, various queue names can
               be given (leading to a asynchronous unit, type 'Q'). If parameter
               is an empty list or None, a synchronous unit (type 'T') is created.

               If the unit does not use the background protocol, the queue name
               may be a list with exactly one element, leading to a qRFC, or
               an empty list or None, leading to a tRFC.
        :type queue_names: list of strings or None (default)
        :param attributes: optional argument for attributes of the unit -- only valid if the background protocol
              is used. The attributes dict may contain the following keywords:

              =============== ============================= ======================= ==========================================================================================
              keyword         default                       type                    description
              =============== ============================= ======================= ==========================================================================================
              kernel_trace    0                             int                     If != 0, the backend will write kernel traces, while executing this unit.
              sat_trace       0                             int                     If != 0, the backend will write statistic records, while executing this unit.
              unit_history    0                             int                     If != 0, the backend will keep a "history" for this unit.
              lock            0                             int                     Used only for type Q: If != 0, the unit will be written to the queue, but not processed.
                                                                                    The unit can then be started manually in the ABAP debugger.
              no_commit_check 0                             int                     Per default the backend will check during execution of a unit, whether one of the
                                                                                    unit's function modules triggers an explicit or implicit COMMITWORK.
                                                                                    In this case the unit is aborted with an error, because the transactional integrity of
                                                                                    this unit cannot be guaranteed. By setting "no_commit_check" to true (!=0), this behavior
                                                                                    can be suppressed, meaning the unit will be executed anyway, even if one of it's
                                                                                    function modules "misbehaves" and triggers a COMMIT WORK.
              user            current operating system user String, len |nbsp| 12   Sender User (optional).
              client          "000"                         String, len |nbsp| 3    Sender Client ("Mandant") (optional).
              t_code          ""                            String, len |nbsp| 20   Sender Transaction Code (optional).
              program         current executable name       String, len |nbsp| 40   Sender Program (optional).
              =============== ============================= ======================= ==========================================================================================

        :type attributes: dict or None (default)
        :raises: :exc:`~pyrfc.RFCError` or a subclass thereof if an error
                 occurred. In this case, the unit is destroyed.
        """

        if type(unit) is not dict or 'id' not in unit or 'background' not in unit:
            raise TypeError("Parameter 'unit' not valid. Please use initialize_unit() to retrieve a valid unit.")
        if not isinstance(calls, Iterable):
            raise TypeError("Parameter 'calls' must be iterable.")
        if len(calls)==0:
            raise TypeError("Parameter 'calls' must contain at least on call description (func_name, params).")
        for func_name, params in calls:
            if type(func_name) is not str or type(params) is not dict:
                raise TypeError("Parameter 'calls' must contain valid call descriptions (func_name, params dict).")
        if self.active_unit:
            raise RFCError("There is an active unit for this connection. "
                           "Use destroy_unit() " +
                           "or confirm_unit().")
        bg = unit['background']
        unit_id = unit['id']

        if bg is True:
            if len(unit_id) != RFC_UNITID_LN:
                raise TypeError(f"Length of parameter 'unit['id']' must be {RFC_UNITID_LN} chars, found {len(unit_id)}.")
            unit['queued'] = self._create_and_submit_unit(unit_id, calls, queue_names, attributes)
        elif bg is False:
            if len(unit_id) != RFC_TID_LN:
                raise TypeError(f"Length of parameter 'unit['id']' must be {RFC_TID_LN} chars, found {len(unit_id)}.")
            if attributes is not None:
                raise RFCError("Argument 'attributes' not valid. (t/qRFC does not support attributes.)")
            if queue_names is None or type(queue_names) is list and len(queue_names) == 0:
                self._create_and_submit_transaction(unit_id, calls)
                unit['queued'] = False
            elif len(queue_names) == 1:
                queue_name = queue_names[0]
                self._create_and_submit_transaction(unit_id, calls, queue_name)
                unit['queued'] = True
            else:
                raise RFCError("Argument 'queue_names' not valid. (t/qRFC only support one queue name.)")
        else:
            raise RFCError("Argument 'unit' not valid. (Is unit['background'] boolean?)")
        return unit

    def get_unit_state(self, unit):
        """Retrieves the processing status of the given background unit.

        .. note::
           Only available for background units.

        :param unit: a unit descriptor as returned by
               :meth:`~pyrfc.Connection.initialize_unit`.
        :return: The state of the current bgRFC unit. Possible values are:
            RFC_UNIT_NOT_FOUND
            RFC_UNIT_IN_PROCESS
            RFC_UNIT_COMMITTED
            RFC_UNIT_ROLLED_BACK
            RFC_UNIT_CONFIRMED
        """
        bg = unit['background']
        if bg is True:
            return self._get_unit_state(unit)
        elif bg is False:
            raise RFCError("No state check possible of non-bgRFC units.")
        else:
            raise RFCError("Argument 'unit' not valid. (Is unit['background'] boolean?)")

    def destroy_unit(self, unit):
        """ Destroy the current unit.

        E.g. if the completed unit could not be recorded in the frontend.

        :param unit: a unit descriptor as returned by
               :meth:`~pyrfc.Connection.initialize_unit`.
        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection attempt fails.
        """
        bg = unit['background']
        if bg is True:
            self._destroy_unit()
        elif bg is False:
            self._destroy_transaction()
        else:
            raise RFCError("Argument 'unit' not valid. (Is unit['background'] boolean?)")

    def confirm_unit(self, unit):
        """ Confirm the current unit in the backend.

        This also destroys the unit.

        :param unit: a unit descriptor as returned by
               :meth:`~pyrfc.Connection.initialize_unit`.
        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection attempt fails.
        """
        bg = unit['background']
        if bg is True:
            self._confirm_unit(unit)
        elif bg is False:
            self._confirm_transaction()
        else:
            raise RFCError("Argument 'unit' not valid. (Is unit['background'] boolean?)")


################################################################################
# SERVER FUNCTIONALITY
################################################################################

# global information about served functions / callbacks
# "function_name": {"funcDescHandle": FunctionDescription object,
#                   "callback": Python function,
#                   "server": Server object)
server_functions = {}

# global information about served functions / callbacks
# "auth_check": Default authorization check function
# "server_log": Server logging flag, default False
server_context = {}


def default_auth_check(func_name=False, request_context = None):
    request_context = request_context or {}
    _server_log(f"authorization check for '{func_name}'", request_context['server_context'])
    return RFC_OK


def _server_log(origin, log_message):
    if server_context["server_log"]:
        print (f"[{datetime.utcnow()} UTC] {origin} '{log_message}'")


cdef class ServerConnection:
    cdef ConnectionParameters _connection
    cdef RFC_SERVER_HANDLE _handle
    cdef public bint debug
    cdef public bint rstrip

    def __init__(self, **params):
        self._connection = ConnectionParameters(**params)
        self._handle = NULL
        self._open()

    cdef _open(self):
        cdef RFC_ERROR_INFO errorInfo
        with nogil:
            self._handle = RfcCreateServer(self._connection._params, self._connection._params_count, &errorInfo)
        if errorInfo.code != RFC_OK:
            self._handle = NULL
            raise wrapError(&errorInfo)
        _server_log("Server connection", f"{<uintptr_t>self._handle}")

    cdef _close(self):
        if self._handle != NULL:
            _server_log("Server close", <uintptr_t>self._handle)
            with nogil:
                RfcShutdownServer(self._handle, 60, NULL)
                RfcDestroyServer(self._handle, NULL)
                self._handle = NULL

    def open(self):
        self._open()

    def close(self):
        self._close()

    def __bool__(self):
        return self.alive

    @property
    def handle(self):
        """Server connection handle

        :getter: Returns server connection handle
        :type: uitptr_t
        """
        return <uintptr_t>self._handle

    @property
    def alive(self):
        """Conection alive property

        :getter: Returns True when alive
        :type: boolean
        """
        return self._handle != NULL

    def __del__(self):
        self._close()
        self._connection._free()

cdef RFC_RC metadataLookup(
            const SAP_UC* functionName,
            RFC_ATTRIBUTES rfcAttributes,
            RFC_FUNCTION_DESC_HANDLE *funcDescHandle
        ) with gil:
    global server_functions
    function_name = wrapString(functionName)
    if function_name not in server_functions:
        _server_log("metadataLookup", f"No metadata found for function '{function_name}'.")
        return RFC_NOT_FOUND
    func_metadata = server_functions[function_name]
    # callback = func_metadata['callback']
    funcDescHandle[0] = <RFC_FUNCTION_DESC_HANDLE><uintptr_t>func_metadata['func_desc_handle']
    _server_log("metadataLookup", f"Function '{function_name}' handle {<uintptr_t>funcDescHandle[0]}.")
    return RFC_OK

cdef get_server_context(RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO* serverErrorInfo):
    cdef RFC_SERVER_CONTEXT context
    cdef RFC_RC rc = RfcGetServerContext(rfcHandle, &context, serverErrorInfo)
    if rc != RFC_OK or serverErrorInfo.code != RFC_OK:
        return None

    server_context = {
        "call_type": UnitCallType(context.type),
        "is_stateful": context.isStateful != 0
    }
    if context.type != RFC_SYNCHRONOUS:
        server_context["unit_identifier"] = wrapUnitIdentifier(context.unitIdentifier[0])
    if context.type == RFC_BACKGROUND_UNIT:
        server_context ["unit_attributes"] = wrapUnitAttributes(context.unitAttributes)

    return server_context

cdef RFC_RC genericHandler(RFC_CONNECTION_HANDLE rfcHandle, RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO* serverErrorInfo) with gil:
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_ATTRIBUTES attributes
    cdef RFC_FUNCTION_DESC_HANDLE funcDesc
    cdef RFC_ABAP_NAME funcName

    global server_functions

    # section 5.6.2 of SAP NWRFC SDK Programming Guide 7.50
    context = get_server_context(rfcHandle, serverErrorInfo)
    if context is None:
        err_msg = f"Error code {serverErrorInfo.code} when getting server context for connection '{<uintptr_t>rfcHandle}'"
        new_error = ExternalRuntimeError(
            message=err_msg,
            code=RFC_EXTERNAL_FAILURE
        )
        fillError(new_error, serverErrorInfo)
        return RFC_EXTERNAL_FAILURE

    funcDesc = RfcDescribeFunction(funcHandle, NULL)
    RfcGetFunctionName(funcDesc, funcName, NULL)

    func_name = wrapString(funcName)
    if func_name not in server_functions:
        _server_log("genericHandler", f"No metadata found for function '{function_name}'")
        return RFC_NOT_FOUND

    func_data = server_functions[func_name]
    callback = func_data['callback']
    server = func_data['server']
    # func_desc = func_data['func_desc_handle']

    try:
        rc = RfcGetConnectionAttributes(rfcHandle, &attributes, &errorInfo)
        if rc != RFC_OK:
            _server_log("genericHandler", f"Request for '{func_name}': Error while retrieving connection attributes (rc={rc}).")
            if not server.debug:
                raise ExternalRuntimeError(message="Invalid connection handle.")
            conn_attr = {}
        else:
            conn_attr = wrapConnectionAttributes(attributes)
            _server_log(
                "genericHandler",
                "User '{user}' from system '{sysId}' client '{client}' host '{partnerHost}' invokes '{func_name}'"
                .format(func_name=func_name, **conn_attr)
            )

        # Context of the request. Might later be extended by activeParameter information.
        request_context = {
            'connection_attributes': conn_attr,
            'server_context': context
        }

        # Authorization check
        auth_function = server_context["auth_check"]
        rc = auth_function(func_name, request_context)
        if rc != RFC_OK:
            new_error = ExternalRuntimeError(
                message=f"Authentication exception raised by callback function: '{func_name}'",
                code=RFC_EXTERNAL_FAILURE
            )
            fillError(new_error, serverErrorInfo)
            return RFC_EXTERNAL_FAILURE

        # Filter out variables that are of direction u'RFC_EXPORT'
        # (these will be set by the callback function)
        func_handle_variables = wrapResult(funcDesc, funcHandle, RFC_EXPORT, server.rstrip)

        # Invoke callback function
        result = callback(request_context, **func_handle_variables)

        # Return results
        if context["call_type"] != UnitCallType.background_unit:
            for name, value in result.iteritems():
                fillFunctionParameter(funcDesc, funcHandle, name, value)

    # Server exception handling: cf. SAP NetWeaver RFC SDK 7.50
    # 5.1 Preparing a Server Program for Receiving RFC Requests
    except ExternalRuntimeError as e:  # System failure
        # Parameter: message (optional: msg_type, msg_class, msg_number, msg_v1-v4)
        # returns:   RFC_EXTERNAL_FAILURE
        fillError(e, serverErrorInfo)
        serverErrorInfo.code = RFC_EXTERNAL_FAILURE  # Overwrite code, if set.
        _server_log("genericHandler", f"Request for '{func_name}' raises ExternalRuntimeError {e} - code set to RFC_EXTERNAL_FAILURE.")
        return RFC_EXTERNAL_FAILURE
    except ABAPRuntimeError as e:  # ABAP Message
        # Parameter: msg_type, msg_class, msg_number, msg_v1-v4
        # returns:   RFC_ABAP_MESSAGE
        fillError(e, serverErrorInfo)
        serverErrorInfo.code = RFC_ABAP_MESSAGE  # Overwrite code, if set.
        _server_log("genericHandler", f"Request for '{func_name}' raises ABAPRuntimeError {e} - code set to RFC_ABAP_MESSAGE.")
        return RFC_ABAP_MESSAGE
    except ABAPApplicationError as e:  # ABAP Exception in implementing function
        # Parameter: key (optional: msg_type, msg_class, msg_number, msg_v1-v4)
        # returns:   RFC_ABAP_EXCEPTION
        fillError(e, serverErrorInfo)
        serverErrorInfo.code = RFC_ABAP_EXCEPTION  # Overwrite code, if set.
        _server_log("genericHandler", f"Request for '{func_name}' raises ABAPApplicationError {e} - code set to RFC_ABAP_EXCEPTION.")
        return RFC_ABAP_EXCEPTION
    except Exception as ex:
        exctype, value = exc_info()[:2]
        _server_log(
            "genericHandler",
            f"Request for '{func_name}' raises an invalid exception:\n Exception: {exctype}\n Values: {value}\n"
            "Callback functions may only raise ABAPApplicationError, ABAPRuntimeError, or ExternalRuntimeError.\n"
            "The values of the request were:\n"
            f"params: {func_handle_variables}\nrequest_context: {request_context}"
        )
        new_error = ExternalRuntimeError(
            message="Invalid exception raised by callback function.",
            code=RFC_EXTERNAL_FAILURE
        )
        fillError(new_error, serverErrorInfo)
        return RFC_EXTERNAL_FAILURE

    return RFC_OK


cdef class Server:
    """ An ABAP server

    An instance of :class:`~pyrfc.Server` allows for installing
    Python callback functions and serve requests from SAP systems.

    :param server_params: Parameters for registering Python server.
                          The parameters may contain the following keywords:
                          ``GWHOST`, ``GWSERV``, ``PROGRAM_ID``, ``TRACE``,
                          and ``SAPROUTER``.

    :type server_params: dict

    :param client_params: Parameters for Python client connection.
                          The parameters may contain the following keywords:
                          ``GWHOST`, ``GWSERV``, ``PROGRAM_ID``, ``TRACE``,
                          and ``SAPROUTER``.

    :type server_params: dict

    :param config: Configuration of the instance. Allowed keys are:

           ``debug``
             For testing/debugging operations. If True, the server
             behaves more permissive, e.g. allows incoming calls without a
             valid connection handle. (default is False)

    :type config: dict or None (default)

    :raises: :exc:`~pyrfc.RFCError` or a subclass
             thereof if the connection attempt fails.
    """
    cdef public bint debug
    cdef public bint rstrip
    cdef Connection _client_connection
    cdef ServerConnection _server_connection
    cdef object _server_thread

    __bgRfcFunction = {
        "check": None,
        "commit": None,
        "rollback": None,
        "confirm": None,
        "getState": None
    }

    def __cinit__(self, server_params, client_params, config=None):
        # config parsing
        config = config or {}
        self.debug = config.get('debug', False)
        self.rstrip = config.get('rstrip', True)
        server_context["server_log"] = config.get("server_log", False)
        server_context["auth_check"] = config.get("auth_check", default_auth_check)
        server_context["port"] = config.get("port", 8080)

        self._client_connection = Connection(**client_params)
        self._server_connection = ServerConnection(**server_params)
        self._server_thread=Thread(target=self.serve)

    @staticmethod
    cdef RFC_RC __onCheckFunction(RFC_CONNECTION_HANDLE rfcHandle, const RFC_UNIT_IDENTIFIER *identifier) with gil:
        handler = Server.__bgRfcFunction["check"]
        if handler is None:
            return RCStatus.OK.value
        try:
            unit_identifier = wrapUnitIdentifier(identifier[0])
            return handler(<uintptr_t>rfcHandle, unit_identifier).value
        except Exception as ex:
            _server_log("Error in bgRFC handler onCheck:", ex)
            return RCStatus.RFC_EXTERNAL_FAILURE.value

    @staticmethod
    cdef RFC_RC __onCommitFunction(RFC_CONNECTION_HANDLE rfcHandle, const RFC_UNIT_IDENTIFIER *identifier) with gil:
        handler = Server.__bgRfcFunction["commit"]
        if handler is None:
            return RCStatus.OK.value
        try:
            unit_identifier = wrapUnitIdentifier(identifier[0])
            return handler(<uintptr_t>rfcHandle, unit_identifier).value
        except Exception as ex:
            _server_log("Error in bgRFC handler onCommit:", ex)
            return RCStatus.RFC_EXTERNAL_FAILURE.value

    @staticmethod
    cdef RFC_RC __onRollbackFunction(RFC_CONNECTION_HANDLE rfcHandle, const RFC_UNIT_IDENTIFIER *identifier) with gil:
        handler = Server.__bgRfcFunction["rollback"]
        if handler is None:
            return RCStatus.OK.value
        try:
            unit_identifier = wrapUnitIdentifier(identifier[0])
            return handler(<uintptr_t>rfcHandle, unit_identifier).value
        except Exception as ex:
            _server_log("Error in bgRFC handler onRollback:", ex)
            return RCStatus.RFC_EXTERNAL_FAILURE.value

    @staticmethod
    cdef RFC_RC __onConfirmFunction(RFC_CONNECTION_HANDLE rfcHandle, const RFC_UNIT_IDENTIFIER *identifier) with gil:
        handler = Server.__bgRfcFunction["confirm"]
        if handler is None:
            return RCStatus.OK.value
        try:
            unit_identifier = wrapUnitIdentifier(identifier[0])
            return handler(<uintptr_t>rfcHandle, unit_identifier).value
        except Exception as ex:
            _server_log("Error in bgRFC handler onConfirm:", ex)
            return RCStatus.RFC_EXTERNAL_FAILURE.value

    @staticmethod
    cdef RFC_RC __onGetStateFunction(
                RFC_CONNECTION_HANDLE rfcHandle,
                const RFC_UNIT_IDENTIFIER *identifier,
                RFC_UNIT_STATE *unitState
            ) with gil:
        handler = Server.__bgRfcFunction["getState"]
        if handler is None:
            _server_log("bgRFC handler onGetState is not registered for server connection handle '{<uintptr_t>rfcHandle}'")
            return RCStatus.RFC_EXTERNAL_FAILURE.value
        try:
            unit_identifier = wrapUnitIdentifier(identifier[0])
            state = handler(<uintptr_t>rfcHandle, unit_identifier)
            # section 5.6.3 pg 84 of SAP NWRFC SDK Programming Guide 7.50
            if state == UnitState.created or state == UnitState.executed:
                unitState[0] = RFC_UNIT_IN_PROCESS
            elif state == UnitState.committed:
                idunitStateentifier[0] = RFC_UNIT_COMMITTED
            elif state == UnitState.rolled_back:
                unitState[0] = RFC_UNIT_ROLLED_BACK
            elif state == UnitState.confirmed:
                unitState[0] = RFC_UNIT_CONFIRMED
            else:
                raise Exception(f"TID {unit_identifier['id']} invalid state '{state}'")
            return RCStatus.OK.value
        except Exception as ex:
            _server_log("Error in bgRFC handler onGetState:\n", ex)
            return RCStatus.RFC_EXTERNAL_FAILURE.value

    def bgrfc_init(self, sysId, bgRfcFunction):
        """Installs the necessary callback functions for processing incoming bgRFC calls.

        These functions need to be implemented by Python application and will be used by the RFC runtime.
        When no callback function is provided, the default one is used,
        not necessarily matching your application requirements.

        For more info search for the ``RfcInstallBgRfcHandlers`` method in
        `SAP NetWeaver RFC SDK Doxygen Documentation <https://support.sap.com/en/product/connectors/nwrfcsdk.html>`_

        :param sysId: System ID of the SAP system for which to use this set of transaction handlers, or None
                      When None value provided, the transaction handlers will be used for bgRFC calls from
                      any backend system, for which no explicit handlers have been installed.
        :type sysId: string or None

        :param bgRfcFunction: Function callbacks
        :type bgRfcFunction: dict(str, function)

            * "check": onCheckFunction,
            * "commit": onCommitFunction,
            * "rollback": onRollbackFunction,
            * "confirm": onConfirmFunction,
            * "getState": onGetStateFunction,

        :return: error code, zero when no error
        """
        for func_name in bgRfcFunction:
            if func_name not in Server.__bgRfcFunction:
                raise TypeError(f"BgRfc callback function key not supported: '{func_name}'")
            if not callable(bgRfcFunction[func_name]):
                raise TypeError(f"BgRfc callback function referenced by '{func_name}' is not callable: '{bgRfcFunction[func_name]}'")
            Server.__bgRfcFunction[func_name] = bgRfcFunction[func_name]
        return self.install_bgrfc_handlers(sysId)

    def install_bgrfc_handlers(self, sysId):
        ucSysId = fillString(sysId) if sysId is not None else NULL
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_RC rc = RfcInstallBgRfcHandlers(
                            ucSysId,
                            Server.__onCheckFunction,
                            Server.__onCommitFunction,
                            Server.__onRollbackFunction,
                            Server.__onConfirmFunction,
                            Server.__onGetStateFunction,
                            &errorInfo
                        )
        free(ucSysId)
        if rc != RFC_OK or errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)
        return rc

    def add_function(self, func_name, callback):
        """
        Installs a function in the server.

        :param func_name: ABAP remote function module name
        :type func_name: string

        :param callback: A callback function that implements the logic.
            The function must accept a ``request_context`` parameter and
            all IMPORT, CHANGING, and TABLE parameters of the given
            ``func_desc``.
        :raises: :exc:`TypeError` if a function with the name given is already
            installed.
        """
        global server_functions
        if func_name in server_functions:
            raise TypeError(f"Server function '{func_name}' already installed.")

        if not self._client_connection:
            self._client_connection.open()
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_ABAP_NAME funcName = fillString(func_name)
        cdef RFC_FUNCTION_DESC_HANDLE func_desc_handle = RfcGetFunctionDesc(self._client_connection._handle, funcName, &errorInfo)
        self._client_connection.close()

        if errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)

        server_functions[func_name] = {
            "func_desc_handle": <uintptr_t>func_desc_handle,
            "callback": callback,
            "server": self
        }

        _server_log("Server function installed", func_name)
        _server_log("Server function installed", server_functions[func_name])

    def serve(self):
        """
        Starts the RFC server, waiting for incoming requests and processes them.

        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the server processing fails.
        """
        cdef RFC_ERROR_INFO errorInfo

        cdef RFC_RC rc = RfcInstallGenericServerFunction(genericHandler, metadataLookup, &errorInfo)
        if rc != RFC_OK or errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)

        rc = RfcLaunchServer(self._server_connection._handle, &errorInfo)
        if rc != RFC_OK or errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)
        _server_log("Server", f"launched {self._server_connection.handle}")

        return rc

    def start(self):
        """
        Start the RFC server in new thread, waiting for incoming requests and processes them.
        """
        self._server_thread.start()

    def stop(self):
        """
        Stop the RFC server thread.
        """
        if self._server_thread.is_alive():
            self._server_thread.join()

    def close(self):
        """ Explicitly close the registration.
        Note that this is usually not necessary as the registration will be closed
        automatically upon object destruction. However, if the the object destruction
        is delayed by the garbage collection, problems may occur when too many
        servers are registered.
        """
        self.stop()
        self._close()

    def get_server_attributes(self):
        """Retrieves detailed information about a multi-count Registered Server or a TCP Socket Server.

        :returns: Dictionary with server state and attributes
        :rtype: dict(str, str or int)

            * serverName: This server's name as given when creating the server.
            * protocolType: This RFC server's type:
              RFC_MULTI_COUNT_REGISTERED_SERVER or RFC_TCP_SOCKET_SERVER
            * registrationCount: The current number of active registrations (in case of a Registered Server)
              or the maximum number of parallel connections the server will accept (in case of a TCP Socket Server)
            * state: Used in state information in order to indicate the current state of an RFC Server.
            * currentBusyCount: The number of requests currently being processed.
            * peakBusyCount: The maximum number of requests the server has been processing in parallel since it has been created
        """
        cdef RFC_RC rc
        cdef RFC_SERVER_ATTRIBUTES attributes
        cdef RFC_ERROR_INFO errorInfo

        rc = RfcGetServerAttributes(self._server_connection._handle, &attributes, &errorInfo)
        if rc != RFC_OK or errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)
        rfcServerState = wrapString(RfcGetServerStateAsString(attributes.state), -1, True)
        return {
            # This server's name as given when creating the server.
            'serverName': wrapString(attributes.serverName, -1, True)
            # This RFC server's type. Will be one of RFC_MULTI_COUNT_REGISTERED_SERVER or RFC_TCP_SOCKET_SERVER
            , 'protocolType': "multi count" if attributes.type == RFC_MULTI_COUNT_REGISTERED_SERVER
            else socket.gethostname()  # Own host name
            # The current number of active registrations (in case of a Registered Server)
            # or the maximum number of parallel connections the server will accept (in case of a TCP Socket Server)
            , 'registrationCount': attributes.registrationCount
            # Used in state information in order to indicate the current state of an RFC Server.
            , 'state': rfcServerState
            # The number of requests currently being processed.
            , 'currentBusyCount': attributes.currentBusyCount
            # The maximum number of requests the server has been processing in parallel since it has been created
            , 'peakBusyCount': attributes.peakBusyCount
        }

    def _close(self):
        """ Close the connection (private function)
        :raises: :exc:`~pyrfc.RFCError` or a subclass
                 thereof if the connection cannot be closed cleanly.
        """
        # Shutdown server
        if self._server_connection:
            self._server_connection.close()
        # Remove all installed server functions
        after_remove = {}
        global server_functions
        for func_name, func_data in server_functions.items():
            if func_data["server"] != self:
                after_remove[func_name] = func_data
        server_functions = after_remove

    cdef _error(self, RFC_ERROR_INFO* errorInfo):
        """
        Error treatment of a connection.

        :param errorInfo: the errorInfo data given in a RFC that returned an RC > 0.
        :return: nothing, raises an error
        """
        # TODO: Error treatment server
        # Set alive=false if the error is in a certain group
        # Before, the alive=false setting depended on the error code. However, the group seems more robust here.
        # errorInfo.code in
        #   RFC_COMMUNICATION_FAILURE, RFC_ABAP_MESSAGE, RFC_ABAP_RUNTIME_FAILURE, RFC_INVALID_HANDLE, RFC_NOT_FOUND, RFC_INVALID_PARAMETER:
        # if errorInfo.group in (ABAP_RUNTIME_FAILURE, LOGON_FAILURE, COMMUNICATION_FAILURE, EXTERNAL_RUNTIME_FAILURE):
        #    self.alive = False

        raise wrapError(errorInfo)


cdef RFC_TYPE_DESC_HANDLE fillTypeDescription(type_desc):
    """
    :param type_desc: object of class TypeDescription
    :return: Handle of RFC_TYPE_DESC_HANDLE
    """
    cdef RFC_RC rc = RFC_OK
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_TYPE_DESC_HANDLE typeDesc
    cdef RFC_FIELD_DESC fieldDesc
    cdef SAP_UC* sapuc

    # Set name, nuc_length, and uc_length
    sapuc = fillString(type_desc.name)
    typeDesc = RfcCreateTypeDesc(sapuc, &errorInfo)
    free(sapuc)
    if typeDesc == NULL:
        raise wrapError(&errorInfo)
    rc = RfcSetTypeLength(typeDesc, type_desc.nuc_length, type_desc.uc_length, &errorInfo)
    if rc != RFC_OK:
        RfcDestroyTypeDesc(typeDesc, NULL)
        raise wrapError(&errorInfo)

    for field_desc in type_desc.fields:
        # Set name
        sapuc = fillString(field_desc['name'])
        strncpyU(fieldDesc.name, sapuc, len(field_desc['name']) + 1)
        free(sapuc)
        fieldDesc.type = RfcFieldType[field_desc['field_type']].value
        fieldDesc.nucLength = field_desc['nuc_length']
        fieldDesc.nucOffset = field_desc['nuc_offset']
        fieldDesc.ucLength = field_desc['uc_length']
        fieldDesc.ucOffset = field_desc['uc_offset']
        fieldDesc.decimals = field_desc['decimals']
        if field_desc['type_description'] is not None:
            fieldDesc.typeDescHandle = fillTypeDescription(field_desc['type_description'])
        else:
            fieldDesc.typeDescHandle = NULL
        fieldDesc.extendedDescription = NULL
        rc = RfcAddTypeField(typeDesc, &fieldDesc, &errorInfo)
        if rc != RFC_OK:
            RfcDestroyTypeDesc(typeDesc, NULL)
            raise wrapError(&errorInfo)

    return typeDesc

cdef RFC_FUNCTION_DESC_HANDLE fillFunctionDescription(func_desc):
    """
    :param func_desc: object of class FunctionDescription
    :return: Handle of RFC_FUNCTION_DESC_HANDLE
    """
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_FUNCTION_DESC_HANDLE funcDesc
    cdef RFC_PARAMETER_DESC paramDesc
    cdef SAP_UC* sapuc

    # Set name
    sapuc = fillString(func_desc.name)
    funcDesc = RfcCreateFunctionDesc(sapuc, &errorInfo)
    free(sapuc)
    if funcDesc == NULL:
        raise wrapError(&errorInfo)

    for param_desc in func_desc.parameters:
        sapuc = fillString(param_desc['name'])
        strncpyU(paramDesc.name, sapuc, len(param_desc['name']) + 1)
        free(sapuc)
        paramDesc.type = RfcFieldType[param_desc['parameter_type']].value
        paramDesc.direction = RfcParameterDirection[param_desc['direction']].value
        paramDesc.nucLength = param_desc['nuc_length']
        paramDesc.ucLength = param_desc['uc_length']
        paramDesc.decimals = param_desc['decimals']
        # defaultValue
        sapuc = fillString(param_desc['default_value'])
        strncpyU(paramDesc.defaultValue, sapuc, len(param_desc['default_value']) + 1)
        free(sapuc)
        # parameterText
        sapuc = fillString(param_desc['parameter_text'])
        strncpyU(paramDesc.parameterText, sapuc, len(param_desc['parameter_text']) + 1)
        free(sapuc)
        paramDesc.optional = <bint> param_desc['optional']
        if param_desc['type_description'] is not None:
            paramDesc.typeDescHandle = fillTypeDescription(param_desc['type_description'])
        else:
            paramDesc.typeDescHandle = NULL
        paramDesc.extendedDescription = NULL
        rc = RfcAddParameter(funcDesc, &paramDesc, &errorInfo)
        if rc != RFC_OK:
            RfcDestroyFunctionDesc(funcDesc, NULL)
            raise wrapError(&errorInfo)

    return funcDesc

cdef RFC_UNIT_IDENTIFIER fillUnitIdentifier(unit) except *:
    cdef RFC_UNIT_IDENTIFIER uIdentifier
    cdef SAP_UC* sapuc
    uIdentifier.unitType = fillString("Q" if unit['queued'] else "T")[0]
    if len(unit['id']) != RFC_UNITID_LN:
        raise RFCError(f"Invalid length of unit['id'] (should be {RFC_UNITID_LN}, but found {len(unit['id'])}).")
    sapuc = fillString(unit['id'])
    strncpyU(uIdentifier.unitID, sapuc, RFC_UNITID_LN + 1)
    free(sapuc)
    return uIdentifier


################################################################################
# THROUGHPUT FUNCTIONS                                                         #
################################################################################

cdef class Throughput:
    _registry = []

    cdef RFC_THROUGHPUT_HANDLE _throughput_handle
    cdef _connections

    def __init__(self, connections = None):
        cdef RFC_ERROR_INFO errorInfo
        self._throughput_handle = NULL
        self._connections = set()
        self._throughput_handle = RfcCreateThroughput(&errorInfo)
        if errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)
        Throughput._registry.append(self)
        connections = connections or []
        if type(connections) is not list:
            connections = [connections]
        for conn in connections:
            if not isinstance(conn, Connection):
                raise TypeError('Connection object required, received', conn, 'of type', type(conn))
            self.setOnConnection(conn)

    @property
    def connections(self):
        """Get connections attached to throughput monitoring

        :getter: Connections' instances
        :type: set of Connection
        """
        return self._connections

    @property
    def _handle(self):
        """Get throughput object handle

        :getter: Throughput object handle
        :type: uintptr_t
        """
        return <uintptr_t>self._throughput_handle

    def setOnConnection(self, Connection connection):
        """Attaches a throughput object to a connection to be monitored by the throughput object.
        Once attached to a connection, the throughput object collects the data statistics of
        function calls invoked via this connection.

        For more info search for the ``RfcSetThroughputOnConnection`` method in
        `SAP NetWeaver RFC SDK Doxygen Documentation <https://support.sap.com/en/product/connectors/nwrfcsdk.html>`_

        :param connection: Connection instance to be attached to throughput monitoring
        :type connection: Connection

        :return: nothing, raises an error
        """
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_RC rc = RfcSetThroughputOnConnection(connection._handle, self._throughput_handle, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        self._connections.add(connection)

    @staticmethod
    def getFromConnection(Connection connection):
        """Returns the currently attached throughput object from a connection, if any.

        For more info search for the ``RfcGetThroughputFromConnection`` method in
        `SAP NetWeaver RFC SDK Doxygen Documentation <https://support.sap.com/en/product/connectors/nwrfcsdk.html>`_

        :param connection: Connection instance
        :type connection: Connection

        :returns: Throughput object the connection is attached to, if any
        :rtype: Throughput

        :raises: :exc:`~pyrfc.RFCError` or a subclass in case of error
        """
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_THROUGHPUT_HANDLE throughput = RfcGetThroughputFromConnection(connection._handle, &errorInfo)
        if errorInfo.code != RFC_OK:
            raise wrapError(&errorInfo)
        for t in Throughput._registry:
            if t._handle == <uintptr_t>throughput:
                return t
        return None

    def removeFromConnection(self, Connection connection):
        """Removes the throughput object from a connection.
        The connection will no longer be monitored.

        :param connection: Connection instance
        :type connection: Connection
        :returns: Nothing
        :raises: :exc:`~pyrfc.RFCError` or a subclass in case of error
        """
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_RC rc = RfcRemoveThroughputFromConnection(connection._handle, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        self._connections.remove(connection)

    def reset(self):
        """Resets the data so far collected and aggregated by the throughput object.

        :returns: Nothing
        :raises: :exc:`~pyrfc.RFCError` or a subclass in case of error
        """
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_RC rc = RfcResetThroughput(self._throughput_handle, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)

    cdef _destroy(self):
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_RC rc
        self._registry.clear()
        self._connections = None
        if self._throughput_handle != NULL:
            rc = RfcDestroyThroughput(self._throughput_handle, &errorInfo)
            self._throughput_handle = NULL
            if rc != RFC_OK:
                # is ok
                pass

    def __del__(self):
        self.destroy()

    def __exit__(self, type, value, traceback):
        self._destroy()

    def __enter__(self):
        return self

    @property
    def stats(self):
        """Get throughput monitor statistics

        :getter: Throughput monitor counters
        :type: dict(str,int)

           * numberOfCalls
           * sentBytes
           * receivedBytes
           * applicationTime
           * totalTime
           * serializationTime
           * deserializationTime
        """
        cdef RFC_ERROR_INFO errorInfo
        cdef RFC_RC rc
        cdef SAP_ULLONG numberOfCalls
        cdef SAP_ULLONG sentBytes
        cdef SAP_ULLONG receivedBytes
        cdef SAP_ULLONG applicationTime
        cdef SAP_ULLONG totalTime
        cdef SAP_ULLONG serializationTime
        cdef SAP_ULLONG deserializationTime

        _stats = {}

        if self._throughput_handle == NULL:
            raise RFCError('No connections assigned')

        rc = RfcGetNumberOfCalls (self._throughput_handle, &numberOfCalls, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['numberOfCalls'] = numberOfCalls

        rc = RfcGetSentBytes (self._throughput_handle, &sentBytes, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['sentBytes'] = sentBytes

        rc = RfcGetReceivedBytes (self._throughput_handle, &receivedBytes, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['receivedBytes'] = receivedBytes

        rc = RfcGetApplicationTime (self._throughput_handle, &applicationTime, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['applicationTime'] = applicationTime

        rc = RfcGetTotalTime (self._throughput_handle, &totalTime, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['totalTime'] = totalTime

        rc = RfcGetSerializationTime (self._throughput_handle, &serializationTime, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['serializationTime'] = serializationTime

        rc = RfcGetDeserializationTime (self._throughput_handle, &deserializationTime, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        _stats['deserializationTime'] = deserializationTime

        return _stats


################################################################################
# FILL FUNCTIONS                                                               #
################################################################################

cdef fillFunctionParameter(RFC_FUNCTION_DESC_HANDLE funcDesc, RFC_FUNCTION_HANDLE container, name, value):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_PARAMETER_DESC paramDesc
    cName = fillString(name)
    rc = RfcGetParameterDescByName(funcDesc, cName, &paramDesc, &errorInfo)
    free(cName)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    fillVariable(paramDesc.type, container, paramDesc.name, value, paramDesc.typeDescHandle)

cdef fillStructureField(RFC_TYPE_DESC_HANDLE typeDesc, RFC_STRUCTURE_HANDLE container, name, value):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_FIELD_DESC fieldDesc
    cdef SAP_UC* cName = fillString(name)
    rc = RfcGetFieldDescByName(typeDesc, cName, &fieldDesc, &errorInfo)
    free(cName)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    fillVariable(fieldDesc.type, container, fieldDesc.name, value, fieldDesc.typeDescHandle)

cdef fillTable(RFC_TYPE_DESC_HANDLE typeDesc, RFC_TABLE_HANDLE container, lines):
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_STRUCTURE_HANDLE lineHandle
    cdef unsigned int rowCount = int(len(lines))
    cdef unsigned int i = 0
    while i < rowCount:
        lineHandle = RfcAppendNewRow(container, &errorInfo)
        if not lineHandle:
            raise wrapError(&errorInfo)
        line = lines[i]
        if type(line) is dict:
            for name, value in line.iteritems():
                fillStructureField(typeDesc, lineHandle, name, value)
        else:
            fillStructureField(typeDesc, lineHandle, '', line)
        i += 1

cdef fillVariable(RFCTYPE typ, RFC_FUNCTION_HANDLE container, SAP_UC* cName, value, RFC_TYPE_DESC_HANDLE typeDesc):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_STRUCTURE_HANDLE struct
    cdef RFC_TABLE_HANDLE table
    cdef SAP_UC* cValue
    cdef SAP_RAW* bValue
    global _LOCALE_RADIX
    # print ("fill", wrapString(cName), value, type(value))
    try:
        if typ == RFCTYPE_STRUCTURE:
            if type(value) is not dict:
                raise TypeError('dictionary required for structure parameter, received', str(type(value)))
            rc = RfcGetStructure(container, cName, &struct, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            for name, value in value.iteritems():
                fillStructureField(typeDesc, struct, name, value)
        elif typ == RFCTYPE_TABLE:
            if type(value) is not list:
                raise TypeError('list required for table parameter, received', str(type(value)))
            rc = RfcGetTable(container, cName, &table, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            fillTable(typeDesc, table, value)
        elif typ == RFCTYPE_BYTE:
            bValue = fillBytes(value)
            rc = RfcSetBytes(container, cName, bValue, int(len(value)), &errorInfo)
            free(bValue)
        elif typ == RFCTYPE_XSTRING:
            bValue = fillBytes(value)
            rc = RfcSetXString(container, cName, bValue, int(len(value)), &errorInfo)
            free(bValue)
        elif typ == RFCTYPE_CHAR:
            if type(value) is not str:
                raise TypeError('an string is required, received', value, 'of type', type(value))
            cValue = fillString(value)
            rc = RfcSetChars(container, cName, cValue, strlenU(cValue), &errorInfo)
            free(cValue)
        elif typ == RFCTYPE_STRING:
            if type(value) is not str:
                raise TypeError('an string is required, received', value, 'of type', type(value))
            cValue = fillString(value)
            rc = RfcSetString(container, cName, cValue, strlenU(cValue), &errorInfo)
            free(cValue)
        elif typ == RFCTYPE_NUM:
            try:
                if value.isdigit():
                    cValue = fillString(value)
                    rc = RfcSetNum(container, cName, cValue, strlenU(cValue), &errorInfo)
                    free(cValue)
                else:
                    raise
            except Exception as ex:
                raise TypeError('a numeric string is required, received', value, 'of type', type(value))
        elif typ == RFCTYPE_BCD or typ == RFCTYPE_FLOAT or typ == RFCTYPE_DECF16 or typ == RFCTYPE_DECF34:
            # cast to string prevents rounding errors in NWRFC SDK
            try:
                if type(value) is float or type(value) is Decimal:
                    svalue = str(value)
                else:
                    # string passed from application should be locale correct, do nothing
                    svalue = value
                # decimal separator must be "." for the Decimal parsing check
                locale_radix = _LOCALE_RADIX  # localeconv()['decimal_point']
                if locale_radix != ".":
                    Decimal('.'.join(svalue.rsplit(locale_radix, 1)))
                else:
                    Decimal(svalue)
                cValue = fillString(svalue)
            except Exception as ex:
                raise TypeError('a decimal value required, received', value, 'of type', type(value))
            rc = RfcSetString(container, cName, cValue, strlenU(cValue), &errorInfo)
            free(cValue)
        elif typ in (RFCTYPE_INT, RFCTYPE_INT1, RFCTYPE_INT2):
            if type(value) is not int:
                raise TypeError('an integer required, received', value, 'of type', type(value))
            rc = RfcSetInt(container, cName, value, &errorInfo)
        elif typ == RFCTYPE_INT8:
            if type(value) is not int:
                raise TypeError('an integer required, received', value, 'of type', type(value))
            rc = RfcSetInt8(container, cName, value, &errorInfo)
        elif typ == RFCTYPE_UTCLONG:
            if type(value) is not str:
                raise TypeError('an string is required, received', value, 'of type', type(value))
            cValue = fillString(value)
            rc = RfcSetString(container, cName, cValue, strlenU(cValue), &errorInfo)
            free(cValue)
        elif typ == RFCTYPE_DATE:
            if value:
                format_ok = True
                if type(value) is date:
                    cValue = fillString(f'{value.year:04}{value.month:02}{value.day:02}')
                else:
                    try:
                        if len(value) != 8:
                            format_ok = False
                        else:
                            if len(value.rstrip()) > 0:
                                date(int(value[:4]), int(value[4:6]), int(value[6:8]))
                            cValue = fillString(value)
                    except Exception as ex:
                        format_ok = False
                if not format_ok:
                    raise TypeError('date value required, received', value, 'of type', type(value))
                rc = RfcSetDate(container, cName, cValue, &errorInfo)
                free(cValue)
            else:
                rc = RFC_OK
        elif typ == RFCTYPE_TIME:
            if value:
                format_ok = True
                if type(value) is time:
                    cValue = fillString(f'{value.hour:02}{value.minute:02}{value.second:02}')
                else:
                    try:
                        if len(value) != 6:
                            format_ok = False
                        else:
                            if len(value.rstrip()) > 0:
                                time(int(value[:2]), int(value[2:4]), int(value[4:6]))
                            cValue = fillString(value)
                    except Exception as ex:
                        format_ok = False

                if not format_ok:
                    raise TypeError('time value required, received', value, 'of type', type(value))
                rc = RfcSetTime(container, cName, cValue, &errorInfo)
                free(cValue)
            else:
                rc = RFC_OK
        else:
            raise RFCError('Unknown RFC type %d when filling %s' % (typ, wrapString(cName)))
    except TypeError as e:
        # This way the field name will be attached in reverse direction
        # to the argument list of the exception. This helps users to find
        # mistakes easier in complex mapping scenarios.
        e.args += (wrapString(cName), )
        raise
    if rc != RFC_OK:
        raise wrapError(&errorInfo)

cdef SAP_RAW* fillBytes(pystr) except NULL:
    cdef size_t size = len(pystr)
    cdef SAP_RAW* bytes = <SAP_RAW*> malloc(size)
    memcpy(bytes, <char*> pystr, size)
    return bytes

cdef fillError(exception, RFC_ERROR_INFO* errorInfo):
    group2error = {
                    ABAPApplicationError: ABAP_APPLICATION_FAILURE,
                    ABAPRuntimeError: ABAP_RUNTIME_FAILURE,
                    LogonError: LOGON_FAILURE,
                    CommunicationError: COMMUNICATION_FAILURE,
                    ExternalRuntimeError: EXTERNAL_RUNTIME_FAILURE,
                    ExternalApplicationError: EXTERNAL_APPLICATION_FAILURE,
                    ExternalAuthorizationError: EXTERNAL_AUTHORIZATION_FAILURE
                }
    if type(exception) not in group2error:
        raise RFCError("Not a valid error group.")

    errorInfo.group = group2error.get(type(exception))

    if exception.message:  # fixed length, exactly 512 chars
        # str = exception.message[0:512].ljust(512)
        str = exception.message[0:512]
        sapuc = fillString(str)
        strncpyU(errorInfo.message, sapuc, min(len(str)+1, 512))
        free(sapuc)
    errorInfo.code = exception.code if exception.code else RFC_UNKNOWN_ERROR
    if exception.key:  # fixed length, exactly 128 chars
        str = exception.key[0:128]
        sapuc = fillString(str)
        strncpyU(errorInfo.key, sapuc, min(len(str)+1, 128))
        free(sapuc)
    if exception.msg_class:
        sapuc = fillString(exception.msg_class[0:20])
        strncpyU(errorInfo.abapMsgClass, sapuc, len(exception.msg_class[0:20]) + 1)
        free(sapuc)
    if exception.msg_type:
        sapuc = fillString(exception.msg_type[0:1])
        strncpyU(errorInfo.abapMsgType, sapuc, len(exception.msg_type[0:1]) + 1)
        free(sapuc)
    if exception.msg_number:
        sapuc = fillString(exception.msg_number[0:3])
        strncpyU(errorInfo.abapMsgNumber, sapuc, len(exception.msg_number[0:3]) + 1)
        free(sapuc)
    if exception.msg_v1:
        sapuc = fillString(exception.msg_v1[0:50])
        strncpyU(errorInfo.abapMsgV1, sapuc, len(exception.msg_v1[0:50]) + 1)
        free(sapuc)
    if exception.msg_v2:
        sapuc = fillString(exception.msg_v2[0:50])
        strncpyU(errorInfo.abapMsgV2, sapuc, len(exception.msg_v2[0:50]) + 1)
        free(sapuc)
    if exception.msg_v3:
        sapuc = fillString(exception.msg_v3[0:50])
        strncpyU(errorInfo.abapMsgV3, sapuc, len(exception.msg_v3[0:50]) + 1)
        free(sapuc)
    if exception.msg_v4:
        sapuc = fillString(exception.msg_v4[0:50])
        strncpyU(errorInfo.abapMsgV4, sapuc, len(exception.msg_v4[0:50]) + 1)
        free(sapuc)

cdef SAP_UC* fillString(pyuc) except NULL:
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    ucbytes = pyuc.encode()
    cdef unsigned ucbytes_len = <unsigned> len(ucbytes)
    cdef unsigned sapuc_size = ucbytes_len + 1
    cdef SAP_UC* sapuc = mallocU(sapuc_size)
    sapuc[0] = 0
    cdef unsigned result_len = 0
    if ucbytes_len > 0:
        rc = RfcUTF8ToSAPUC(ucbytes, ucbytes_len, sapuc, &sapuc_size, &result_len, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
    return sapuc

################################################################################
# WRAPPER FUNCTIONS                                                            #
################################################################################
# wrapper functions take C values and returns Python values

cdef wrapConnectionAttributes(RFC_ATTRIBUTES attributes):
    return {
        'dest': wrapString(attributes.dest, 64, True).rstrip('\0')
        , 'host': wrapString(attributes.host, 100, True).rstrip('\0')
        , 'partnerHost': wrapString(attributes.partnerHost, 100, True).rstrip('\0')
        , 'sysNumber': wrapString(attributes.sysNumber, 2, True).rstrip('\0')
        , 'sysId': wrapString(attributes.sysId, 8, True).rstrip('\0')
        , 'client': wrapString(attributes.client, 3, True).rstrip('\0')
        , 'user': wrapString(attributes.user, 12, True).rstrip('\0')
        , 'language': wrapString(attributes.language, 2, True).rstrip('\0')
        , 'trace': wrapString(attributes.trace, 1, True).rstrip('\0')
        , 'isoLanguage': wrapString(attributes.isoLanguage, 2, True).rstrip('\0')
        , 'codepage': wrapString(attributes.codepage, 4, True).rstrip('\0')
        , 'partnerCodepage': wrapString(attributes.partnerCodepage, 4, True).rstrip('\0')
        , 'rfcRole': wrapString(attributes.rfcRole, 1, True).rstrip('\0')
        , 'type': wrapString(attributes.type, 1).rstrip('\0')
        , 'partnerType': wrapString(attributes.partnerType, 1, True).rstrip('\0')
        , 'rel': wrapString(attributes.rel, 4, True).rstrip('\0')
        , 'partnerRel': wrapString(attributes.partnerRel, 4, True).rstrip('\0')
        , 'kernelRel': wrapString(attributes.kernelRel, 4, True).rstrip('\0')
        , 'cpicConvId': wrapString(attributes.cpicConvId, 8, True).rstrip('\0')
        , 'progName': wrapString(attributes.progName, 128, True).rstrip('\0')
        , 'partnerBytesPerChar': wrapString(attributes.partnerBytesPerChar, 1, True).rstrip('\0')
        , 'partnerSystemCodepage': wrapString(attributes.partnerSystemCodepage, 4, True).rstrip('\0')
        , 'partnerIP': wrapString(attributes.partnerIP, 15, True).rstrip('\0')
        , 'partnerIPv6': wrapString(attributes.partnerIPv6, 45, True).rstrip('\0')
        , 'reserved': wrapString(attributes.reserved, 17, True).rstrip('\0')
    }


cdef wrapTypeDescription(RFC_TYPE_DESC_HANDLE typeDesc):
    """ Parses a RFC_TYPE_DESC_HANDLE

    :param typeDesc: Handle of RFC_TYPE_DESC_HANDLE
    :return: object of class TypeDescription
    """
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_FIELD_DESC fieldDesc
    cdef RFC_ABAP_NAME typeName
    cdef unsigned nuc_length, uc_length
    cdef unsigned i, fieldCount

    rc = RfcGetTypeName(typeDesc, typeName, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    name = wrapString(typeName)
    rc = RfcGetTypeLength(typeDesc, &nuc_length, &uc_length, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    type_desc = TypeDescription(name, nuc_length, uc_length)

    rc = RfcGetFieldCount(typeDesc, &fieldCount, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    for i in range(fieldCount):
        rc = RfcGetFieldDescByIndex(typeDesc, i, &fieldDesc, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        field_description = {
            'name': wrapString(fieldDesc.name),
            'field_type': RfcFieldType(fieldDesc.type).name,
            'nuc_length': fieldDesc.nucLength,
            'nuc_offset': fieldDesc.nucOffset,
            'uc_length': fieldDesc.ucLength,
            'uc_offset': fieldDesc.ucOffset,
            'decimals': fieldDesc.decimals
        }
        if fieldDesc.typeDescHandle is NULL:
            field_description['type_description'] = None
        else:
            field_description['type_description'] = wrapTypeDescription(fieldDesc.typeDescHandle)
        # Add field to object
        type_desc.add_field(**field_description)

    return type_desc

cdef wrapFunctionDescription(RFC_FUNCTION_DESC_HANDLE funcDesc):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_ABAP_NAME functionName
    cdef unsigned i, paramCount
    cdef RFC_PARAMETER_DESC paramDesc

    rc = RfcGetFunctionName(funcDesc, functionName, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    name = wrapString(functionName)
    func_desc = FunctionDescription(name)

    rc = RfcGetParameterCount(funcDesc, &paramCount, &errorInfo)
    if rc != RFC_OK:
        raise wrapError(&errorInfo)
    for i in range(paramCount):
        rc = RfcGetParameterDescByIndex(funcDesc, i, &paramDesc, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        parameter_description = {
            'name': wrapString(paramDesc.name),
            'parameter_type': RfcFieldType(paramDesc.type).name,
            'direction': RfcParameterDirection(paramDesc.direction).name,
            'nuc_length': paramDesc.nucLength,
            'uc_length': paramDesc.ucLength,
            'decimals': paramDesc.decimals,
            'default_value': wrapString(paramDesc.defaultValue),
            'parameter_text': wrapString(paramDesc.parameterText),
            'optional': bool(paramDesc.optional)
            # skip: void* extendedDescription;
            # This field can be used by the application programmer (i.e. you) to store arbitrary extra information.
        }
        if paramDesc.typeDescHandle is NULL:
            parameter_description['type_description'] = None
        else:
            parameter_description['type_description'] = wrapTypeDescription(paramDesc.typeDescHandle)
        func_desc.add_parameter(**parameter_description)

    return func_desc


cdef wrapResult(
            RFC_FUNCTION_DESC_HANDLE funcDesc,
            RFC_FUNCTION_HANDLE container,
            RFC_DIRECTION filter_parameter_direction,
            config
        ):
    """
    :param funcDesc: a C pointer to a function description.
    :param container: a C pointer to a function container
    :param filter_parameter_direction: A RFC_DIRECTION - parameters with this
           direction will be excluded.
    :param config (rstrip: right strip strings, dtime: return datetime objects)
    :return:
    """
    cdef unsigned i, paramCount
    cdef RFC_PARAMETER_DESC paramDesc
    RfcGetParameterCount(funcDesc, &paramCount, NULL)
    result = {}
    for i in range(paramCount):
        RfcGetParameterDescByIndex(funcDesc, i, &paramDesc, NULL)
        if paramDesc.direction != filter_parameter_direction:
            result[wrapString(paramDesc.name)] = wrapVariable(
                paramDesc.type,
                container,
                paramDesc.name,
                paramDesc.nucLength,
                paramDesc.typeDescHandle,
                config
            )
    return result

cdef wrapUnitIdentifier(RFC_UNIT_IDENTIFIER uIdentifier):
    return {
        'queued': "Q" == wrapString(&uIdentifier.unitType, 1),
        'id': wrapString(uIdentifier.unitID)
    }

cdef wrapUnitAttributes(RFC_UNIT_ATTRIBUTES *uattr):
    unit_attributes = {}
    unit_attributes['kernel_trace'] = uattr.kernelTrace != 0
    unit_attributes['sat_trace'] = uattr.satTrace != 0
    unit_attributes['unit_history'] = uattr.unitHistory != 0
    unit_attributes['lock'] = uattr.lock != 0
    unit_attributes['no_commit_check'] = uattr.noCommitCheck != 0
    unit_attributes['user'] = wrapString(uattr.user, 12, True)
    unit_attributes['client'] = wrapString(uattr.client, 3, True)
    unit_attributes['t_code'] = wrapString(uattr.tCode, 20, True)
    unit_attributes['program'] = wrapString(uattr.program, 40, True)
    unit_attributes['hostname'] = wrapString(uattr.hostname, 40, True)
    unit_attributes['sending_date'] = wrapString(uattr.sendingDate, 8, True)
    unit_attributes['sending_time'] = wrapString(uattr.sendingTime, 6, True)
    return unit_attributes

cdef wrapStructure(RFC_TYPE_DESC_HANDLE typeDesc, RFC_STRUCTURE_HANDLE container, config):
    cdef unsigned i, fieldCount
    cdef RFC_FIELD_DESC fieldDesc
    RfcGetFieldCount(typeDesc, &fieldCount, NULL)
    result = {}
    for i in range(fieldCount):
        RfcGetFieldDescByIndex(typeDesc, i, &fieldDesc, NULL)
        result[wrapString(fieldDesc.name)] = wrapVariable(
                fieldDesc.type,
                container,
                fieldDesc.name,
                fieldDesc.nucLength,
                fieldDesc.typeDescHandle,
                config
            )
    if len(result) == 1:
        if '' in result:
            result = result['']
    return result

# # Used for debugging tables, cf. wrapTable()
# cdef class TableCursor:
#
#    cdef RFC_TYPE_DESC_HANDLE typeDesc
#    cdef RFC_TABLE_HANDLE container
#
#    def __getitem__(self, i):
#        cdef RFC_ERROR_INFO errorInfo
#        RfcMoveTo(self.container, i, &errorInfo)
#        return wrapStructure(self.typeDesc, self.container)

cdef wrapTable(RFC_TYPE_DESC_HANDLE typeDesc, RFC_TABLE_HANDLE container, config):
    cdef RFC_ERROR_INFO errorInfo
    cdef unsigned rowCount
    # # For debugging in tables (cf. class TableCursor)
    # tc = TableCursor()
    # tc.typeDesc = typeDesc
    # tc.container = container
    # return tc
    RfcGetRowCount(container, &rowCount, &errorInfo)
    table = [None] * rowCount
    while rowCount > 0:
        rowCount -= 1
        RfcMoveTo(container, rowCount, &errorInfo)
        table[rowCount] = wrapStructure(typeDesc, container, config)
        RfcDeleteCurrentRow(container, &errorInfo)
    return table

cdef wrapVariable(
            RFCTYPE typ,
            RFC_FUNCTION_HANDLE container,
            SAP_UC* cName,
            unsigned cLen,
            RFC_TYPE_DESC_HANDLE typeDesc,
            config
        ):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    cdef RFC_STRUCTURE_HANDLE structure
    cdef RFC_TABLE_HANDLE table
    cdef RFC_CHAR* charValue
    cdef SAP_UC* stringValue
    cdef RFC_NUM* numValue
    cdef SAP_RAW* byteValue
    cdef RFC_FLOAT floatValue
    cdef RFC_INT intValue
    cdef RFC_INT1 int1Value
    cdef RFC_INT2 int2Value
    cdef RFC_INT8 int8Value
    cdef RFC_DATE dateValue
    cdef RFC_TIME timeValue
    cdef unsigned resultLen, strLen
    if typ == RFCTYPE_STRUCTURE:
        rc = RfcGetStructure(container, cName, &structure, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return wrapStructure(typeDesc, structure, config)
    elif typ == RFCTYPE_TABLE:
        rc = RfcGetTable(container, cName, &table, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return wrapTable(typeDesc, table, config)
    elif typ == RFCTYPE_CHAR:
        charValue = mallocU(cLen)
        try:
            rc = RfcGetChars(container, cName, charValue, cLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return wrapString(charValue, cLen, config & _MASK_RSTRIP)
        finally:
            free(charValue)
    elif typ == RFCTYPE_STRING:
        rc = RfcGetStringLength(container, cName, &strLen, &errorInfo)
        try:
            stringValue = mallocU(strLen+1)
            rc = RfcGetString(container, cName, stringValue, strLen+1, &resultLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return wrapString(stringValue, resultLen)
        finally:
            free(stringValue)
    elif typ == RFCTYPE_NUM:
        numValue = mallocU(cLen)
        try:
            rc = RfcGetNum(container, cName, numValue, cLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return wrapString(numValue, cLen)
        finally:
            free(numValue)
    elif typ == RFCTYPE_BYTE:
        byteValue = <SAP_RAW*> malloc(cLen)
        try:
            rc = RfcGetBytes(container, cName, byteValue, cLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return byteValue[:cLen]
        finally:
            free(byteValue)
    elif typ == RFCTYPE_XSTRING:
        rc = RfcGetStringLength(container, cName, &strLen, &errorInfo)
        try:
            byteValue = <SAP_RAW*> malloc(strLen+1)
            byteValue[strLen] = 0
            rc = RfcGetXString(container, cName, byteValue, strLen, &resultLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return byteValue[:resultLen]
        finally:
            free(byteValue)
    elif typ == RFCTYPE_BCD:
        # An upper bound for the length of the _string representation_
        # of the BCD is given by (2*cLen)-1 (each digit is encoded in 4bit,
        # the first 4 bit are reserved for the sign)
        # Furthermore, a sign char, a decimal separator char may be present
        # => (2*cLen)+1
        strLen = 2*cLen + 1
        try:
            stringValue = mallocU(strLen+1)
            rc = RfcGetString(container, cName, stringValue, strLen+1, &resultLen, &errorInfo)
            if rc == 23:  # Buffer too small, use returned requried result length
                # print("Warning: Buffer for BCD (cLen={}, buffer={}) too small: "
                #      "trying with {}".format(cLen, strLen, resultLen))
                free(stringValue)
                strLen = resultLen
                stringValue = mallocU(strLen+1)
                rc = RfcGetString(container, cName, stringValue, strLen+1, &resultLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return Decimal(wrapString(stringValue, -1, config & _MASK_RSTRIP))
        finally:
            free(stringValue)
    elif typ == RFCTYPE_DECF16 or typ == RFCTYPE_DECF34:
        # An upper bound for the length of the _string representation_
        # of the DECF is given by (2*cLen)-1 (each digit is encoded in 4bit,
        # the first 4 bit are reserved for the sign)
        # Furthermore, a sign char, a decimal separator char may be present
        # => (2*cLen)+1
        # and exponent char, sign and exponent
        # => +9
        strLen = 2*cLen + 10
        try:
            stringValue = mallocU(strLen+1)
            rc = RfcGetString(container, cName, stringValue, strLen+1, &resultLen, &errorInfo)
            if rc == 23:  # Buffer too small, use returned requried result length
                # print("Warning: Buffer for DECF (cLen={}, buffer={}) too small: "
                #      "trying with {}".format(cLen, strLen, resultLen))
                free(stringValue)
                strLen = resultLen
                stringValue = mallocU(strLen+1)
                rc = RfcGetString(container, cName, stringValue, strLen+1, &resultLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            return Decimal(wrapString(stringValue, -1, config & _MASK_RSTRIP))
        finally:
            free(stringValue)
    elif typ == RFCTYPE_FLOAT:
        rc = RfcGetFloat(container, cName, &floatValue, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return floatValue
    elif typ == RFCTYPE_INT:
        rc = RfcGetInt(container, cName, &intValue, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return intValue
    elif typ == RFCTYPE_INT1:
        rc = RfcGetInt1(container, cName, &int1Value, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return int1Value
    elif typ == RFCTYPE_INT2:
        rc = RfcGetInt2(container, cName, &int2Value, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return int2Value
    elif typ == RFCTYPE_INT8:
        rc = RfcGetInt8(container, cName, &int8Value, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        return int8Value
    elif typ == RFCTYPE_UTCLONG:
        # rc = RfcGetStringLength(container, cName, &strLen, &errorInfo)
        strLen = 27  # is fixed
        try:
            stringValue = mallocU(strLen+1)
            # textual representation from NWRFC SDK because clients' systems unlikely support nanoseconds
            rc = RfcGetString(container, cName, stringValue, strLen+1, &resultLen, &errorInfo)
            if rc != RFC_OK:
                raise wrapError(&errorInfo)
            utcValue = wrapString(stringValue, resultLen)
            # replace the "," separator with "."
            return utcValue[:19]+'.'+utcValue[20:]
        finally:
            free(stringValue)
    elif typ == RFCTYPE_DATE:
        rc = RfcGetDate(container, cName, dateValue, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        value = wrapString(dateValue, 8)
        # return date or None
        if config & _MASK_DTIME:
            if (value == '00000000') or not value:
                return None
            return datetime.strptime(value, '%Y%m%d').date()
        # return date string or ''
        if (value == '00000000') or not value:
            return ''
        return value
    elif typ == RFCTYPE_TIME:
        rc = RfcGetTime(container, cName, timeValue, &errorInfo)
        if rc != RFC_OK:
            raise wrapError(&errorInfo)
        value = wrapString(timeValue, 6)
        # return time or None
        if config & _MASK_DTIME:
            if not value:
                return None
            return datetime.strptime(value, '%H%M%S').time()
        # return time string or ''
        if not value:
            return ''
        return value
    else:
        raise RFCError('Unknown RFC type %d when wrapping %s' % (typ, wrapString(cName)))

cdef wrapError(RFC_ERROR_INFO* errorInfo):
    group2error = {
            ABAP_APPLICATION_FAILURE: ABAPApplicationError,
            ABAP_RUNTIME_FAILURE: ABAPRuntimeError,
            LOGON_FAILURE: LogonError,
            COMMUNICATION_FAILURE: CommunicationError,
            EXTERNAL_RUNTIME_FAILURE: ExternalRuntimeError,
            EXTERNAL_APPLICATION_FAILURE: ExternalApplicationError,
            EXTERNAL_AUTHORIZATION_FAILURE: ExternalAuthorizationError
        }
    error = group2error[errorInfo.group]
    return error(
            wrapString(errorInfo.message), errorInfo.code, wrapString(errorInfo.key),
            wrapString(errorInfo.abapMsgClass), wrapString(errorInfo.abapMsgType), wrapString(errorInfo.abapMsgNumber),
            wrapString(errorInfo.abapMsgV1), wrapString(errorInfo.abapMsgV2),
            wrapString(errorInfo.abapMsgV3), wrapString(errorInfo.abapMsgV4)
        )

cdef wrapString(const SAP_UC* uc, uclen=-1, rstrip=False):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    if uclen == -1:
        uclen = strlenU(uc)
    if uclen == 0:
        return ''
    cdef unsigned utf8_size = uclen * 5 + 1
    cdef char *utf8 = <char*> malloc(utf8_size)
    utf8[0] = 0
    cdef unsigned result_len = 0
    rc = RfcSAPUCToUTF8(uc, uclen, <RFC_BYTE*> utf8, &utf8_size, &result_len, &errorInfo)
    if rc != RFC_OK:
        # raise wrapError(&errorInfo)
        raise RFCError('wrapString uclen: %u utf8_size: %u' % (uclen, utf8_size))
    utf8[result_len] = 0
    try:
        if rstrip:
            return utf8[:result_len].rstrip().decode()
        else:
            return utf8[:result_len].decode()
    finally:
        free(utf8)

cdef wrapString(SAP_UC* uc, uclen=-1, rstrip=True):
    cdef RFC_RC rc
    cdef RFC_ERROR_INFO errorInfo
    if uclen == -1:
        uclen = strlenU(uc)
    if uclen == 0:
        return ''
    cdef unsigned utf8_size = uclen * 5 + 1
    cdef char *utf8 = <char*> malloc(utf8_size)
    utf8[0] = 0
    cdef unsigned result_len = 0
    rc = RfcSAPUCToUTF8(uc, uclen, <RFC_BYTE*> utf8, &utf8_size, &result_len, &errorInfo)
    if rc != RFC_OK:
        # raise wrapError(&errorInfo)
        raise RFCError('wrapString uclen: %u utf8_size: %u' % (uclen, utf8_size))
    utf8[result_len] = 0
    try:
        if rstrip:
            return utf8[:result_len].rstrip().decode()
        else:
            return utf8[:result_len].decode()
    finally:
        free(utf8)
