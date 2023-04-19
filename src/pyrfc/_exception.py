# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

""" :mod:`pyrfc`-specific exception classes
"""


class RFCError(Exception):
    """Exception base class

    Indicates that there was an error in the Python connector.
    """

    pass


class RFCLibError(RFCError):
    """RFC library error

    Base class for exceptions raised by the local underlying C connector (sapnwrfc.c).
    """

    def __init__(
        self,
        message=None,
        code=None,
        key=None,
        msg_class=None,
        msg_type=None,
        msg_number=None,
        msg_v1=None,
        msg_v2=None,
        msg_v3=None,
        msg_v4=None,
    ):
        super(RFCLibError, self).__init__(message)
        self.message = message  # Exception.message removed in Py3
        self.code = code
        self.key = key
        self.msg_class = msg_class
        self.msg_type = msg_type
        self.msg_number = msg_number
        self.msg_v1 = msg_v1
        self.msg_v2 = msg_v2
        self.msg_v3 = msg_v3
        self.msg_v4 = msg_v4

    def __str__(self):
        code = 28 if self.code is None else self.code
        rc_text = RFC_RC(code) if code in [item.value for item in RFC_RC] else "???"
        return (
            f"{rc_text} (rc={self.code}): key={self.key}, message={self.message}"
            f" [MSG: class={self.msg_class}, type={self.msg_type}, number={self.msg_number},"
            f" v1-4:={self.msg_v1};{self.msg_v2};{self.msg_v3};{self.msg_v4}]"
        )


class ABAPApplicationError(RFCLibError):
    """ABAP application error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    ABAP_APPLICATION_FAILURE.
    """

    pass


class ABAPRuntimeError(RFCLibError):
    """ABAP runtime error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    ABAP_RUNTIME_FAILURE.
    """

    pass


class LogonError(RFCLibError):
    """Logon error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    LOGON_FAILURE.
    """

    def __init__(
        self,
        message=None,
        code=2,
        key="RFC_LOGON_FAILURE",
        msg_class=None,
        msg_type=None,
        msg_number=None,
        msg_v1=None,
        msg_v2=None,
        msg_v3=None,
        msg_v4=None,
    ):
        # Setting default values allows for raising an error with one parameter.
        super(LogonError, self).__init__(
            message,
            code,
            key,
            msg_class,
            msg_type,
            msg_number,
            msg_v1,
            msg_v2,
            msg_v3,
            msg_v4,
        )


class CommunicationError(RFCLibError):
    """Communication error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    COMMUNICATION_FAILURE.
    """

    pass


class ExternalRuntimeError(RFCLibError):
    """External runtime error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    EXTERNAL_RUNTIME_FAILURE.
    """

    pass


class ExternalApplicationError(RFCLibError):
    """External application error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    EXTERNAL_APPLICATION_FAILURE.
    """

    pass


class ExternalAuthorizationError(RFCLibError):
    """External authorization error

    This exception is raised if a RFC call returns an RC code greater than 0
    and the error object has an RFC_ERROR_GROUP value of
    EXTERNAL_AUTHORIZATION_FAILURE.
    """

    pass


class RFCTypeError(RFCLibError):
    """Type concersion error

    This exception is raised when invalid data type detected in RFC input (fill) conversion
    and the error object has an RFC_ERROR_GROUP value of
    RFC_TYPE_ERROR
    """

    pass
