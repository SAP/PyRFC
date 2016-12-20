
import os
import sys
from setuptools import setup, find_packages
from distutils.extension import Extension
# Cython import
# Note: Historically, the default setup.py did _not_ contain cython requirements.
#       To build just the extensions inplace, use:
#       python setup.py build_ext --inplace
CYTHON_VERSION = '0.25.2'  # fixed to assure conscious change of version.
try:
    import Cython.Distutils
except ImportError:
    sys.exit("Cython not installed. Please install version {}.".format(CYTHON_VERSION))

# SAP NW RFC SDK dependency
SAPNWRFC_HOME = os.environ.get('SAPNWRFC_HOME')
if not SAPNWRFC_HOME:
    sys.exit("Environment variable SAPNWRFC_HOME not set. Please specify this variable with the root directory of the SAP NW RFC Library.")
# Python sources
PYTHONSOURCE = os.environ.get('PYTHONSOURCE')
if not PYTHONSOURCE:
    sys.exit("Environment variable PYTHONSOURCE not set. Please specify this variable with the root directory of the PYTHONSOURCE Library.")


NAME = 'pyrfc'
here = os.path.abspath(os.path.dirname(__file__))

def _read(name):
    f = open(os.path.join(here, name))
    return f.read()

if sys.platform.startswith('linux'):
    LIBS = ['sapnwrfc', 'sapucum']
    MACROS = [('NDEBUG', None), ('_LARGEFILE_SOURCE', None), ('_FILE_OFFSET_BITS', 64), ('SAPonUNIX', None), ('SAPwithUNICODE', None) , ('SAPwithTHREADS', None), ('SAPonLIN', None)]
    COMPILE_ARGS = ['-Wall', '-O2', '-fexceptions', '-funsigned-char', '-fno-strict-aliasing', '-Wall', '-Wno-uninitialized', '-Wcast-align', '-fPIC', '-pthread', '-minline-all-stringops', '-I{}/include'.format(SAPNWRFC_HOME)]
    LINK_ARGS = ['-L{}/lib'.format(SAPNWRFC_HOME)]
elif sys.platform.startswith('win'):
    LIBS = ['sapnwrfc', 'libsapucum']
    MACROS = [('_LARGEFILE_SOURCE', None), ('SAPwithUNICODE', None), ('_CONSOLE', None), ('WIN32', None), ('SAPonNT', None), ('SAP_PLATFORM_MAKENAME', 'ntintel'), ('UNICODE', None), ('_UNICODE', None)]
    COMPILE_ARGS = ['-I{}\\include'.format(SAPNWRFC_HOME), '-I{}\\Include'.format(PYTHONSOURCE), '-I{}\\Include\\PC'.format(PYTHONSOURCE)]
    #LINK_ARGS = ['-L{}\\lib'.format(SAPNWRFC_HOME)] # JK: Does not work with MS VS8.0 Linker, works with MinGW?
    LINK_ARGS = ['-LIBPATH:{}\\lib'.format(SAPNWRFC_HOME), '-LIBPATH:{}\\PCbuild'.format(PYTHONSOURCE)]

pyrfc = Extension( '%s._%s' % (NAME, NAME)
    , ['%s/_%s.pyx' % (NAME, NAME)]
    , libraries=LIBS
    , define_macros=MACROS
    , extra_compile_args=COMPILE_ARGS
    , extra_link_args=LINK_ARGS
)

# cf. http://docs.python.org/distutils/setupscript.html#additional-meta-data
setup(name=NAME,
    version=_read('VERSION').strip(),
    description='Python bindings for SAP NetWeaver RFC. Wraps SAP NW RFC Library (libsapnwrfc)',
    long_description=_read('README.md'),
    classifiers=[ # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    keywords='%s sap' % NAME,
    author='Srdjan Boskovic',
    author_email='srdjan.boskovic@sap.com',
    url='https://github.com/SAP/pyrfc',
    license='OSI Approved :: Apache Software License',
    packages=find_packages(),
    package_data={
        # If any package contains *.py files, include them:
        '': ['*.py']
    },
    zip_safe=False, # http://packages.python.org/distribute/setuptools.html#setting-the-zip-safe-flag
    install_requires=['setuptools'],
    setup_requires=['setuptools-git',
                    'Cython==' + CYTHON_VERSION,
                    'Sphinx'],
    cmdclass={'build_ext': Cython.Distutils.build_ext},
    ext_modules=[pyrfc],
    test_suite='pyrfc',
)
