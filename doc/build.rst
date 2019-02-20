.. _build:

====================
Building from source
====================

SAP NW RFC Library shall be installed as described in the :ref:`Installation
<installation>`. Instead of downloading and installing precompiled egg, you
need to prepare the toolchain and clone the :mod:`pyrfc` repository, so that you can build
the distribution release code and documentation.

Toolchain preparation
=====================

Linux platform
---------------
* :ref:`Install Python and pip <install-python-linux>`
* :ref:`Install SAP NW RFC Library <install-c-connector>`
* To get any software from the Git source control system the Git 
  client is required as well, use whatever your distribution has
* Install Cython. Versions tested so far are 0.17.2, 0.19.0 and 0.20.0, other are expected to work as well.
* The system must contain a ``gcc`` compiler as well as  development
  header and library files as provided by your distribution.

Windows platform
-----------------

* :ref:`Install Python <install-python-win>`
* :ref:`Install SAP NW RFC Library <install-c-connector>`
* To get any software from the Git source control system the Git 
  client is required as well. Download and install from 
  http://code.google.com/p/msysgit/downloads/list?can=3. 
  During installation specify that Git runs 
  out of the Bash shell as you may need that shell later on.
* Install Cython, using `Windows installer <http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython>`_, 
  see also http://wiki.cython.org/64BitCythonExtensionsOnWindows
* Download and install the compiler toolchain, tested on Windows 7 32 and 64 bit platforms

  * `MS VisualStudio2008 Express Edition <http://go.microsoft.com/?linkid=7729279>`_
  * `Microsoft Windows SDK for Windows 7 and .NET Framework 3.5 SP1 <http://www.microsoft.com/en-us/download/details.aspx?id=3138>`_

macOS platform
--------------


* Install Xcode command line tools and C++ development headers


    # $ MACOS_UNICODE_DIR=/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk/usr/include/unicode
    # $ sudo ln -s $MACOS_UNICODE_DIR $SAPNWRFC_HOME/include/unicode
    # $ sudo cp $MACOS_UNICODE_DIR/uchar.h $SAPNWRFC_HOME/include/

Building the code
=================

To build eggs for different Python versions, install these versions
on your system and create a virtual environment for each of these versions,
for example:

``virtualenv --python=<PATH e.g. c:\Python27\python.exe OR /usr/bin/python2.7> ...``

Otherwise, follow the example below.

Linux platform
--------------

Clone the repository:

.. code-block:: sh

   git clone https://github.com/SAP/PyRFC

Edit ``setup.py`` and set the CYTHON_VERSION

Build the distribution

.. code-block:: sh

   python setup.py clean --all
   python setup.py bdist_wheel

The result is found in the ``dist/`` directory. The process has to be done on all platforms 
for which we provide eggs. 


Windows platform
----------------

Open the ``GIT Bash`` shell and clone the repository.

.. code-block:: sh

   git clone https://github.com/SAP/PyRFC

Open the ``CMD Shell`` from ``Microsoft Windows SDK 7.0`` and change to cloned ``pyrfc`` folder.

Edit ``setup.py`` and set the CYTHON_VERSION

Set env variables for the release, use /x64 for 64 bit and /x86 for 32 bit:

.. code-block:: sh

   set DISTUTILS_USE_SDK=1
   setenv /x64 /release

Build the distribution:

.. code-block:: sh

   python setup.py clean --all
   python setup.py bdist_wheel

Check the ``pyrfc\dist`` folder for a new created egg.

macOS platform
--------------



.. code-block:: sh

    MACOS_UNICODE_DIR=/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk/usr/include/unicode
    sudo ln -s $MACOS_UNICODE_DIR $SAPNWRFC_HOME/include/unicode
    sudo cp $MACOS_UNICODE_DIR/uchar.h $SAPNWRFC_HOME/include/.


Virtual Environments
--------------------

You may have buth 32bit and 64bit versions of Python installed on your
system and use virtual environments. This is basically possible (e.g. installing 
the 32bit version on 64 bit system in ``C:\Python27_32\``, but beware of modifying 
the PATH variable.

However, the PATH variable is modified when using a virtual environment, therefore
modify the ``Scripts/activate.bat`` file with:

.. code-block:: sh

   set SAPNWRFC_HOME=C:\nwrfcsdk_x86
   set PATH=C:\nwrfcsdk_x86\lib\;%PATH%
   set PATH=%VIRTUAL_ENV%\Scripts;%PATH%

This assures that specific SAP NW RFC Library is used (e.g. 32bit in this example). 
This is not required for building the distribution, but rather for importing the Python connector.

The build process remains the same, only before building the distribution, you need to 
activate the virtual environment and assure that library paths are correct in ``setup.py``.

Python 3
--------

Prerequisites for building on Python 3, tested on Linux Mint and Ubuntu

.. code-block:: sh

   sudo apt-get install python3-setuptools python3-dev python-configparser
   sudo pip3 install cython sphinx ipython pytest wheel


Building the documentation
==========================

Ensure that the lib directory of the SAP NW RFC library is in your PATH environment.

Change into the ``doc`` directory and type:

.. code-block:: sh

   make clean
   make html

The result is found in ``_build/html`` and for other options call ``make``.

* If you get an error *'sphinx-build' is not recognized as an internal or external command, operable program or batch file* on calling ``make html``, install ``sphinx``
* If you have DLL import errors (Windows), check the lib directory of the SAP NW RFC Library PATH env variable.

The docu is hosted on GitHub Pages, a propietary solution where a git branch ``gh-pages`` is created 
as an orphan and the output of the documentation build process (``_build/html``) is stored in that branch. 
GitHub then serves these files under a special ``/pages/`` url.

To update GitHub Pages, copy everyhing under ``_build/html`` and overwrite the existing files in the ``gh-pages`` branch root.

.. code-block:: sh

    cp _build/html ~/tmp
    git checkout gh-pages
    rm -Rf *.html *.js *.egg build doc _* pyrfc* *.inv .buildinfo 
    cp -R ~/tmp/_build/html/. .


.. note::

   An additional file .nojekyll is placed in ``gh-pages`` to disable the default GitHub processing which breaks sphinx style folders with leading underscores.

   ``gh-pages`` updates are a bit inconvenien, check if this answer helps http://stackoverflow.com/questions/4750520/git-branch-gh-pages
