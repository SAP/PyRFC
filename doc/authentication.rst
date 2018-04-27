.. _authentication:

========
Security
========

Plain RFC connections are mainly used for prototyping, while in production
secure connections are required. For more information on RFC security see:

* `Security on SAP Service Marketplace <https://www.sap.com/corporate/en/company/security.html>`_
* `RFC Security Best Practices on SAP SCN <http://wiki.scn.sap.com/wiki/display/Security/Best+Practice+-+How+to+analyze+and+secure+RFC+connections>`_
* `Secure Network Communication (SNC) - SAP Help <http://help.sap.com/saphelp_nw70ehp1/helpdata/en/0a/0a2e0fef6211d3a6510000e835363f/frameset.htm>`_

SAP NW RFC Library supports plain and secure connection with following authentication methods:

* `Plain with user / password <plain_auth>`_

* SNC

  * `with User PSE <secure-auth-pse>`_
  * `with X509 <secure-auth-x509>`_

NW ABAP servers support in addition:

* SAP logon tickets
* Security Assertion Markup Language (SAML)

Assuming you are familiar with abovementioned concepts and have ABAP backend system 
configured for SNC communication, here you may find connection strings examples, 
for testing plain and secure RFC connections, with various authentication methods.


Authentication
==============

.. _plain-auth:

Plain with user / password
--------------------------

The simplest and least secure form of the user authentication.

.. code-block:: python

   ABAP_SYSTEM = {
        'user': 'demo',
        'passwd': 'welcome',

        'name': 'I64',
        'client': '800',
        'ashost': '10.0.0.1',
        'sysnr': '00',
        'saprouter': SAPROUTER,
        'trace': '3'
   }

   c = get_connection(ABAP_SYSTEM) # plain

.. _secure-auth-user-pse:

SNC with User PSE
-----------------

`User PSE <http://help.sap.com/saphelp_nw73/helpdata/en/4c/61a6c6364012f3e10000000a15822b/content.htm?frameset=/en/4c/6269c8c72271d0e10000000a15822b/frameset.htm>`_
is used for opening the SNC connection and the same user is used for the authentication
(logon) in NW ABAP backend. Generally not recomended, see `SAP Note 1028503 - SNC-secured RFC connection: Logon ticket is ignored <https://launchpad.support.sap.com/#/notes/1028503>`_

**Prerequisites**

* SNC name must be configured for the ABAP user in NW ABAP system, using transaction SU01

.. figure:: images/SU01-SNC.png
    :align: center

* SAP Single Sign On must be configured on a client and the user must be logged in on a client.

.. code-block:: python

   ABAP_SYSTEM = {
        'snc_partnername': 'p:CN=I64, O=SAP-AG, C=DE',
        'snc_lib': 'C:\\Program Files (x86)\\SECUDE\\OfficeSecurity\\secude.dll',

        'name': 'I64',
        'client': '800',
        'ashost': '10.0.0.1',
        'sysnr': '00',
        'saprouter': SAPROUTER,
        'trace': '3'
   }

   c = get_connection(ABAP_SYSTEM)

In this example the SNC_LIB key contains the path to security library
(SAP cryptographic library or 3rd party product). Alternatively, the 
SNC_LIB can be set as the environment variable, in which case it does 
not have to be provided as a parameter for opening SNC connection.

.. _secure-auth-x509:

SNC with X509
-------------

The client system PSE is used for opening SNC connection and forwarding user 
X509 certificate to NW ABAP backend system, for authentication and logon.

**Prerequisites**

* The user does not have to be logged into the client system, neither the Single
  Sign On must be configured on a client
* The trusted relationship must be established between the NW ABAP backend and 
  the client system.
* The client system must be registered in the NW ABAP backend Access Control 
  List (ACL), using transaction SNC0
* Keystores are generated on a client system, using SAP cryptography tool *SAPGENPSE* and 
  the environment variable SECUDIR points to the folder with generated keystores

.. figure:: images/SNC0-1.png
    :align: center

.. figure:: images/SNC0-2.png
    :align: center

* User X509 certificate must be mapped to ABAP NW backend user, using transaction EXTID_DN

.. figure:: images/EXTID_DN-1.png
    :align: center

.. figure:: images/EXTID_DN-2.png
    :align: center

The same connection parameters as in a previous example, with X509 certificate added.

.. code-block:: python

   ABAP_SYSTEM = {
        'snc_partnername': 'p:CN=I64, O=SAP-AG, C=DE',
        'snc_lib': 'C:\\Program Files (x86)\\SECUDE\\OfficeSecurity\\secude.dll',

        'x509cert': 'MIIDJjCCAtCgAwIBAgIBNzA ... NgalgcTJf3iUjZ1e5Iv5PLKO',

        'name': 'I64',
        'client': '800',
        'ashost': '10.0.0.1',
        'sysnr': '00',
        'saprouter': SAPROUTER,
        'trace': '3'
   }

   c = get_connection(ABAP_SYSTEM)

See `SAP Help <http://help.sap.com/saphelp_nw04s/helpdata/en/b1/07dd3aeedb7445e10000000a114084/frameset.htm>`_ for more information.



