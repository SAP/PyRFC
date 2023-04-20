from locale import localeconv
from os.path import isfile, join
import pickle
from sys import platform
from threading import Thread

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


def enum_names(enum_obj):
    return set(e.name for e in enum_obj)


def enum_values(enum_obj):
    return set(e.value for e in enum_obj)


def py_to_string(obj):
    return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)


def string_to_py(objstr):
    return pickle.loads(objstr)


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
