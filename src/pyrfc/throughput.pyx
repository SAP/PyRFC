
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
