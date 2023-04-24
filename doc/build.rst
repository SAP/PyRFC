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

* :ref:`Install Python, pip <install-python-linux>` and packages:

  .. code-block:: sh

     pip install build cython wheel pytest sphinx

* :ref:`Install SAP NW RFC Library <install-c-connector>`
* To get any software from the Git source control system the Git
  client is required as well, use whatever your distribution has
* The system must contain a ``gcc`` compiler as well as  development
  header and library files as provided by your distribution

Windows platform
-----------------

* :ref:`Install Python, pip<install-python-win>` and utilities:

  .. code-block:: sh

     pip install build cython wheel pytest sphinx

* :ref:`Visual C++ Redistributable Package for Visual Studio 2013 <install-vs-cpp-redist>` is required for runtime,

* :ref:`Install SAP NW RFC Library <install-c-connector>`
* To get any software from the Git source control system the Git
  client is required as well. Download and install from
  http://code.google.com/p/msysgit/downloads/list?can=3.
  During installation specify that Git runs
  out of the Bash shell as you may need that shell later on.
* Download and install the compiler toolchain, following `SAP Note 2573790 - Installation, Support and Availability of the SAP NetWeaver RFC Library 7.50 <https://launchpad.support.sap.com/#/notes/2573790>`_


macOS platform
--------------

* Install Xcode command line tools with C++ development headers

  .. code-block:: sh

    xcode-select --install
    sudo installer -pkg macOS_SDK_headers_for_macOS_10.14.pkg -target /


Building the code
=================

Clone the repository:

.. code-block:: sh

   git clone https://github.com/SAP/PyRFC
   cd PyRFC
   python -m build --wheel --outdir dist

The result is found in the ``dist/`` directory. The process has to be done on all platforms
for which we provide wheels.


Linting and Formatting
----------------------

.. code-block:: sh

   # cython
   cython-lint setup.py src/pyrfc tests --max-line-length=180

   # python
   flake8 setup.py src tests --max-line-length=180
   black src test



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

    cp -R _build/html ~/tmp
    git checkout gh-pages
    rm -Rf *.html *.js *.egg build doc _* pyrfc* *.inv .buildinfo
    cp -R ~/tmp/_build/html/. .


.. note::

   An additional file .nojekyll is placed in ``gh-pages`` to disable the default GitHub processing which breaks sphinx style folders with leading underscores.

   ``gh-pages`` updates are a bit inconvenien, check if this answer helps http://stackoverflow.com/questions/4750520/git-branch-gh-pages
