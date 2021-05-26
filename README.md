# PyRFC

:heavy_exclamation_mark: Upgrade to SAP NWRFC SDK PL8 before using PyRFC 2.4.0 or newer

:heavy_exclamation_mark: Package name is changed, use `pip install pyrfc` instead of `pip install pynwrfc`. The 2.4.0 is the last release packaged into `pyrfc` and `pynwrfc`.

Asynchronous, non-blocking [SAP NetWeawer RFC SDK](https://support.sap.com/en/product/connectors/nwrfcsdk.html) bindings for Python.

[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/pyrfc)](https://pypi.org/project/pynfc/)
[![PyPI - Version](https://img.shields.io/pypi/v/pyrfc)](https://pypi.org/project/pyrfc/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrfc)](https://pypi.org/project/pyrfc/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyrfc)](https://pypistats.org/packages/pyrfc)
[![REUSE status](https://api.reuse.software/badge/github.com/SAP/PyRFC)](https://api.reuse.software/info/github.com/SAP/PyRFC)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4349/badge)](https://bestpractices.coreinfrastructure.org/projects/4349)

## Features

- Client, Throughput and Server bindings
- Automatic conversion between Python and ABAP datatypes
- Stateless and stateful connections (multiple function calls in the same ABAP session / same context)
- Sequential and parallel calls, using one or more clients

## Supported platforms

- Python 3

- Windows 10 and macOS >= 10.15 supported by pre-built wheels and build from source installation

- Linux wheels are supported by build from source installation only

- Prebuilt Centos wheels are attached to the [latest release on GitHub](https://github.com/SAP/PyRFC/releases/latest)

- Pre-built [portable Linux wheels](https://www.python.org/dev/peps/pep-0513/)

  - are not supported, neither issues related to portable Linux wheels

  - :exclamation: must not be distributed with embedded SAP NWRFC SDK binaries, only private use permitted

- [Platforms supported by SAP NWRFC SDK](https://launchpad.support.sap.com/#/notes/2573790) can be supported by [build from source](http://sap.github.io/PyRFC/build.html)

## Requirements

### All platforms

- SAP NWRFC SDK 7.50 PL3 or later must be [downloaded](https://launchpad.support.sap.com/#/softwarecenter/template/products/_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT) (SAP partner or customer account required) and [locally installed](http://sap.github.io/node-rfc/install.html#sap-nw-rfc-library-installation)

  - Using the latest version is recommended as SAP NWRFC SDK is fully backwards compatible, supporting all NetWeaver systems, from today S4, down to R/3 release 4.6C.
  - SAP NWRFC SDK [overview](https://support.sap.com/en/product/connectors/nwrfcsdk.html) and [release notes](https://launchpad.support.sap.com/#/softwarecenter/object/0020000000340702020)

- Build from source on older Linux systems, may require `uchar.h` file, attached to [SAP OSS Note 2573953](https://launchpad.support.sap.com/#/notes/2573953), to be copied to SAP NWRFC SDK include directory

### Windows

- [Visual C++ Redistributable Package for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784) is required for runtime, see [SAP Note 2573790 - Installation, Support and Availability of the SAP NetWeaver RFC Library 7.50](https://launchpad.support.sap.com/#/notes/2573790)

- Build toolchain for Python 3 requires [Microsoft C++ Build Tools](https://aka.ms/buildtools), the latest version recommended

- Build toolchain for Python 2 requires [Microsoft Visual C++ 9.0](http://aka.ms/vcpython27)

:exclamation: Due to a [change introduced with Python 3.8 for Windows](https://docs.python.org/3.8/whatsnew/3.8.html#bpo-36085-whatsnew), PATH directories are no longer searched for DLL. The SAP NWRFC SDK lib path is no longer required on PATH, for Python >= 3.8.

### macOS

- The macOS firewall stealth mode must be disabled ([Can't ping a machine - why?](https://discussions.apple.com/thread/2554739)):

```shell
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode off
```

- Remote paths must be set in SAP NWRFC SDK for macOS: [documentation](http://sap.github.io/PyRFC/install.html#macos)

- When the node-rfc is started for the first time, the popups come-up for each NWRFC SDK library, to confirm it should be opened. If SDK is installed in admin folder, the node-rfc app shall be that first time started with admin privileges, eg. `sudo -E`

## SPJ articles

Highly recommended reading about RFC communication and SAP NW RFC Library, published in the SAP Professional Journal (SPJ)

- [Part I RFC Client Programming](https://wiki.scn.sap.com/wiki/x/zz27Gg)

- [Part II RFC Server Programming](https://wiki.scn.sap.com/wiki/x/9z27Gg)

- [Part III Advanced Topics](https://wiki.scn.sap.com/wiki/x/FD67Gg)

## Download and installation

```shell
pip install pyrfc
```

Cython is required on Linux platforms, for the the default build from source installation method.

Build from source can be also requested on Windows and Darwin platforms:

```shell
pip install pyrfc --no-binary :all:
# or
PYRFC_BUILD_CYTHON=yes pip install pyrfc --no-binary :all:
```

Alternative build from source installation:

```shell
git clone https://github.com/SAP/PyRFC.git
cd PyRFC
python setup.py bdist_wheel
pip install --upgrade --no-index --find-links=dist pyrfc
```

See also the [pyrfc documentation](http://sap.github.io/PyRFC),
complementing _SAP NWRFC SDK_ [documentation](https://support.sap.com/nwrfcsdk).

## Getting started

**Note:** The package must be [installed](#installation) before use.

### Open Connection

In order to call remote enabled ABAP function module (ABAP RFM), first a connection must be opened.

```python
from pyrfc import Connection
conn = Connection(ashost='10.0.0.1', sysnr='00', client='100', user='me', passwd='secret')
```

Connection parameters are documented in **sapnwrfc.ini** file, located in the SAP NWRFC SDK `demo` folder.

### Call ABAP function modules

Using an open connection, remote function modules (RFM) can be invoked. More info in [pyrfc documentation](http://sap.github.io/PyRFC/client.html#client-scenariol).

```python
# ABAP variables are mapped to Python variables
result = conn.call('STFC_CONNECTION', REQUTEXT=u'Hello SAP!')
print (result)
{u'ECHOTEXT': u'Hello SAP!',
 u'RESPTEXT': u'SAP R/3 Rel. 702   Sysid: ABC   Date: 20121001   Time: 134524   Logon_Data: 100/ME/E'}

# ABAP structures are mapped to Python dictionaries
IMPORTSTRUCT = { "RFCFLOAT": 1.23456789, "RFCCHAR1": "A" }

# ABAP tables are mapped to Python lists, of dictionaries representing ABAP tables' rows
IMPORTTABLE = []

result = conn.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE)

print result["ECHOSTRUCT"]
{ "RFCFLOAT": 1.23456789, "RFCCHAR1": "A" ...}

print result["RFCTABLE"]
[{ "RFCFLOAT": 1.23456789, "RFCCHAR1": "A" ...}]
```

Finally, the connection is closed automatically when the instance is deleted by the garbage collector. As this may take some time, we may either call the close() method explicitly or use the connection as a context manager:

```python
with Connection(user='me', ...) as conn:
    conn.call(...)
# connection automatically closed here
```

Alternatively, connection parameters can be provided as a dictionary:

```python
def get_connection(conn_params):
    """Get connection"""
    print 'Connecting ...', conn_params['ashost']
    return Connection(**conn_param)

from pyrfc import Connection

abap_system = {
    'user'      : 'me',
    'passwd'    : 'secret',
    'ashost'    : '10.0.0.1',
    'saprouter' : '/H/111.22.33.44/S/3299/W/e5ngxs/H/555.66.777.888/H/',
    'sysnr'     : '00',
    'client'    : '100',
    'trace'     : '3', #optional, in case you want to trace
    'lang'      : 'EN'
}

conn = get_connection(**abap_system)
Connecting ... 10.0.0.1

conn.alive
True
```

See also the [pyrfc documentation](http://sap.github.io/PyRFC),
complementing _SAP NWRFC SDK_ [documentation](https://support.sap.com/nwrfcsdk).

## How to obtain support

If you encounter an issue or have a feature request, you can create a [ticket](https://github.com/SAP/PyRFC/issues).

Check out the [SAP Community](https://community.sap.com/) (search for "pyrfc") and stackoverflow (use the tag [pyrfc](https://stackoverflow.com/questions/tagged/pyrfc)), to discuss code-related problems and questions.

## **Contributing**

We appreciate contributions from the community to **PyRFC**!
See [CONTRIBUTING.md](CONTRIBUTING.md) for more details on our philosophy around extending this module.

## License

Copyright (c) 2018 SAP SE or an SAP affiliate company. All rights reserved. This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the [LICENSE file](LICENSES/Apache-2.0.txt).