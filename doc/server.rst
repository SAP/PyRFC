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
"blueprint" and Python server will create exactly such ABAP interface to
expose Python functionality.

When Python server function "ABC" for example is registered on Python server,
the name of ABAP "blueprint" function module is given, where the input/output
parameters definition shall be taken from. Let use ABAP function module "XYZ" for
this example. The Python server will fetch ABAP function module "XYZ" definition
and expose Python function using ABAP function module input/output parameters.
The ABAP logic of "XYZ" is here irrelevant, the function module can
be empty. Already existing or new ABAP function module can be used to define
Python function interface.

Python RFC server shall run in separate thread, created automatically by PyRFC,
or created by Python application.

.. _server-thread-pyrfc:

Server in thread created by PyRFC
=================================

Server running in new thread created by PyRFC is started using ``start()`` method:

.. literalinclude:: ../examples/server/server_pyrfc_thread.py
   :language: python
   :lines: 25-32

and can be stopped using ``stop()`` method:

.. literalinclude:: ../examples/server/server_pyrfc_thread.py
   :language: python
   :lines: 39-40

Example: `server_pyrfc_thread.py <https://github.com/SAP/PyRFC/blob/master/examples/server/server_pyrfc_thread.py>`_

.. _server-thread-app:

Server in thread created by application
=======================================

Here the PyRFC server is registered for ABAP system ``gateway`` and Python function
``my_stfc_connection`` is exposed input/output parameters like ABAP function module ``STFC_CONNECTION``.

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 4-8

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 27-28

Server is created and started in Python function `launch_server()` and this function is invoked in
new thread started by application:

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 18-34

and stopped by application:

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 38-40

Example: `server_app_thread.py <https://github.com/SAP/PyRFC/blob/master/examples/server/server_app_thread.py>`_

Source code of ABAP test reports, calling RFC function modules exposed by Python server:
`z_stfc_connection_call.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_stfc_connection_call.abap>`_ and
`z_stfc_structure_call.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_stfc_structure_call.abap>`_

.. _server-bgrfc:

Background RFC (bgRFC) Server
=============================

Configuration
-------------

*Configure RFC destination using ``SM59`` transaction*

- TCP/IP Connection ```NWRFC_SERVER_OS``
- Special Options > Select Protocol: basXML serializer

``basXML`` serializer shall be configured for RFC server destination in SM59 transaction

.. figure:: _static/images/server/sm59-serializer.png
    :align: center

*Configure bgRFC queues using transaction ``SBGRFCCONF``*

Scheduler app server and destination

.. figure:: _static/images/server/BGRFCCONF-Scheduler-App-Server.png
    :align: center

.. figure:: _static/images/server/SBGRFCCONF-Scheduler-Destination.png
    :align: center

Configure inbound destination prefixes for bgRFC queues' names. Other queue names are processed as standard RFC queues.

.. figure:: _static/images/server/SBGRFCCONF-Define-Inbound-Destination.png
    :align: center


bgRFC Client Test
-----------------

Send bgRFC queue to ABAP system MME

.. code-block:: sh

   python examples/server/bgrfc_client.py MME

.. literalinclude:: ../examples/server/bgrfc_client.py
   :language: python
   :lines: 6-21

Check bgRFC queue status using ``SBGRFCMON - bgRFC Monitor`` transaction

Deleting the unit lock will release the unit for immediate execution

.. figure:: _static/images/server/SBGRFCMON1-Client-MME.png
    :align: center

.. figure:: _static/images/server/SBGRFCMON2-Client-MME.png
    :align: center

bgRFC Server Test
-----------------

