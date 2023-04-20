from datetime import date, time, datetime
from decimal import Decimal

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
