.. To achieve a printout of the class docstring (for the __init__ method),
   but also information about the methods _with signatures_, we have to use
   .. autoclass: bla (for the class docstring, without auto there is no docstring)
      .. automethod: foo (for the method definitions with (manual) signatures.

.. cf. http://stackoverflow.com/questions/11830242/non-breaking-space

.. |nbsp| unicode:: 0xA0
   :trim:

.. currentmodule:: pyrfc

###################
:mod:`pyrfc`
###################

The :mod:`pyrfc` package.

.. toctree::
   :maxdepth: 2

.. _pyrfcapi:

======================
PyRFC module functions
======================

.. autofunction:: get_nwrfclib_version
.. autofunction:: set_ini_file_directory(path_name)
.. autofunction:: reload_ini_file
.. autofunction:: language_iso_to_sap(lang_iso)
.. autofunction:: language_sap_to_iso(lang_sap)
.. autofunction:: set_cryptolib_path(path_name)
.. autofunction:: set_locale_radix(value=None)
.. autofunction:: cancel_connection(client_connection)

.. _apiconn:

==========
Connection
==========

.. autoclass:: Connection

   .. autoattribute:: alive
   .. autoattribute:: handle
   .. autoattribute:: options
   .. automethod:: get_connection_attributes()
   .. automethod:: open()
   .. automethod:: reopen()
   .. automethod:: call(func_name, options, params)
   .. automethod:: close()
   .. automethod:: cancel()
   .. automethod:: free()
   .. automethod:: ping()
   .. automethod:: reset_server_context()
   .. automethod:: is_valid()
   .. automethod:: initialize_unit([background=True])
   .. automethod:: fill_and_submit_unit(unit, calls[, queue_names=None[, attributes=None]])
   .. automethod:: confirm_unit(unit)
   .. automethod:: destroy_unit(unit)
   .. automethod:: get_unit_state(unit)
   .. automethod:: get_function_description(func_name)
   .. automethod:: type_desc_get(type_name)
   .. automethod:: type_desc_remove(type_name)
   .. automethod:: func_desc_remove(func_name)

.. _apiserver:

==========
Server
==========

.. autoclass:: Server

   .. automethod:: bgrfc_init(sysId, bgRfcFunction)
   .. automethod:: add_function(func_name, callback)
   .. automethod:: serve()
   .. automethod:: start()
   .. automethod:: stop()
   .. automethod:: close()
   .. automethod:: get_server_attributes()

.. _apiconnectionparams:

=====================
Connection Parameters
=====================

.. autoclass:: ConnectionParameters

.. _apifuncdesc:

====================
Function Description
====================

.. note::

   Actually, the FunctionDescription class does not support exceptions.

.. autoclass:: FunctionDescription

   .. automethod:: add_parameter(name, parameter_type, direction, nuc_length, uc_length[, decimals=0[, default_value=""[, parameter_text=""[, optional=False[, type_description=None]]]]])

.. _apitypedesc:

===================
Type Description
===================
.. autoclass:: TypeDescription

   .. automethod:: add_field(name, field_type, nuc_length, uc_length, nuc_offset, uc_offset[, decimals=0[, type_description=None]])

.. _apithrououghput:

==========
Throughput
==========

.. autoclass:: Throughput

   .. autoattribute:: _handle
   .. autoattribute:: connections
   .. autoattribute:: stats
   .. automethod:: setOnConnection()
   .. automethod:: getFromConnection()
   .. automethod:: removeFromConnection()
   .. automethod:: reset()

.. _apierr:

======
Errors
======

If a problem occurs in the Python connector or in an underlying component (e.g.
C connector, SAP system, ABAP code, ...), an exception is raised. The class
of the exception indicates where the problem occurred.

1. ``RFCError``: This error is raised, if a problem occurred in the Python
   connector.
2. ``RFCLibError``: This error is raised, if a problem occurred in the C
   connector.
3. All other errors represent errors with the RFC call to the SAP backend
   system. For these errors, the errorInfo struct of the C connector is wrapped,
   e.g. for a given exception ``e``, the error code is available in ``e.code``.
   The class of the error depends on the group of the error.

.. image:: _static/images/exceptions.*
   :alt: Inheritance of errors: Exception->RFCError->RFCLibError->specific errors
   :align: center
   :scale: 90%
   :name: Inheritance of errors

.. autoexception:: RFCError

.. autoexception:: RFCLibError

.. autoexception:: LogonError

.. autoexception:: CommunicationError

.. autoexception:: ABAPApplicationError

.. autoexception:: ABAPRuntimeError

.. autoexception:: ExternalAuthorizationError

.. autoexception:: ExternalRuntimeError

.. autoexception:: ExternalApplicationError


.. _error-types:

Error types, codes, groups, and classes
=======================================

:ref:`Schmidt and Li (2009a)<c09a>` describe four possible *error types* on
the basis of the return code (i.e. *error code*) of a RFM invocation:

* ABAP exception,
* system failure,
* ABAP messages, and
* communication failure.

However, there are in total roughly 30 possible return codes that indicate some
kind of error. As each error information struct provides an
*error group* information with seven possible groups,
which was taken as the basis for the exception *classes*.

The following table should facilitate the matching between the different
error representations.

======================= =============================== =========================== ====================
type (SPJ)              code [numeric] (C)              group (C)                   class (Python)
======================= =============================== =========================== ====================
ABAP exception          RFC_ABAP_EXCEPTION [5]          ABAP_APPLICATION_FAILURE    ABAPApplicationError
system failure          RFC_ABAP_RUNTIME_FAILURE [3]    ABAP_RUNTIME_FAILURE        ABAPRuntimeError
ABAP message            RFC_ABAP_MESSAGE [4]            ABAP_RUNTIME_FAILURE        ABAPRuntimeError
communication failure   RFC_COMMUNICATION_FAILURE [1]   COMMUNICATION_FAILURE       CommunicationError
\                       RFC_LOGON_FAILURE [2]           LOGON_FAILURE               LogonError
======================= =============================== =========================== ====================
