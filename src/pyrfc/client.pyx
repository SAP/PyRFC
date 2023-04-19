from collections.abc import Iterable
from sys import platform
from threading import Timer

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
