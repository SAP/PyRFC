from sys import exc_info
from threading import Thread
import socket

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
