from . csapnwrfc cimport *

cdef RFC_RC genericHandler (RFC_CONNECTION_HANDLE rfcHandle, RFC_FUNCTION_HANDLE funcHandle, RFC_ERROR_INFO* serverErrorInfo):
    return RFC_OK

cdef RFC_RC metadataLookup(const SAP_UC* functionName, RFC_ATTRIBUTES rfcAttributes, RFC_FUNCTION_DESC_HANDLE *funcDescHandle):
    return RFC_OK


cdef RFC_RC stest():
    cdef RFC_ERROR_INFO errorInfo
    RFC_RC = RfcInstallGenericServerFunction(genericHandler, metadataLookup, &errorInfo)
    return RFC_OK
