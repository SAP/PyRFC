import inspect
import os
import sys
from codecs import open
from setuptools import setup, find_packages
from setuptools.extension import Extension

try:
    import Cython.Distutils
except ImportError:
    sys.exit('Cython not installed.')

# SAP NW RFC SDK dependency
SAPNWRFC_HOME = os.environ.get('SAPNWRFC_HOME')
if not SAPNWRFC_HOME:
    sys.exit('Environment variable SAPNWRFC_HOME not set. Please specify this variable with the root directory of the SAP NW RFC Library.')
# Python sources
PYTHONSOURCE = os.environ.get('PYTHONSOURCE')
if not PYTHONSOURCE:
    PYTHONSOURCE = inspect.getfile(inspect).split('/inspect.py')[0]
    #sys.exit('Environment variable PYTHONSOURCE not set. Please specify this variable with the root directory of the PYTHONSOURCE Library.')

NAME = 'pyrfc'
HERE = os.path.abspath(os.path.dirname(__file__))


def _read(name):
    with open(os.path.join(HERE, name), 'rb', 'utf-8') as f:
        return f.read()


if sys.platform.startswith('linux'):
    LIBS = ['sapnwrfc', 'sapucum']
    MACROS = [('NDEBUG', None), ('_LARGEFILE_SOURCE', None), ('_FILE_OFFSET_BITS', 64),
              ('SAPonUNIX', None), ('SAPwithUNICODE', None), ('SAPwithTHREADS', None), ('SAPonLIN', None)]
    COMPILE_ARGS = ['-Wall', '-O2', '-fexceptions', '-funsigned-char', '-fno-strict-aliasing', '-Wall', '-Wno-uninitialized',
                    '-Wcast-align', '-fPIC', '-pthread', '-minline-all-stringops', '-I{}/include'.format(SAPNWRFC_HOME)]
    LINK_ARGS = ['-L{}/lib'.format(SAPNWRFC_HOME)]
elif sys.platform.startswith('win'):
    LIBS = ['sapnwrfc', 'libsapucum']
    MACROS = [('_LARGEFILE_SOURCE', None), ('SAPwithUNICODE', None), ('_CONSOLE', None), ('WIN32', None),
              ('SAPonNT', None), ('SAP_PLATFORM_MAKENAME', 'ntintel'), ('UNICODE', None), ('_UNICODE', None)]
    COMPILE_ARGS = ['-I{}\\include'.format(SAPNWRFC_HOME), '-I{}\\Include'.format(
        PYTHONSOURCE), '-I{}\\Include\\PC'.format(PYTHONSOURCE)]
    LINK_ARGS = [
        '-LIBPATH:{}\\lib'.format(SAPNWRFC_HOME), '-LIBPATH:{}\\PCbuild'.format(PYTHONSOURCE)]
else:
    sys.exit('Platform not supported: {}.'.format(sys.platform))

# https://docs.python.org/2/distutils/apiref.html
PYRFC_EXT = Extension(
    name='%s._%s' % (NAME, NAME), sources=['src/%s/_%s.pyx' % (NAME, NAME)], libraries=LIBS, define_macros=MACROS, extra_compile_args=COMPILE_ARGS, extra_link_args=LINK_ARGS
)

# cf. http://docs.python.org/distutils/setupscript.html#additional-meta-data
setup(name=NAME,
      version=_read('VERSION').strip(),
      description='Python bindings for SAP NetWeaver RFC Library (libsapnwrfc)',
      long_description=_read('README.md'),
      classifiers=[  # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Cython',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='%s sap' % NAME,
      author='Srdjan Boskovic',
      author_email='srdjan.boskovic@sap.com',
      url='https://github.com/SAP/pyrfc',
      license='OSI Approved :: Apache Software License',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      package_data={
          # If any package contains *.py files, include them:
          '': ['*.py']
      },
      # http://packages.python.org/distribute/setuptools.html#setting-the-zip-safe-flag
      zip_safe=False,
      install_requires=['setuptools'],
      setup_requires=['setuptools-git',
                      'Cython',
                      'Sphinx'],
      cmdclass={'build_ext': Cython.Distutils.build_ext},
      ext_modules=[PYRFC_EXT],
      test_suite='pyrfc',
      )
