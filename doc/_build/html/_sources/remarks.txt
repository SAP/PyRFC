.. currentmodule:: pyrfc

=======
Remarks
=======

RFC call results differ from expected
=====================================

The response when invoking ABAP function module directly via transaction SE37 
may be different from the response when called via Python connector. Typically leading 
zeros are not shown in SE37 but sent to Python when remote FM is called from Python.

This is surely a bug and in general there are few possible causes: 
the ``pyrfc`` package, the *SAP NW RFC Library*, or the function
module itself. Bugs in *SAP NW RFC Library* are unlikely, in ``pyrfc`` less likely and
the cause is usually the implementation of the ABAP FM, not respecting technical restriction 
described `here <http://sapinsider.wispubs.com/Assets/Articles/2001/January/BAPI-Conversion-Issues>`_.

Conversion ("ALPHA") exists are triggered in SAP GUI and in SE37 but not when 
the ABAP FM is called via SAP RFC protocol, therefore the rectifying logic shall be
implemented in the FM.
The behaviour can be also caised by different authorization levels, when ABAP FM is invoked 
locally or remotely, via SAP RFC protocol.

Please try to assure that RFC is working (e.g. testing with the C connector),
before reporting the problem.


Multiple threads
================

If you work with a multiple thread environment, assure that each thread has
its own ``Connection`` object. The reason is that during the RFC calls,
the Python global interpreter lock (GIL) is released.


Open, valid, and alive connections
==================================

A connection may be closed by the client (e.g. via :meth:`Connection.close`) or
by the server (e.g. if an ABAP message is raised). The connection object
maintains a object variable ``alive`` to record the actual state.
However, the variable is of internal use only, as the connection object
*will try to reopen the connection, if needed*.
This leads to the -- seemingly strange -- situation that an explicitly closed
connection will allow you to call, e.g. :meth:`Connection.ping`.

Implementation remark: It is not possible to query the actual state of the
connection in a reliable manner. Although *SAP NW RFC Library* offers the function
``RfcIsConnectionHandleValid()``, it will only return *False* if the connection
was closed by the client, not if it was closed from the server side. Therefore,
an explicit object variable is kept.
