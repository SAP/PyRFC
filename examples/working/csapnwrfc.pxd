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

    ctypedef SAP_UC* const_SAP_UC_ptr "const SAP_UC*"

    enum:  RFC_TID_LN
    ctypedef SAP_UC RFC_TID[RFC_TID_LN+1]
    enum:  RFC_UNITID_LN
    ctypedef SAP_UC RFC_UNITID[RFC_UNITID_LN+1]

    ctypedef enum RFCTYPE:
        RFCTYPE_CHAR
        RFCTYPE_DATE
        RFCTYPE_BCD
        RFCTYPE_DECF16
        RFCTYPE_DECF34
        RFCTYPE_TIME
        RFCTYPE_BYTE
        RFCTYPE_TABLE
        RFCTYPE_NUM
        RFCTYPE_FLOAT
        RFCTYPE_INT
        RFCTYPE_INT2
        RFCTYPE_INT1
        RFCTYPE_INT8
        RFCTYPE_STRUCTURE
        RFCTYPE_STRING
        RFCTYPE_XSTRING
        RFCTYPE_UTCLONG

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
        RFC_IMPORT   = 0x01
        RFC_EXPORT   = 0x02
        RFC_CHANGING = RFC_IMPORT | RFC_EXPORT
        RFC_TABLES   = 0x04 | RFC_CHANGING

    ctypedef void* RFC_FUNCTION_DESC_HANDLE
    ctypedef void* RFC_FUNCTION_HANDLE
    ctypedef void* RFC_TYPE_DESC_HANDLE
    ctypedef void* DATA_CONTAINER_HANDLE
    ctypedef DATA_CONTAINER_HANDLE RFC_STRUCTURE_HANDLE
    ctypedef DATA_CONTAINER_HANDLE RFC_TABLE_HANDLE
    ctypedef void* RFC_CONNECTION_HANDLE
    ctypedef void* RFC_TRANSACTION_HANDLE
    ctypedef void* RFC_UNIT_HANDLE
    ctypedef void* RFC_METADATA_QUERY_RESULT_HANDLE
    ctypedef void* RFC_THROUGHPUT_HANDLE

    ctypedef struct RFC_CONNECTION_PARAMETER:
        SAP_UC* name
        SAP_UC* value

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
        void* extendedDescription

    ctypedef struct RFC_FIELD_DESC:
        RFC_ABAP_NAME   name
        RFCTYPE         type
        unsigned        nucLength
        unsigned        nucOffset
        unsigned        ucLength
        unsigned        ucOffset
        unsigned        decimals
        RFC_TYPE_DESC_HANDLE typeDescHandle
        void* extendedDescription

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

    ctypedef struct RFC_UNIT_IDENTIFIER:
        SAP_UC unitType
        RFC_UNITID unitID

    ctypedef enum RFC_UNIT_STATE:
        RFC_UNIT_NOT_FOUND
        RFC_UNIT_IN_PROCESS
        RFC_UNIT_COMMITTED
        RFC_UNIT_ROLLED_BACK
        RFC_UNIT_CONFIRMED

    ctypedef (RFC_RC)RFC_SERVER_FUNCTION(RFC_CONNECTION_HANDLE, RFC_FUNCTION_HANDLE, RFC_ERROR_INFO *)
    ctypedef (RFC_RC)RFC_FUNC_DESC_CALLBACK(SAP_UC *, RFC_ATTRIBUTES, RFC_FUNCTION_DESC_HANDLE *)
    RFC_RC RfcInstallGenericServerFunction(RFC_SERVER_FUNCTION serverFunction, RFC_FUNC_DESC_CALLBACK funcDescProvider, RFC_ERROR_INFO* errorInfo)