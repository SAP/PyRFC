.. currentmodule:: pyrfc

.. _server:

===============
Server scenario
===============

Server usage refers to a situation, in which a Python script serves RFC requests
that are sent by an SAP backend system.

To illustrate the usage, we will first show an :ref:`server-example`, then
describe some basic aspects of the :ref:`server-server` and finally cover some
:ref:`server-advanced`.

.. note::

   For this section, we assume previous knowledge from the :ref:`client` section.
   Furthermore, the server related article by :ref:`Schmidt and Li (2009b)<c09b>`
   is highly recommended.

.. warning::
   Server functionality is currently not working with Python 32bit under
   Windows.

.. _server-example:

Example ``serverStfcConnection.py``
===================================

Creating a Python RFC server consists basically of two parts:

1. A :class:`~pyrfc.Server` object that stores metadata about the functions
   that it will serve, and that later registers at a gateway.
2. For each served function, a callback function (or: implementing function)
   has to be provided.

A simple example for a server can be found
in the file ``serverStfcConnection.py`` in the ``examples/`` directory.
This server offers a function with the same metadata as ``STFC_CONNECTION``,
but will return a slightly modified version as the usual ABAP implementation.

The metadata for ``STFC_CONNECTION`` consists of

* one IMPORT parameter -- ``REQUTEXT`` -- and
* two EXPORT parameters -- ``ECHOTEXT`` (usually a copy of ``REQUTEXT``) and
  ``RESPTEXT`` (usually some connection/system details).

``STFC_CONNECTION`` callback function
-------------------------------------

Lets look at our callback function (ll. 9-14), that implements the server logic:

.. literalinclude:: ../examples/serverStfcConnection.py
   :language: python
   :lines: 9-15

The callback function takes two parameters. The first one, ``request_context``
contains call-specific information and is obligatory for any callback function.
Afterwards, the parameters depend on the function's metadata description.
In our case, there is one IMPORT parameter that is expected by the callback
function.

The callback function fills the value for the two EXPORT parameters and returns
them in a dictionary.

``STFC_CONNECTION`` Server
--------------------------

The :class:`~pyrfc.Server` class offers server related functionality.
In the example, its usage is found in lines 23-27.

.. literalinclude:: ../examples/serverStfcConnection.py
   :language: python
   :lines: 23-27

* First, a :class:`~pyrfc.Server` object is created and gateway parameters
  are passed.
* Second, a function is installed via :meth:`~pyrfc.Server.install_function`.
  The parameters are a :class:`~pyrfc.FunctionDescription` object and
  a callback function.
* Finally, the server serves requests by invoking the
  :meth:`~pyrfc.Server.serve` method.

A remark regarding the second point: The function description
for our callback function is retrieved from an SAP system in lines 17-20.

.. literalinclude:: ../examples/serverStfcConnection.py
   :language: python
   :lines: 17-20

Retrieving functions descriptions in such a way is convenient for various
reasons (cf. :ref:`Schmidt and Li (2009b, p. 2)<c09b>`). However, hard coding
of function descriptions is possible (cf. :ref:`ex-serverFunctionDescription`).

Registering the server
----------------------

.. Wenn man in SM59 auf Goto->Remote Gateways klickt, bekommt man Informationen
   zu den Gateways.
   Klickt man auf
   Logged on Clients: Goto  Logged on Clients  Delete Client
   (Aus CPIC-Sicht ist nämlich ein registrierter Server ein Client... 


Registering the server needs some preparation in the SAP backend.
Configuration of RFC connections is handled in transaction ``SM59``.
Create a new RFC destination (e.g. ``PYTHON_SVR_DEST``) of type ``T`` and
choose under technical settings:

* Activation type: Registered Server Program
* Registered Server Program: Program ID <your program ID>

The program ID is used when instantiating a Server object.

Invoking the server
-------------------

A simple approach to invoke our server is to

1. log on to an SAP backend system,
2. use transaction ``SE37``,
3. test/execute the function module ``STFC_CONNECTION``, and
4. set ``RFC target sys.`` to the RFC destination of the server
   (e.g. ``PYTHON_SVR_DEST``).


.. _server-server:

Server
======

For server usage, the Python connector offers the class :class:`Server`.
An object is instantiated with gateway parameters. The server will register
at this gateway before serving requests.

Gateway parameters are:

``GWHOST``
  The name of the gateway host

``GWSERV``
  The name of the gateway server

``PROGRAM_ID``
  The name under which the Python connector will register at the gateway. This
  corresponds to an RFC destination in transaction ``SM59`` of type "T" in
  registration mode.

``TRACE``
  Sets the trace level, cf. the documentation of ``RfcSetTraceLevel`` in
  ``sapnwrfc.h`` of the C connector.

``SAPROUTER``
  An SAP router string

Furthermore, the server accepts a ``config`` parameter.

.. _server-config:

Config
------

Upon construction, a :class:`Server` object may be configured
in various ways by passing a ``config`` parameter.

.. _server-config-rstrip:

:attr:`~pyrfc.Server.rstrip`
'''''''''''''''''''''''''''''''''''

ABAP allows two different ways to store strings: A fixed length string type C
and a dynamic length string type STRING.
Strings of type C are padded with blanks, if the content is shorter than the
predefined length. In order to unify the connectors behavior regarding strings,
the ``rstrip`` option was introduced. If set to ``True``, all strings are right
stripped before being passed to the callback function.

*Default: True*

.. _server-functions:

Server functions
----------------

The :meth:`Server.install_function` installs a function in the server. It
expects two parameters: a :class:`FunctionDescription` object for the metadata
description and a callback function that implements the server logic.

The callback function will be called if the gateway receives an RFC call for
the given :class:`FunctionDescription` and if the server object is serving
requests (:meth:`Server.serve`).
In this case, the callback function is called with the following parameters:

``request_context``
  A dictionary with the following key:

  ``connection_attributes``
    A dictionary with connection attributes of the client. The keys are the
    same as returned by :meth:`Connection.get_connection_attributes`, excluding
    ``alive`` and ``active_unit``. As done by
    :meth:`Connection.get_connection_attributes`, the values are right stripped
    strings. These connection attributes may be used for authorization checks.

  For a future release, information about active parameters will be given here.

``<PARAMETERS>``
  All IMPORT, CHANGING, and TABLE parameters of the :class:`FunctionDescription`.


.. _server-advanced:

Advanced topics
===============

.. _server-advanced-exceptions:

Raising exceptions
------------------

An external server program is allowed to throw errors as a usual ABAP function
module. To do so, a certain type of exception is raised.

=========================== =================================== =============================== =============================================== ==================== ===============================================================================================================================================
Error type                  Corresponds to ABAP statement       In Python triggered via         Arguments to pass                               Effect on connection Effect in the back end (ABAP)
=========================== =================================== =============================== =============================================== ==================== ===============================================================================================================================================
ABAP exception              RAISE <exception key>               raise ABAPApplicationError(...) key                                             Remains open         SY-SUBRC is set corresponding to the exception key in the EXCEPTIONS clause.
ABAP exception with details MESSAGE ... RAISING <exception key> raise ABAPApplicationError(...) key, msg_type, msg_class, msg_number, msg_v1-v4 Remains open         As above. The following fields are filled: SY-MSGTY, SY-MSGID, SY-MSGNO, and SY-MSGV1-V4.
ABAP message                MESSAGE ...                         raise ABAPRuntimeError(...)     msg_type, msg_class, msg_number, msg_v1-v4      Is closed            SY-SUBRC is set corresponding to the SYSTEM_FAILURE key in the EXCEPTIONS clause and the SY-MSG fields are filled as above.
System failure                                                  raise ExternalRuntimeError(...) message                                         Is closed            SY-SUBRC is set corresponding to the SYSTEM_FAILURE key in the EXCEPTIONS clause and the parameter specified in the MESSAGE addition is filled.
=========================== =================================== =============================== =============================================== ==================== ===============================================================================================================================================

Other exceptions are not permitted. For further details on error raising cf.
:ref:`Schmidt and Li (2009b, pp. 6ff)<c09b>`.

Note that the arguments have a maximum length. If a longer string is passed,
only the first valid number of characters will be used.

* key: 128 chars
* message: 512 chars
* msg_type: 1 char
* msg_class: 20 chars
* msg_number: 3 chars
* msg_v1-v4: 50 chars each


.. _server-advanced-authorization:

Authorization
-------------

At the current state of the Python connector, an authorization check has to
be implemented in the callback function by evaluating the connection attributes
found in ``request_context['connection_attributes']`` (cf. :ref:`server-functions`).


Hard-coded function descriptions
--------------------------------

In some cases, it is not possible to retrieve the metadata from an SAP backend
system (cf. :ref:`Schmidt and Li (2009c, pp. 9ff)<c09b>`). For these situations,
objects of :class:`~pyrfc.FunctionDescription` and
:class:`~pyrfc.TypeDescription` can be hard-coded.

The required methods are

.. this autosummary generates warnings, because the signatures could not be retrieved (cython code)
.. autosummary::

   FunctionDescription.add_parameter
   TypeDescription.add_field


.. _ex-serverFunctionDescription:

Example serverFunctionDescription.py
''''''''''''''''''''''''''''''''''''

Similar to the example ``hardCodedServer.c`` of the C connector, in the file
``serverFunctionDescription.py`` in the ``examples/`` directory,
a function description -- and included type descriptions -- are constructed
manually.
In line 3-15 we define a :class:`~pyrfc.TypeDescription` object
consisting of three fields:

.. literalinclude:: ../examples/serverFunctionDescription.py
   :language: python
   :lines: 3-15

Afterwards, a :class:`~pyrfc.FunctionDescription` object is created and
several fields are added.

.. literalinclude:: ../examples/serverFunctionDescription.py
   :language: python
   :lines: 17-55
