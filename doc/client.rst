.. currentmodule:: pyrfc

.. _client:

===============
Client scenario
===============

In *Client* scenario, Python calls remote enabled ABAP function module (FM) [#f1]_ 
via SAP RFC protocol, as shown in :ref:`intro`. To introduce the functionality, 
we will start with an three :ref:`examples<client-ex>`, then show some
:ref:`details<client-connectionconfig>` of the :class:`Connection`, and finally
cover some :ref:`implementation details<client-tech>`.


.. _client-ex:

Examples
========

To create a connection, construct a :class:`Connection` object and
pass the credentials that should be used to open a connection to an
SAP backend system.

>>> from pyrfc import Connection
>>> conn = Connection(user='me', passwd='secret', ashost='10.0.0.1', sysnr='00', client='100')

For the examples we usually store the logon information in a config document
(`sapnwrfc.cfg`) that is read with `ConfigParser`_. Thus, if the logon information
is stored in a dictionary, we may construct a :class:`Connection`
instance by `unpacking`_ the dictionary, e.g.

.. _ConfigParser: http://docs.python.org/library/configparser.html
.. _unpacking: http://docs.python.org/tutorial/controlflow.html#unpacking-argument-lists

>>> params = {'user': 'me', 'passwd': 'secret', 'ashost':'10.0.0.1', 'sysnr':'00', 'client':'100'}
>>> conn = Connection(**params)


.. _client-stfcstructure:

Example ``clientStfcStructure.py``
----------------------------------

Lets do a remote function call with a more complex set of parameters.

A function module knows four types of parameters:

1. IMPORT parameters, set by the client.
2. EXPORT parameters, set by the server.
3. CHANGING parameters, set by the client, can be modified by the server.
4. TABLE parameters, set by the client, can be modified by the server.

A simple example of an RFC with different parameter types can be found
in the file ``clientStfcStructure.py`` in the ``examples/`` directory. The FM
``STFC_STRUCTURE`` uses the IMPORT parameter ``IMPORTSTRUCT``, copies it
to the EXPORT parameter ``ECHOSTRUCT``, then modifies it and appends it
to the TABLE parameter ``RFCTABLE``. Furthermore, it fills the EXPORT parameter
``RESPTEXT`` with some system/call information.

The parameter ``IMPORTSTRUCT`` is of type ``RFCTEST``, which contains 12 fields
of different types. We fill these fields with example values (ll. 7-22).
(Note: A comment after each fields tells something about the ABAP datatype.)

.. literalinclude:: ../examples/clientStfcStructure.py
   :language: python
   :lines: 7-22


Afterwards, the FM is invoked via the
:meth:`call(function_name, **kwargs)<Connection.call>` method. It
takes the FM's name as the first argument and then keyword arguments that
describes the IMPORT, CHANGING, and TABLE parameters.

.. literalinclude:: ../examples/clientStfcStructure.py
   :language: python
   :lines: 31

The result contains all EXPORT, CHANGING, and TABLE parameters. It
is printed out::

   {u'ECHOSTRUCT': {u'RFCCHAR1': u'a',
                    u'RFCCHAR2': u'ij',
                    u'RFCCHAR4': u'bcde',
                    u'RFCDATA1': u'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk',
                    u'RFCDATA2': u'llllllllllllllllllllllllllllllllllllllllllllllllll',
                    u'RFCDATE': datetime.date(2012, 10, 3),
                    u'RFCFLOAT': 1.23456789,
                    u'RFCHEX3': 'fgh',
                    u'RFCINT1': 127,
                    u'RFCINT2': 32766,
                    u'RFCINT4': 2147483646,
                    u'RFCTIME': datetime.time(12, 34, 56)},
    u'RESPTEXT': u'SAP R/3 Rel. 702   Sysid: E1Q      Date: 20121012   Time: 212344',
    u'RFCTABLE': [{u'RFCCHAR1': u'X',
                   u'RFCCHAR2': u'YZ',
                   u'RFCCHAR4': u'E1Q',
                   u'RFCDATA1': u'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk',
                   u'RFCDATA2': u'llllllllllllllllllllllllllllllllllllllllllllllllll',
                   u'RFCDATE': datetime.date(2012, 10, 12),
                   u'RFCFLOAT': 2.23456789,
                   u'RFCHEX3': '\xf1\xf2\xf3',
                   u'RFCINT1': 128,
                   u'RFCINT2': 32767,
                   u'RFCINT4': 2147483647,
                   u'RFCTIME': datetime.time(21, 23, 44)}]}

There are some points worth mentioning.

1. The types of the variables are automatically converted from and to Python
   objects in an intuitive way.
2. Parameters are represented as key-value pairs in a dictionary. For more
   complex types, the value is a dictionary (for structures) or a list of
   dictionaries (for tables).

.. _client-printdescription:

Example ``clientPrintDescription.py``
-------------------------------------

As you have seen in the previous example, all you need to know for
calling a FM is the FM's name and its parameters -- the so called
*metadata description*. However, maybe you don't know this in advance,
so what can you do?

A simple approach is to login to the SAP backend system and investigate the
function module's description in transaction SE37.
Alternatively, the :meth:`~Connection.get_function_description` method
could be used.

The example script ``clientPrintDescription.py`` retrieves and
prints the metadata description for a given
function module's name [#f2]_. The :meth:`~Connection.get_function_description`
returns a :class:`FunctionDescription`  object that
contains information about the parameters.
A parameter may have a type description (a :class:`TypeDescription` object),
which contains information about the type's fields.
The scripts iterates over the parameters and fields and prints them out:

.. code-block:: python

   Parameters of function: STFC_STRUCTURE
   NAME          PARAMETER_TYPE    DIRECTION   NUC_LENGTH UC_LENGTH DECIMALS  DEFAULT_VALUE   OPTIONAL   TYPE_DESCRIPTION PARAMETER_TEXT
   IMPORTSTRUCT  RFCTYPE_STRUCTURE RFC_IMPORT  144        264       0                         False      RFCTEST          Importing structure
       -----------( Structure of RFCTEST (n/uc_length=144/264)--
   NAME          FIELD_TYPE        NUC_LENGTH NUC_OFFSET UC_LENGTH UC_OFFSET DECIMALS   TYPE_DESCRIPTION
   RFCFLOAT      RFCTYPE_FLOAT     8          0          8         0         16         None
   RFCCHAR1      RFCTYPE_CHAR      1          8          2         8         0          None
   RFCINT2       RFCTYPE_INT2      2          10         2         10        0          None
   RFCINT1       RFCTYPE_INT1      1          12         1         12        0          None
   RFCCHAR4      RFCTYPE_CHAR      4          13         8         14        0          None
   RFCINT4       RFCTYPE_INT       4          20         4         24        0          None
   RFCHEX3       RFCTYPE_BYTE      3          24         3         28        0          None
   RFCCHAR2      RFCTYPE_CHAR      2          27         4         32        0          None
   RFCTIME       RFCTYPE_TIME      6          29         12        36        0          None
   RFCDATE       RFCTYPE_DATE      8          35         16        48        0          None
   RFCDATA1      RFCTYPE_CHAR      50         43         100       64        0          None
   RFCDATA2      RFCTYPE_CHAR      50         93         100       164       0          None
       -----------( Structure of RFCTEST )-----------
   ----------------------------------------------------------------------------------------------------------------------------------------
   RFCTABLE      RFCTYPE_TABLE     RFC_TABLES  144        264       0                         False      RFCTEST          Importing/exporting table
       -----------( Structure of RFCTEST (n/uc_length=144/264)--
   [...]
       -----------( Structure of RFCTEST )-----------
   ----------------------------------------------------------------------------------------------------------------------------------------
   ECHOSTRUCT    RFCTYPE_STRUCTURE RFC_EXPORT  144        264       0                         False      RFCTEST          Exporting structure
       -----------( Structure of RFCTEST (n/uc_length=144/264)--
   [...]
       -----------( Structure of RFCTEST )-----------
   ----------------------------------------------------------------------------------------------------------------------------------------
   RESPTEXT      RFCTYPE_CHAR      RFC_EXPORT  255        510       0                         False      None             Exporting response message
   ----------------------------------------------------------------------------------------------------------------------------------------

Once again some remarks:

1. The ``parameter_type`` and ``field_type`` are not the ABAP types (that were
   given as a comment in the first example), but the type names given by the
   C connector. For more details on the type conversion,
   see the :ref:`technical details<client-datatypes>`.
2. Most of the information presented here is not relevant for client usage. The
   important values are:

   :attr:`FunctionDescription.parameters`
     ``name``, ``parameter_type``, ``direction``,
     ``nuc_length`` (in case of fixed length strings or numeric strings),
     ``decimals`` (in case of decimal types -- ``RFCTYPE_BCD``), and
     ``optional``.

   :attr:`TypeDescription.fields`
     ``name``, ``field_type``,
     ``nuc_length`` (in case of fixed length strings or numeric strings), and
     ``decimals`` (in case of decimal types -- ``RFCTYPE_BCD``).

3. Later, in the :ref:`server` usage, the classes :class:`FunctionDescription`
   and :class:`TypeDescription` will be used again when installing a function
   on a Python server.

.. _client-errors:

Errors
------

If something goes wrong while working with the RFC functionality, e.g.
invoking a function module that does not exist in the backend, an error
is raised:

>>> python clientPrintDescription.py STFC_STRUCTURES
... An error occurred.
... [...]
... pyrfc._exception.ABAPApplicationError: Error 5: [FU_NOT_FOUND] ID:FL Type:E Number:046 STFC_STRUCTURES ABAP: FL E 046 STFC_STRUCTURES

.. How to get rid of the ``_exception`` part?

For further description see :ref:`Errors <apierr>`.

.. _client-idocunit:

Example clientIDocUnit.py
-------------------------

.. warning::

   The background protocol (bgRFC) is not working in the current version.
   Please use only tRFC/qRFC protocols.

Certain operations, e.g. sending IDocs, are not possible with the RFC protocol.
Rather, a protocol with transactional guarantees has to be used.
The first transactional protocols were tRFC (transactional RFC)
and qRFC (queued RFC). Afterwards, bgRFC (background RFC) were introduced.
All these protocols have in common that they group one or more FM invocations
as one *logical unit of work* (LUW). Consequently, a :class:`Connection`
object offers various methods to work with such *units*.

Working with units is as follows:

1. Initialize a unit by using :meth:`~Connection.initialize_unit`.
   The method returns a unit descriptor, which is used later on.
   When initializing the unit, decide whether to use the bgRFC protocol (default)
   or the tRFC or qRFC protocol by setting ``background=False``.

2. The next step is to create the unit in the backend system,
   prepare the invocation of one or more RFC in it and submit the unit to the
   backend. All this functionality is provided by
   :meth:`~Connection.fill_and_submit_unit`. The method takes
   two required parameters. The first one is a unit descriptor as returned by
   :meth:`~Connection.initialize_unit`. The second one is a list
   of RFC descriptions that should be executed in the unit. A RFC descriptions
   consists of a tuple with the name of the FM as the first element and a
   dictionary describing the function container as the second element.

3. If :meth:`~Connection.fill_and_submit_unit` ended successfully,
   i.e. without raising an exception, the unit should be confirmed by
   :meth:`~Connection.confirm_unit`.
   In case there is a problem with the unit, it can be deleted in the backend
   system by calling :meth:`~Connection.destroy_unit`.

The current state of a unit can be -- in case of units using the bgRFC protocol --
retrieved by :meth:`~Connection.get_unit_state`.

The example script ``clientIDocUnit.py`` provides examples for
sending iDocs. The script was inspired by ``iDocClient.c`` of
:ref:`Schmidt and Li (2009c, pp. 2ff)<c09c>`, but omits the implementation
of client side features that assure atomic execution (see also next section).

.. note::

   Use transaction ``WE05`` to see the IDocs recorded in the SAP backend.

.. note::

   In case you are using queued units (qRFC), use transaction ``SMQR`` to
   register a new queue. In transaction ``SMQ2`` (qRFC monitor) you see the
   incoming calls.
   Note that it is possible to send the unit to a non-registered queue name.
   It will be held with status ``ready`` in the monitor until it is deleted or
   the queue registered. For further information, see `qRFC Administration`_.

.. _`qRFC Administration`: http://help.sap.com/erp2005_ehp_05/helpdata/en/0c/275c3c60065627e10000000a114084/content.htm


Assuring atomic execution
'''''''''''''''''''''''''
In order to assure that the unit is executed exactly once, it is of great
importance that the **end system** on the client side initiates the confirmation.
Citing Schmidt and Le (sapnwrfc.h, l. 1361ff) with modifications:

    | After [fill_and_submit_unit()] returned successfully, you should use this function to cleanup
    | the status information for this unit on backend side. However, be careful: if you have
    | a three-tier architecture, don't bundle Submit and Confirm into one single logical step.
    | Otherwise you run the risk, that the middle tier (the NW RFC lib) successfully executes
    | both, the Submit and the Confirm, but on the way back to the first tier an error occurs
    | and the first tier can not be sure that the unit was really executed in the backend and
    | therefore decides to re-execute it. This will now result in a duplicate execution in the
    | backend, because the Confirm step in the first try has already deleted the UID in the
    | backend, and consequently the backend is no longer protected against re-execution of this
    | UID. In a three-tier architecture, the first tier should trigger both steps separately:
    | first the Submit, and after it knows that the Submit was successful, the Confirm.
    | Also in case the Confirm runs into an error, [...] try the Confirm again at a later point [.]

Further details to this issue can be found in :ref:`Schmidt and Li (2009c, pp. 4-5)<c09c>`.


.. _client-connectionconfig:

Configuration of a connection
=============================

Upon construction, a :class:`Connection` object may be configured
in various ways by passing a ``config`` parameter.

>>> conn = Connection(config = {'keyword': value, ...}, **params)

The following keywords for the config dictionary are possible:

.. _client-connectionconfig-rstrip:

:attr:`~Connection.rstrip`
-----------------------------

ABAP allows two different ways to store strings: A fixed length string type C
and a dynamic length string type STRING.
Strings of type C are padded with blanks, if the content is shorter than the
predefined length. In order to unify the connector's behavior regarding strings,
the ``rstrip`` option was introduced. If set to ``True``, all strings are
right-stripped before being returned by an RFC call.

*Default: True*

.. _client-connectionconfig-returnimportparams:

:attr:`~Connection.return_import_params`
-------------------------------------------
Usually, you do not need the IMPORT parameters in the result of
:meth:`Connection.call`. If ``return_import_params`` is set to ``False``,
parameters of type IMPORT are filtered out.

*Default: False*

.. note::
   All the parameters are public object attributes, i.e. they can be modified
   after the object's construction.

.. _client-methods:

Selected :class:`Connection` methods
====================================

Besides the mentioned methods in the examples, the :class:`Connection` offers
some basic methods for working with a connection:

.. autosummary::

   Connection.ping
   Connection.reset_server_context
   Connection.get_connection_attributes
   Connection.close



.. _client-tech:

Technical details
=================

This section describes the :ref:`client-datatypes` and the :ref:`client-transmission`.


.. _client-datatypes:

Data types
----------

A remote function call executes ABAP code, which works with parameters
that have an ABAP data type. Hence, when you look at the metadata description
you will find ABAP data types for the parameters.

The Python connector does not provide ABAP data types to be instantiated and
used within Python code, but rather converts between ABAP data types and Python
built-in types.

.. Resources:
   http://help.sap.com/saphelp_nw04/helpdata/en/fc/eb2fd9358411d1829f0000e829fbfe/content.htm
   http://msdn.microsoft.com/en-us/library/cc185537%28v=bts.10%29.aspx

================= ========== ========================================== =========== ============== ==================================================================
Type Category     ABAP       Meaning                                    RFC         Python         Remark
================= ========== ========================================== =========== ============== ==================================================================
numeric           I          Integer (whole number)                     INT         int            Internal 1 and 2 byte integers (INT1, INT2) are also mapped to int
numeric           F          Floating point number                      FLOAT       float
numeric           P          Packed number / BCD number                 BCD         Decimal
character         C          Text field (alphanumeric characters)       CHAR        unicode
character         D          Date field (Format: YYYYMMDD)              DATE        datetime.date  or string -> config['dtime']
character         T          Time field (Format: HHMMSS)                TIME        datetime.time  or string -> config['dtime']
character         N          Numeric text field (numeric characters)    NUM         unicode
hexadecimal       X          Hexadecimal field                          BYTE        str [bytes]
variable length   STRING     Dynamic length string                      STRING      unicode
variable length   XSTRING    Dynamic length hexadecimal string          BYTE        str [bytes]
================= ========== ========================================== =========== ============== ==================================================================

Further `details on predefined ABAP types`_ are available online.

.. _details on predefined ABAP types: https://help.sap.com/http.svc/rc/abapdocu_752_index_htm/7.52/en-US/index.htm?file=abenddic_builtin_types_intro.htm

The Python representation of a parameter is a simple key-value pair, where
the key is the name of the parameter and the value is the value of the parameter
in the corresponding Python type.
Beside the mentioned types, there are tables and structures:

* A structure is represented in Python by a dictionary, with the
  structure fields' names as dictionary keys.
* A table is represented in Python by a list of dictionaries.

For an example see :ref:`client-stfcstructure`.

.. _client-transmission:

Data transmission
-----------------

The data transmission in the C connector takes place as follows:
If you want to invoke an RFC,
a function container is constructed from the metadata description of the RFC.
The function container is a memory structure to which the parameters are
written. Then the RFC is invoked and the function container is passed
to the backend system. The backend system now executes the RFC on the
given function container, i.e. it reads some values from the
function container and writes other values to it. Finally, the function
container is passed back to the C connector.

This has some important consequences:

* There is no technical distinction between input and output values.
* In the metadata description, each parameter is classified as IMPORT,
  EXPORT, CHANGING, and TABLES. Hence, there is a convention regarding
  which parameters are set when the RFC is invoked and which parameters
  are filled or changed after the RFC's execution.
* It is possible, though not good practice, to set the output values (i.e.
  parameter of type EXPORT) when invoking an RFC. Similarly, it is possible
  that an RFC will modify the input values (parameters of type IMPORT).
  However, a well written RFC will not manipulate the input values and
  initialize the output values to a default value.



.. rubric:: Footnotes

.. [#f1] To be invoked externally, the function module needs to be
          remote-enabled. For the sake of readability, we will use
          the shorter term ("FM") throughout the text.

.. [#f2] This example was inspired by the ``printDescription.c`` of
         :ref:`Schmidt and Li (2009a, pp. 3ff)<c09a>`.
