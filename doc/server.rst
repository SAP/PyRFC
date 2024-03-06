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
   :lines: 41-54

and can be stopped using ``close()`` method:

.. literalinclude:: ../examples/server/server_pyrfc_thread.py
   :language: python
   :lines: 61-62

Example: `server_pyrfc_thread.py <https://github.com/SAP/PyRFC/blob/master/examples/server/server_pyrfc_thread.py>`_

.. _server-thread-app:

Server in thread created by application
=======================================

Here the PyRFC server is registered for ABAP system ``gateway`` and Python function
``my_stfc_connection`` is exposed input/output parameters like ABAP function module ``STFC_CONNECTION``.

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 10-20

Server is created and started in Python function `launch_server()` and this function is invoked in
new thread started by application:

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 33-60

and stopped by application:

.. literalinclude:: ../examples/server/server_app_thread.py
   :language: python
   :lines: 62-63

Example: `server_app_thread.py <https://github.com/SAP/PyRFC/blob/master/examples/server/server_app_thread.py>`_

Source code of ABAP test reports, calling RFC function modules exposed by Python server:
`z_stfc_connection_call.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_stfc_connection_call.abap>`_ and
`z_stfc_structure_call.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_stfc_structure_call.abap>`_

.. _server-bgrfc:

Background RFC (bgRFC) Server
=============================

Configuration
-------------

Configure RFC destination using ``SM59`` transaction

- TCP/IP Connection ``NWRFC_SERVER_OS``
- Special Options > Select Protocol: basXML serializer

``basXML`` serializer shall be configured for RFC server destination in SM59 transaction

.. image:: _static/images/server/sm59-serializer.png
   :scale: 50%

Configure bgRFC queues using ``SBGRFCCONF`` transaction

Scheduler app server and destination

.. image:: _static/images/server/SBGRFCCONF-Scheduler-App-Server.png
   :scale: 50%

Scheduler destination

.. image:: _static/images/server/SBGRFCCONF-Scheduler-Destination.png
   :scale: 50%

Configure inbound destination prefixes for bgRFC queues' names. Other queue names are processed as standard RFC queues.

.. image:: _static/images/server/SBGRFCCONF-Define-Inbound-Destination.png
   :scale: 50%

bgRFC Client
------------

To test sending bgRFC queue to ABAP system, you can try the example
`bgrfc_client.py <https://github.com/SAP/PyRFC/blob/master/examples/server/bgrfc_client.py>`_ , adapted to your system,

.. code-block:: sh

   python examples/server/bgrfc_client.py MME

.. literalinclude:: ../examples/server/bgrfc_client.py
   :language: python
   :lines: 6-21

Check bgRFC queue status using ``SBGRFCMON - bgRFC Monitor`` transaction

Deleting the unit lock will release the unit for immediate execution

.. image:: _static/images/server/SBGRFCMON1-Client-MME.png
   :scale: 50%

.. image:: _static/images/server/SBGRFCMON2-Client-MME.png
   :scale: 50%


bgRFC Server
------------

For bgRFC server configuration and implementation, first check the section ``5.6 Queued and Background RFC Server`` of
`SAP NWRFC SDK 7.50 Programming Guide <https://support.sap.com/content/dam/support/en_us/library/ssp/products/connectors/nwrfcsdk/NW_RFC_750_ProgrammingGuide.pdf>`_

In addition to standard server, the bgRFC server requires the implementation of bgRFC event handlers,
as per example `bgrfc_server.py <https://github.com/SAP/PyRFC/blob/master/examples/server/bgrfc_server.py>`_
Event handlers shall be registered before server has started:

.. literalinclude:: ../examples/server/bgrfc_server.py
   :language: python
   :lines: 158-189

To test, first start the Python server

.. code-block:: sh

   python examples/server/bgrfc_server.py ALX

   [2023-03-28 12:16:13.215013 UTC] Server connection '5175819264'
   {'serverName': '', 'protocolType': 'multi count', 'registrationCount': 0, 'state': 'RFC_SERVER_INITIAL', 'currentBusyCount': 0, 'peakBusyCount': 0}
   [2023-03-28 12:16:13.577820 UTC] Server function installed 'STFC_WRITE_TO_TCPIC'
   [2023-03-28 12:16:13.578015 UTC] Server function installed '{'func_desc_handle': 5166353136, 'callback': <function stfc_write_to_tcpic at 0x1007f2020>, 'server': <pyrfc._cyrfc.Server object at 0x1008b81d0>}'
   [2023-03-28 12:16:13.645304 UTC] Server 'launched 5175819264'
   Press Enter key to stop server...

Then run ABAP test report `z_nwrfc_server_bgrfc.abap <https://github.com/SAP/PyRFC/blob/master/examples/server/z_nwrfc_server_bgrfc.abap>`_
to create outbound bgRFC queue in ABAP system

.. image:: _static/images/server/z_nwrfc_server_bgrfc.png
    :align: center

After pressing the ``Execute`` button, the server log in Python system shell continues with

.. code-block:: sh

   bgRFC:onCheck handle 5175859712 tid FA163E82B1991EDDB3AC6EB2628DE0F1 status created
   [2023-03-28 12:24:27.128859 UTC] metadataLookup 'Function 'STFC_WRITE_TO_TCPIC' handle 5166353136.'
   [2023-03-28 12:24:27.130577 UTC] genericHandler 'User 'BOSKOVIC' from system 'ALX', client '000', host 'vmw6265.wdf.sap.corp' invokes 'STFC_WRITE_TO_TCPIC''
   [2023-03-28 12:24:27.130621 UTC] authorization check for 'STFC_WRITE_TO_TCPIC' '{'call_type': <UnitCallType.background_unit: 3>, 'is_stateful': False, 'unit_identifier': {'queued': True, 'id': 'FA163E82B1991EDDB3AC6EB2628DE0F1'}, 'unit_attributes': {'kernel_trace': False, 'sat_trace': False, 'unit_history': False, 'lock': True, 'no_commit_check': False, 'user': 'BOSKOVIC', 'client': '000', 't_code': 'SE38', 'program': 'Z_NWRFC_SERVER_BGRFC', 'hostname': 'ldai1alx_ALX_18', 'sending_date': '20230328', 'sending_time': '122427'}}'
   server function: stfc_write_to_tcpic tid: FA163E82B1991EDDB3AC6EB2628DE0F1 call: 0 {'call_type': <UnitCallType.background_unit: 3>, 'is_stateful': False, 'unit_identifier': {'queued': True, 'id': 'FA163E82B1991EDDB3AC6EB2628DE0F1'}, 'unit_attributes': {'kernel_trace': False, 'sat_trace': False, 'unit_history': False, 'lock': True, 'no_commit_check': False, 'user': 'BOSKOVIC', 'client': '000', 't_code': 'SE38', 'program': 'Z_NWRFC_SERVER_BGRFC', 'hostname': 'ldai1alx_ALX_18', 'sending_date': '20230328', 'sending_time': '122427'}}
   TCPICDAT: [{'LINE': 'BASIS_BGRFC_OUTIN   00001               12345678901234567890123456789012'}]
   bgRFC:onCommit handle 5175859712 unit {'queued': True, 'id': 'FA163E82B1991EDDB3AC6EB2628DE0F1'}
   bgRFC:onConfirm handle 5175859712 unit {'queued': True, 'id': 'FA163E82B1991EDDB3AC6EB2628DE0F1'}

After pressing ``Enter`` button in Python system shell, recorded events are shown, recorded in `tlog.log <https://github.com/SAP/PyRFC/blob/masterexamples/server/tlog.log>`_

.. code-block:: sh

   2023-03-28 12:24:27.127087 FA163E82B1991EDDB3AC6EB2628DE0F1 created
   2023-03-28 12:24:27.130816 FA163E82B1991EDDB3AC6EB2628DE0F1 executed stfc_write_to_tcpic
   2023-03-28 12:24:27.132676 FA163E82B1991EDDB3AC6EB2628DE0F1 committed
   2023-03-28 12:24:27.224103 FA163E82B1991EDDB3AC6EB2628DE0F1 confirmed

Unit status management and log example is provided in ``TLog`` class in `tlog.py <https://github.com/SAP/PyRFC/blob/masterexamples/server/tlog.py>`_ script
and can be tested like:

.. code-block:: sh

   python examples/server/tlog.py

   True
   {'utc': '2023-03-28 12:32:35.064000', 'tid': '60819ABA77594C698E98D552951A8A3B', 'status': 'executed', 'note': 'python_function_module'}

   6
   2023-03-28 12:24:27.127087 FA163E82B1991EDDB3AC6EB2628DE0F1 created
   2023-03-28 12:24:27.130816 FA163E82B1991EDDB3AC6EB2628DE0F1 executed stfc_write_to_tcpic
   2023-03-28 12:24:27.132676 FA163E82B1991EDDB3AC6EB2628DE0F1 committed
   2023-03-28 12:24:27.224103 FA163E82B1991EDDB3AC6EB2628DE0F1 confirmed
   2023-03-28 12:31:38.743892 41C5E22EB6D345EDBA8D8FBCD9F3EDE9 created
   2023-03-28 12:31:38.744026 41C5E22EB6D345EDBA8D8FBCD9F3EDE9 executed python_function_module