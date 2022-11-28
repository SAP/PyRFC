.. currentmodule:: pyrfc

.. _server:

===============
Server scenario
===============

In *Server* scenario, ABAP system is calling Python remote enabled RFC server,
to consume Python functionality. Python functionality must be exposed like
an ABAP function module and Python server shall provide input / output parameters
just like ABAP function module.

To streamline that process, the real ABAP function module is used as a
"blueprint" and Python server will create exactly the same interface to
expose the functionality.

When Python server function "ABC" for example is registered on Python server,
the name of ABAP "blueprint" function module is given, where the input/output
parameters definition shall be taken from. The Python server function "ABC"
can therefore look like ABAP function module "XYZ" for example, using exactly  the same interface
like "XYZ". The ABAP logic of "XYZ" is here irrelevant, the function module can
be empty. Already existing or new ABAP function module can be used here.

Python RFC server shall run in separate thread and that thread is either created
automatically, by PyRFC, or it can be created by Python application.

.. _server-ex:

Examples
========

Here the PyRFC server is registered for ABAP system ``gateway`` and function modules'
"blueprint" definitions are read from ABAP system ``MME``.

Python function ``my_stfc_connection`` is exposed as ABAP function ``STFC_CONNECTION``.

.. literalinclude:: ../examples/server/start_stop.py
   :language: python
   :lines: 39-43

Server in thread created by PyRFC
---------------------------------

Server running in new thread created by PyRFC is started using ``start()`` method:

.. literalinclude:: ../examples/server/start_stop.py
   :language: python
   :lines: 45-49

and can be stopped using ``stop()`` method:

.. literalinclude:: ../examples/server/start_stop.py
   :language: python
   :lines: 66-67

Example: `start_stop.py <https://github.com/SAP/PyRFC/blob/master/examples/server/start_stop.py>`_


Server in thread created by application
---------------------------------------

Server running in new thread created by application is started using
``serve()`` method, like

.. literalinclude:: ../examples/server/serve.py
   :language: python
   :lines: 62-64

and stopped by application:

.. literalinclude:: ../examples/server/serve.py
   :language: python
   :lines: 70-72


Example: `start_stop.py <https://github.com/SAP/PyRFC/blob/master/examples/server/serve.py>`_

Source code of ABAP test reports, calling RFC function modules exposed by Python server:
`z_stfc_connection_call.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_stfc_connection_call.abap>`_ and
`z_stfc_structure_call.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_stfc_structure_call.abap>`_