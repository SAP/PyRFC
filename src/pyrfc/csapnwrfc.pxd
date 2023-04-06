# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

cdef extern from "sapnwrfc.h":
    ctypedef unsigned short SAP_UC
    ctypedef unsigned short SAP_CHAR
    ctypedef unsigned short SAP_USHORT
    ctypedef SAP_USHORT SAP_UTF16
    ctypedef unsigned long long SAP_ULLONG
    # size_t strlenU(SAP_UC*)
    unsigned strlenU(SAP_UC*)
    SAP_CHAR *mallocU(size_t)
    void *malloc(size_t)
    void free(void*)
    void *memcpy(void*, void*, size_t)
    void strncpyU(SAP_UTF16*, SAP_UTF16*, size_t)
    void memsetR(void*, unsigned short, size_t)
    # size_t sizeofR(par)

    ctypedef unsigned char SAP_RAW
    ctypedef SAP_RAW RFC_BYTE
    ctypedef SAP_UC RFC_CHAR
    ctypedef RFC_CHAR RFC_NUM
    ctypedef SAP_RAW RFC_INT1
    ctypedef short RFC_INT2
    ctypedef int RFC_INT
    ctypedef long long RFC_INT8
    ctypedef double RFC_FLOAT
    ctypedef RFC_CHAR RFC_DATE[8]
    ctypedef RFC_CHAR RFC_TIME[6]
    ctypedef RFC_CHAR RFC_ABAP_NAME[30+1]
    ctypedef RFC_CHAR RFC_PARAMETER_DEFVALUE[30+1]
    ctypedef RFC_CHAR RFC_PARAMETER_TEXT[79+1]

    ctypedef SAP_UC *const_SAP_UC_ptr "const SAP_UC*"

    enum:  RFC_TID_LN
    ctypedef SAP_UC RFC_TID[RFC_TID_LN+1]
    enum:  RFC_UNITID_LN
    ctypedef SAP_UC RFC_UNITID[RFC_UNITID_LN+1]

    ctypedef enum RFCTYPE:
        RFCTYPE_CHAR
        RFCTYPE_DATE
        RFCTYPE_BCD
        RFCTYPE_TIME
        RFCTYPE_BYTE
        RFCTYPE_TABLE
        RFCTYPE_NUM
        RFCTYPE_FLOAT
        RFCTYPE_INT
        RFCTYPE_INT2
        RFCTYPE_INT1
        RFCTYPE_NULL
        RFCTYPE_ABAPOBJECT
        RFCTYPE_STRUCTURE
        RFCTYPE_DECF16
        RFCTYPE_DECF34
        RFCTYPE_XMLDATA
        RFCTYPE_STRING
        RFCTYPE_XSTRING
        RFCTYPE_INT8		    # 8-byte integer
        RFCTYPE_UTCLONG         # timestamp/long, 8-byte integer
        RFCTYPE_UTCSECOND       # timestamp/second, 8-byte integer
        RFCTYPE_UTCMINUTE       # timestamp/minute, 8-byte integer
        RFCTYPE_DTDAY		    # date/day , 4-byte integer
        RFCTYPE_DTWEEK          # date/week, 4-byte integer
        RFCTYPE_DTMONTH         # date/month, 4-byte integer
        RFCTYPE_TSECOND         # time/second, 4-byte integer
        RFCTYPE_TMINUTE         # time/minute, 2-byte integer
        RFCTYPE_CDAY            # calendar day, 2-byte integer

    ctypedef enum RFC_RC:
        RFC_OK
        RFC_COMMUNICATION_FAILURE
        RFC_LOGON_FAILURE
        RFC_ABAP_RUNTIME_FAILURE
        RFC_ABAP_MESSAGE
        RFC_ABAP_EXCEPTION
        RFC_CLOSED
        RFC_CANCELED
        RFC_TIMEOUT
        RFC_MEMORY_INSUFFICIENT
        RFC_VERSION_MISMATCH
        RFC_INVALID_PROTOCOL
        RFC_SERIALIZATION_FAILURE
        RFC_INVALID_HANDLE
        RFC_RETRY
        RFC_EXTERNAL_FAILURE
        RFC_EXECUTED
        RFC_NOT_FOUND
        RFC_NOT_SUPPORTED
        RFC_ILLEGAL_STATE
        RFC_INVALID_PARAMETER
        RFC_CODEPAGE_CONVERSION_FAILURE
        RFC_CONVERSION_FAILURE
        RFC_BUFFER_TOO_SMALL
        RFC_TABLE_MOVE_BOF
        RFC_TABLE_MOVE_EOF
        RFC_START_SAPGUI_FAILURE
        RFC_ABAP_CLASS_EXCEPTION
        RFC_UNKNOWN_ERROR
        RFC_AUTHORIZATION_FAILURE
        RFC_AUTHENTICATION_FAILURE
        RFC_CRYPTOLIB_FAILURE
        RFC_IO_FAILURE
        RFC_LOCKING_FAILURE

    ctypedef enum RFC_ERROR_GROUP:
        OK
        ABAP_APPLICATION_FAILURE
        ABAP_RUNTIME_FAILURE
        LOGON_FAILURE
        COMMUNICATION_FAILURE
        EXTERNAL_RUNTIME_FAILURE
        EXTERNAL_APPLICATION_FAILURE
        EXTERNAL_AUTHORIZATION_FAILURE

    ctypedef enum RFC_DIRECTION:
        RFC_IMPORT = 0x01
        RFC_EXPORT = 0x02
        RFC_CHANGING = RFC_IMPORT | RFC_EXPORT
        RFC_TABLES = 0x04 | RFC_CHANGING

    ctypedef struct RFC_UNIT_IDENTIFIER:
        SAP_UC unitType
        RFC_UNITID unitID

    ctypedef enum RFC_CALL_TYPE:
        RFC_SYNCHRONOUS
        RFC_TRANSACTIONAL
        RFC_QUEUED
        RFC_BACKGROUND_UNIT

    ctypedef void *RFC_FUNCTION_DESC_HANDLE
    ctypedef void *RFC_FUNCTION_HANDLE
    ctypedef void *RFC_TYPE_DESC_HANDLE
    ctypedef void *DATA_CONTAINER_HANDLE
    ctypedef DATA_CONTAINER_HANDLE RFC_STRUCTURE_HANDLE
    ctypedef DATA_CONTAINER_HANDLE RFC_TABLE_HANDLE
    ctypedef void *RFC_CONNECTION_HANDLE
    ctypedef void *RFC_TRANSACTION_HANDLE
    ctypedef void *RFC_UNIT_HANDLE
    ctypedef void *RFC_METADATA_QUERY_RESULT_HANDLE
    ctypedef void *RFC_THROUGHPUT_HANDLE
    ctypedef void *RFC_SERVER_HANDLE
    ctypedef (RFC_RC)RFC_SERVER_FUNCTION(RFC_CONNECTION_HANDLE, RFC_FUNCTION_HANDLE, RFC_ERROR_INFO *) with gil
    ctypedef (RFC_RC)RFC_FUNC_DESC_CALLBACK(SAP_UC *, RFC_ATTRIBUTES, RFC_FUNCTION_DESC_HANDLE *) with gil
    ctypedef (RFC_RC)RFC_ON_CHECK_UNIT(RFC_CONNECTION_HANDLE, RFC_UNIT_IDENTIFIER*) with gil
    ctypedef (RFC_RC)RFC_ON_COMMIT_UNIT(RFC_CONNECTION_HANDLE, RFC_UNIT_IDENTIFIER *) with gil
    ctypedef (RFC_RC)RFC_ON_ROLLBACK_UNIT(RFC_CONNECTION_HANDLE, RFC_UNIT_IDENTIFIER *) with gil
    ctypedef (RFC_RC)RFC_ON_CONFIRM_UNIT(RFC_CONNECTION_HANDLE, RFC_UNIT_IDENTIFIER *) with gil
    ctypedef (RFC_RC)RFC_ON_GET_UNIT_STATE(RFC_CONNECTION_HANDLE, RFC_UNIT_IDENTIFIER*, RFC_UNIT_STATE*) with gil

    ctypedef struct RFC_CONNECTION_PARAMETER:
        SAP_UC *name
        SAP_UC *value

    ctypedef struct RFC_ERROR_INFO:
        RFC_RC code
        RFC_ERROR_GROUP group
        SAP_UC key[128]
        SAP_UC message[512]
        SAP_UC abapMsgClass[20+1]
        SAP_UC abapMsgType[1+1]
        RFC_NUM abapMsgNumber[3+1]
        SAP_UC abapMsgV1[50+1]
        SAP_UC abapMsgV2[50+1]
        SAP_UC abapMsgV3[50+1]
        SAP_UC abapMsgV4[50+1]

    ctypedef struct RFC_PARAMETER_DESC:
        RFC_ABAP_NAME   name
        RFC_DIRECTION   direction
        RFCTYPE         type
        unsigned        nucLength
        unsigned        ucLength
        unsigned        decimals
        RFC_TYPE_DESC_HANDLE typeDescHandle
        RFC_PARAMETER_DEFVALUE defaultValue
        RFC_PARAMETER_TEXT parameterText
        RFC_BYTE     optional
        void *extendedDescription

    ctypedef struct RFC_FIELD_DESC:
        RFC_ABAP_NAME   name
        RFCTYPE         type
        unsigned        nucLength
        unsigned        nucOffset
        unsigned        ucLength
        unsigned        ucOffset
        unsigned        decimals
        RFC_TYPE_DESC_HANDLE typeDescHandle
        void *extendedDescription

    ctypedef struct RFC_ATTRIBUTES:
        SAP_UC dest[64+1]
        SAP_UC host[100+1]
        SAP_UC partnerHost[100+1]
        SAP_UC sysNumber[2+1]
        SAP_UC sysId[8+1]
        SAP_UC client[3+1]
        SAP_UC user[12+1]
        SAP_UC language[2+1]
        SAP_UC trace[1+1]
        SAP_UC isoLanguage[2+1]
        SAP_UC codepage[4+1]
        SAP_UC partnerCodepage[4+1]
        SAP_UC rfcRole[1+1]
        SAP_UC type[1+1]
        SAP_UC partnerType[1+1]
        SAP_UC rel[4+1]
        SAP_UC partnerRel[4+1]
        SAP_UC kernelRel[4+1]
        SAP_UC cpicConvId[8 + 1]
        SAP_UC progName[128+1]
        SAP_UC partnerBytesPerChar[1+1]
        SAP_UC partnerSystemCodepage[4 + 1]
        SAP_UC partnerIP[15 + 1]
        SAP_UC partnerIPv6[45 + 1]
        SAP_UC reserved[17]

    ctypedef enum RFC_PROTOCOL_TYPE:
        RFC_UNKOWN
        RFC_CLIENT
        RFC_STARTED_SERVER
        RFC_REGISTERED_SERVER
        RFC_MULTI_COUNT_REGISTERED_SERVER
        RFC_TCP_SOCKET_CLIENT
        RFC_TCP_SOCKET_SERVER
        RFC_WEBSOCKET_CLIENT
        RFC_WEBSOCKET_SERVER
        RFC_PROXY_WEBSOCKET_CLIENT

    ctypedef enum RFC_SERVER_STATE:
        RFC_SERVER_INITIAL
        RFC_SERVER_STARTING
        RFC_SERVER_RUNNING
        RFC_SERVER_BROKEN
        RFC_SERVER_STOPPING
        RFC_SERVER_STOPPED

    ctypedef struct RFC_SERVER_ATTRIBUTES:
        SAP_UC *serverName
        RFC_PROTOCOL_TYPE type
        unsigned registrationCount
        RFC_SERVER_STATE state
        unsigned currentBusyCount
        unsigned peakBusyCount

    ctypedef struct RFC_UNIT_ATTRIBUTES:
        short kernelTrace
        short satTrace
        short unitHistory
        short lock
        short noCommitCheck
        SAP_UC user[12+1]
        SAP_UC client[3+1]
        SAP_UC tCode[20+1]
        SAP_UC program[40+1]
        SAP_UC hostname[40+1]
        RFC_DATE sendingDate
        RFC_TIME sendingTime

    ctypedef enum RFC_UNIT_STATE:
        RFC_UNIT_NOT_FOUND
        RFC_UNIT_IN_PROCESS
        RFC_UNIT_COMMITTED
        RFC_UNIT_ROLLED_BACK
        RFC_UNIT_CONFIRMED

    ctypedef struct RFC_SERVER_CONTEXT:
        # Specifies the type of function call. Depending on the value of this field, some of the other fields of this struct may be filled.
        RFC_CALL_TYPE type
        # If type is RFC_TRANSACTIONAL or RFC_QUEUED, this field is filled with the 24 digit TID of the tRFC/qRFC unit.
        RFC_TID tid
        # If type is RFC_BACKGROUND_UNIT, this pointer is set to the unit identifier of the LUW.
        # Note: the pointer is valid only during the execution context of your server function.
        RFC_UNIT_IDENTIFIER* unitIdentifier
        # If type is RFC_BACKGROUND_UNIT, this pointer is set to the unit attributes of the LUW.
        # Note: the pointer is valid only during the execution context of your server function.
        RFC_UNIT_ATTRIBUTES* unitAttributes
        # Specifies whether the current server connection is processing stateful RFC requests
        # (assigned permanently to one fixed ABAP user session).
        unsigned isStateful
        # Contains a unique zero-terminated session ID, identifying the ABAP or external user session.
        # Can be used in stateful servers to store session context in a hashmap.
        SAP_UC sessionID[33]

    RFC_RC RfcIsConnectionHandleValid(RFC_CONNECTION_HANDLE rfcHandle, RFC_INT *isValid, RFC_ERROR_INFO *errorInfo) nogil
    RFC_CONNECTION_HANDLE RfcOpenConnection(RFC_CONNECTION_PARAMETER *connectionParams, unsigned paramCount, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcCloseConnection(RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcCancel(RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcGetServerContext(RFC_CONNECTION_HANDLE rfcHandle, RFC_SERVER_CONTEXT *context, RFC_ERROR_INFO *errorInfo)	nogil
    RFC_RC RfcResetServerContext(RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcPing(RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcListenAndDispatch (RFC_CONNECTION_HANDLE rfcHandle, int timeout, RFC_ERROR_INFO *errorInfo)
    RFC_FUNCTION_DESC_HANDLE RfcGetFunctionDesc(RFC_CONNECTION_HANDLE rfcHandle, SAP_UC *funcName, RFC_ERROR_INFO *errorInfo)
    RFC_FUNCTION_HANDLE RfcCreateFunction(RFC_FUNCTION_DESC_HANDLE funcDescHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDestroyFunction(RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcInvoke(RFC_CONNECTION_HANDLE rfcHandle, RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcSetParameterActive(RFC_FUNCTION_HANDLE funcHandle, SAP_UC *paramName, int isActive, RFC_ERROR_INFO *errorInfo)

    SAP_UC *RfcGetVersion(unsigned *majorVersion, unsigned *minorVersion, unsigned *patchLevel)

    SAP_UC *RfcGetRcAsString(RFC_RC rc)
    SAP_UC *RfcGetTypeAsString(RFCTYPE type)
    SAP_UC *RfcGetDirectionAsString(RFC_DIRECTION direction)
    RFC_RC RfcGetChars(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_CHAR *charBuffer, unsigned bufferLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetNum(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_NUM *charBuffer, unsigned bufferLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetBytes(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, SAP_RAW *byteBuffer, unsigned bufferLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetXString(
                DATA_CONTAINER_HANDLE dataHandle,
                SAP_UC *name,
                SAP_RAW *byteBuffer,
                unsigned bufferLength,
                unsigned *xstringLength,
                RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetString(
                DATA_CONTAINER_HANDLE dataHandle,
                SAP_UC *name,
                SAP_UC *stringBuffer,
                unsigned bufferLength,
                unsigned *stringLength,
                RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetFloat(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_FLOAT *value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetInt(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_INT *value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetInt1(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_INT1 *value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetInt2(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_INT2 *value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetInt8(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_INT8 *value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetDate(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_DATE emptyDate, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetTime(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_TIME emptyTime, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetStringLength(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, unsigned *stringLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetChars(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_CHAR *charValue, unsigned valueLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetBytes(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, SAP_RAW *byteValue, unsigned valueLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetXString(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, SAP_RAW *byteValue, unsigned valueLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetNum(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, SAP_UC *stringValue, unsigned valueLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetString(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, SAP_UC *stringValue, unsigned valueLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetFloat(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_FLOAT value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetInt(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_INT value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetInt8(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_INT8 value, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetDate(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_DATE date, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetTime(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_TIME time, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetStructure(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_STRUCTURE_HANDLE *structHandle, RFC_ERROR_INFO *errorInfo)

    RFC_CONNECTION_HANDLE RfcCreateServer(RFC_CONNECTION_PARAMETER *connectionParams, unsigned paramCount, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcLaunchServer(RFC_SERVER_HANDLE serverHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcInstallGenericServerFunction(RFC_SERVER_FUNCTION serverFunction, RFC_FUNC_DESC_CALLBACK funcDescProvider, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcShutdownServer(RFC_SERVER_HANDLE serverHandle, unsigned timeout, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcDestroyServer(RFC_SERVER_HANDLE serverHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcGetServerAttributes(RFC_SERVER_HANDLE serverHandle, RFC_SERVER_ATTRIBUTES *serverAttributes, RFC_ERROR_INFO *errorInfo) nogil
    SAP_UC *RfcGetServerStateAsString(RFC_SERVER_STATE serverState)

    RFC_FUNCTION_DESC_HANDLE RfcDescribeFunction(RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO *errorInfo)

    RFC_TYPE_DESC_HANDLE RfcCreateTypeDesc(SAP_UC *name, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcAddTypeField(RFC_TYPE_DESC_HANDLE typeHandle, RFC_FIELD_DESC *fieldDescr, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetTypeLength(RFC_TYPE_DESC_HANDLE typeHandle, unsigned nucByteLength, unsigned ucByteLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetTypeName(RFC_TYPE_DESC_HANDLE typeHandle, RFC_ABAP_NAME bufferForName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetFieldCount(RFC_TYPE_DESC_HANDLE typeHandle, unsigned *count, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetFieldDescByIndex(RFC_TYPE_DESC_HANDLE typeHandle, unsigned index, RFC_FIELD_DESC *fieldDescr, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetFieldDescByName(RFC_TYPE_DESC_HANDLE typeHandle, SAP_UC *name, RFC_FIELD_DESC *fieldDescr, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetTypeLength(RFC_TYPE_DESC_HANDLE typeHandle, unsigned *nucByteLength, unsigned *ucByteLength, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDestroyTypeDesc(RFC_TYPE_DESC_HANDLE typeHandle, RFC_ERROR_INFO *errorInfo)
    RFC_TYPE_DESC_HANDLE RfcGetTypeDesc(RFC_CONNECTION_HANDLE rfcHandle, SAP_UC *typeName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcRemoveTypeDesc(SAP_UC *repositoryID, SAP_UC *typeName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcMetadataBatchQuery(
        RFC_CONNECTION_HANDLE rfcHandle,
        const SAP_UC **functionNames,
        unsigned functionCount,
        const SAP_UC **typeNames,
        unsigned typeCount,
        const SAP_UC **classNames,
        unsigned classCount,
        RFC_METADATA_QUERY_RESULT_HANDLE handle,
        RFC_ERROR_INFO *errorInfo)

    RFC_FUNCTION_DESC_HANDLE RfcCreateFunctionDesc(SAP_UC *name, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetFunctionName(RFC_FUNCTION_DESC_HANDLE funcDesc, RFC_ABAP_NAME bufferForName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcAddParameter(RFC_FUNCTION_DESC_HANDLE funcDesc, RFC_PARAMETER_DESC *paramDescr, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetParameterCount(RFC_FUNCTION_DESC_HANDLE funcDesc, unsigned *count, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetParameterDescByIndex(RFC_FUNCTION_DESC_HANDLE funcDesc, unsigned index, RFC_PARAMETER_DESC *paramDesc, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetParameterDescByName(RFC_FUNCTION_DESC_HANDLE funcDesc, SAP_UC *name, RFC_PARAMETER_DESC *paramDesc, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDestroyFunctionDesc(RFC_FUNCTION_DESC_HANDLE funcDesc, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcRemoveFunctionDesc(const SAP_UC *repositoryID, const SAP_UC *functionName, RFC_ERROR_INFO *errorInfo)
    RFC_FUNCTION_DESC_HANDLE RfcGetCachedFunctionDesc(const SAP_UC *repositoryID, const SAP_UC *funcName, RFC_ERROR_INFO *errorInfo)

    RFC_RC RfcGetRowCount(RFC_TABLE_HANDLE tableHandle, unsigned *rowCount, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcMoveTo(RFC_TABLE_HANDLE tableHandle, unsigned index, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDeleteCurrentRow(RFC_TABLE_HANDLE tableHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetTable(DATA_CONTAINER_HANDLE dataHandle, SAP_UC *name, RFC_TABLE_HANDLE *tableHandle, RFC_ERROR_INFO *errorInfo)
    RFC_STRUCTURE_HANDLE RfcAppendNewRow(RFC_TABLE_HANDLE tableHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcUTF8ToSAPUC(
                const unsigned char *utf8,
                unsigned utf8Length,
                SAP_UC *sapuc,
                unsigned *sapucSize,
                unsigned *resultLength,
                RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSAPUCToUTF8(
                const SAP_UC *sapuc,
                unsigned sapucLength,
                RFC_BYTE *utf8,
                unsigned *utf8Size,
                unsigned *resultLength,
                RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetConnectionAttributes(RFC_CONNECTION_HANDLE rfcHandle, RFC_ATTRIBUTES *attr, RFC_ERROR_INFO *errorInfo)

    RFC_RC RfcGetTransactionID(RFC_CONNECTION_HANDLE rfcHandle, RFC_TID tid, RFC_ERROR_INFO *errorInfo)
    RFC_TRANSACTION_HANDLE RfcCreateTransaction(RFC_CONNECTION_HANDLE rfcHandle, RFC_TID tid, SAP_UC *queueName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcInvokeInTransaction(RFC_TRANSACTION_HANDLE tHandle, RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSubmitTransaction(RFC_TRANSACTION_HANDLE tHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcConfirmTransaction(RFC_TRANSACTION_HANDLE tHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDestroyTransaction(RFC_TRANSACTION_HANDLE tHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetUnitID(RFC_CONNECTION_HANDLE rfcHandle, RFC_UNITID uid, RFC_ERROR_INFO *errorInfo)
    RFC_UNIT_HANDLE RfcCreateUnit(
            RFC_CONNECTION_HANDLE rfcHandle,
            RFC_UNITID uid,
            const SAP_UC *queueNames[],
            unsigned queueNameCount,
            RFC_UNIT_ATTRIBUTES *unitAttr,
            RFC_UNIT_IDENTIFIER *identifier,
            RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcInvokeInUnit(RFC_UNIT_HANDLE unitHandle, RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSubmitUnit(RFC_UNIT_HANDLE unitHandle, RFC_ERROR_INFO *errorInfo) nogil
    RFC_RC RfcConfirmUnit(RFC_CONNECTION_HANDLE rfcHandle, RFC_UNIT_IDENTIFIER *identifier, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDestroyUnit(RFC_UNIT_HANDLE unitHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetUnitState(RFC_CONNECTION_HANDLE rfcHandle, RFC_UNIT_IDENTIFIER *identifier, RFC_UNIT_STATE *state, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcInstallBgRfcHandlers(
                const SAP_UC *sysId,
                RFC_ON_CHECK_UNIT onCheckFunction,
                RFC_ON_COMMIT_UNIT onCommitFunction,
                RFC_ON_ROLLBACK_UNIT onRollbackFunction,
                RFC_ON_CONFIRM_UNIT onConfirmFunction,
                RFC_ON_GET_UNIT_STATE onGetStateFunction,
                RFC_ERROR_INFO *errorInfo) nogil

    RFC_THROUGHPUT_HANDLE RfcCreateThroughput(RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcDestroyThroughput (RFC_THROUGHPUT_HANDLE throughput, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetThroughputOnConnection (RFC_CONNECTION_HANDLE rfcHandle, RFC_THROUGHPUT_HANDLE throughput, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcRemoveThroughputFromConnection (RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO *errorInfo)
    RFC_THROUGHPUT_HANDLE RfcGetThroughputFromConnection (RFC_CONNECTION_HANDLE rfcHandle, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcResetThroughput (RFC_THROUGHPUT_HANDLE throughput, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetNumberOfCalls (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *numberOfCalls, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetTotalTime (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *totalTime, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetSerializationTime (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *serializationTime, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetDeserializationTime (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *deserializationTime, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetApplicationTime (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *applicationTime, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetSentBytes (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *sentBytes, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcGetReceivedBytes (RFC_THROUGHPUT_HANDLE throughput, SAP_ULLONG *receivedBytes, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcSetIniPath (const SAP_UC *pathName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcLoadCryptoLibrary (const SAP_UC *pathName, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcReloadIniFile (RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcLanguageIsoToSap (const SAP_UC *laiso, SAP_UC *lang, RFC_ERROR_INFO *errorInfo)
    RFC_RC RfcLanguageSapToIso (const SAP_UC *lang, SAP_UC *laiso, RFC_ERROR_INFO *errorInfo)
