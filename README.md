# SAP NW RFC SDK Client for Python

[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Asynchronous, non-blocking [SAP NetWeawer RFC SDK](https://support.sap.com/en/products/connectors/nwrfcsdk.html) client bindings for Python.

## Features

- Stateless and stateful connections (multiple function calls in the same ABAP session (same context))
- Sequential and parallel calls, using one or more clients
- Automatic conversion between Python and ABAP datatypes
- Extensive unit tests

## Supported platforms

- Python 3, on Python 2 only critical fixes

- The _pyrfc_ connector can be [built from source](http://sap.github.io/PyRFC/build.html) on all [platforms supported by SAP NW RFC SDK](https://launchpad.support.sap.com/#/notes/2573790).

- Pre-built _pyrfc_ wheels are provided in respective [releases](https://github.com/SAP/PyRFC/releases), for Python 3 and Python 2 (until 2020), for Windows 10, Ubuntu 16.04 and macOS 10.14.

## Prerequisites

### All platforms

- SAP NW RFC SDK C++ binaries must be downloaded (SAP partner or customer account required) and [locally installed](http://sap.github.io/node-rfc/install.html#sap-nw-rfc-library-installation). More information on [SAP NW RFC SDK section on SAP Support Portal](https://support.sap.com/en/product/connectors/nwrfcsdk.html). Using the latest version is reccomended as SAP NW RFC SDK is fully backwards compatible, supporting all NetWeaver systems, from today S4, down to R/3 release 4.6C.

- Build from source on macOS and older Linux systems, may require `uchar.h` file, attached to [SAP OSS Note 2573953](https://launchpad.support.sap.com/#/notes/2573953), to be copied to SAP NW RFC SDK include directory: [documentation](http://sap.github.io/PyRFC/install.html#macos)

### Windows

- Visual C++ Redistributable is required for runtime. The version is given in [SAP Note 2573790 - Installation, Support and Availability of the SAP NetWeaver RFC Library 7.50](https://launchpad.support.sap.com/#/notes/2573790)

- Build toolchain for Python 3 requires [Microsoft C++ Build Tools](https://aka.ms/buildtools), the latest version reccomended

- Build toolchain for Python 2 requires [Microsoft Visual C++ 9.0](http://aka.ms/vcpython27)

:exclamation: Due to a [change introduced with Python 3.8 for Windows](https://docs.python.org/3.8/whatsnew/3.8.html#bpo-36085-whatsnew), PATH directories are no longer searched for DLL. The SAP NWRFC SDK lib path is no longer required on PATH, for Python >= 3.8.

### macOS

- The macOS firewall stealth mode must be disabled ([Can't ping a machine - why?](https://discussions.apple.com/thread/2554739)):

```shell
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode off
```

- Remote paths must be set in SAP NWRFC SDK for macOS: [documentation](http://sap.github.io/PyRFC/install.html#macos)

- Build from source requires `uchar.h` file, attached to [SAP OSS Note 2573953](https://launchpad.support.sap.com/#/notes/2573953), to be copied to SAP NW RFC SDK include directory: [documentation](http://sap.github.io/PyRFC/install.html#macos)

## Installation

:exclamation: in preparation :exclamation: Local build from source on your system, triggered by PyPI package install. Check prerequisites above:

```shell
pip install pyrfc
```

Pre-built wheel installation, without local build from source. Check prerequisites above and choose the wheel adequate for your platform:

```shell
pip install https://github.com/SAP/PyRFC/releases/download/2.0.2/pyrfc-2.0.2-cp38-cp38-macosx_10_15_x86_64.whl
```

Alternatively, or if the _pyrfc_ package for your platform not provided, [build the package from source](http://sap.github.io/PyRFC/build.html) on your system and pip install:

```shell
git clone https://github.com/SAP/PyRFC.git
cd PyRFC
python setup.py bdist_wheel
pip install dist/pyrfc-2.0.3-cp38-cp38-macosx_10_15_x86_64.whl
# set ABAP system parameters in test/pyrfc.cfg
pytest -vv
```

See also the the [pyrfc documentation](http://sap.github.io/PyRFC),
complementing _SAP NW RFC SDK_ [documentation](https://support.sap.com/nwrfcsdk).

## Getting started

**Note:** The package must be [installed](#installation) before use.

### Open Connection

In order to call remote enabled ABAP function module (ABAP RFM), first a connection must be opened.

```python
>>> from pyrfc import Connection
>>> conn = Connection(ashost='10.0.0.1', sysnr='00', client='100', user='me', passwd='secret')
```

Connection parameters are documented in **sapnwrfc.ini** file, located in the SAP NWRFC SDK `demo` folder.

### Call ABAP function modules

Using an open connection, remote function modules (RFM) can be invoked. More info in [pyrfc documentation](http://sap.github.io/PyRFC/client.html#client-scenariol).

```python
>>> result = conn.call('STFC_CONNECTION', REQUTEXT=u'Hello SAP!')
>>> print result
{u'ECHOTEXT': u'Hello SAP!',
 u'RESPTEXT': u'SAP R/3 Rel. 702   Sysid: ABC   Date: 20121001   Time: 134524   Logon_Data: 100/ME/E'}
```

Finally, the connection is closed automatically when the instance is deleted by the garbage collector. As this may take some time, we may either call the close() method explicitly or use the connection as a context manager:

```python
>>> with Connection(user='me', ...) as conn:
        conn.call(...)
    # connection automatically closed here
```

Alternatively, connection parameters can be provided as a dictionary:

```python
>>> def get_connection(conn_params):
...     """Get connection"""
...     print 'Connecting ...', conn_params['ashost']
...     return Connection(**conn_param)

>>> from pyrfc import Connection

>>> abap_system = {
...    'user'      : 'me',
...    'passwd'    : 'secret',
...    'ashost'    : '10.0.0.1',
...    'saprouter' : '/H/111.22.33.44/S/3299/W/e5ngxs/H/555.66.777.888/H/',
...    'sysnr'     : '00',
...    'client'    : '100',
...    'trace' : '3', #optional, in case you want to trace
...    'lang'      : 'EN'
... }

>>> conn = get_connection(abap_system)
Connecting ... 10.0.0.1

>>>conn.alive
True
```

See also the the [pyrfc documentation](http://sap.github.io/PyRFC),
complementing _SAP NW RFC SDK_ [documentation](https://support.sap.com/nwrfcsdk).

## Known Issues

- Python 2 will not be maintained past 2020

- Unicode path fix required for [build from source](http://sap.github.io/PyRFC/build.html) on macOS

## How to obtain support

If you encounter an issue or have a feature request, you can create a [ticket](https://github.com/SAP/PyRFC/issues).

Check out the [SAP Community](https://community.sap.com/) (search for "pyrfc") and stackoverflow (use the tag [pyrfc](https://stackoverflow.com/questions/tagged/pyrfc)), to discuss code-related problems and questions.

## License

Copyright (c) 2013 SAP SE or an SAP affiliate company. All rights reserved. This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the [LICENSE](LICENSE) file.
