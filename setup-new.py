import os
import sys
import Cython
from Cython.Build import cythonize
from setuptools import setup, find_packages
from distutils.extension import Extension

from setuptools import find_packages

# SAP NW RFC SDK dependency
SAPNWRFC_HOME = os.environ.get("SAPNWRFC_HOME")
if not SAPNWRFC_HOME:
    sys.exit(
        "Environment variable SAPNWRFC_HOME not set. Please specify this variable with the root directory of the SAP NW RFC Library."
    )
SAPNWRFC_INCLUDE_DIR = SAPNWRFC_HOME + "/include"

NAME = "pyrfc"
HERE = os.path.abspath(os.path.dirname(__file__))


def _read(name):
    print(name, HERE)
    with open(os.path.join(HERE, name), "r", encoding="utf-8") as f:
        return f.read()


PYTHONSOURCE = "/Users/d037732/.pyenv/versions/3.7.4/include/python3.7m"
INCLUDE_DIRS = [SAPNWRFC_INCLUDE_DIR, PYTHONSOURCE]
LIBRARIES = ["sapnwrfc", "sapucum"]
if sys.platform.startswith("linux"):
    MACROS = [
        ("NDEBUG", None),
        ("_LARGEFILE_SOURCE", None),
        ("_FILE_OFFSET_BITS", 64),
        ("SAPonUNIX", None),
        ("SAPwithUNICODE", None),
        ("SAPwithTHREADS", None),
        ("SAPonLIN", None),
    ]
    COMPILE_ARGS = [
        "-Wall",
        "-O2",
        "-fexceptions",
        "-funsigned-char",
        "-fno-strict-aliasing",
        "-Wall",
        "-Wno-uninitialized",
        "-Wcast-align",
        "-fPIC",
        "-pthread",
        "-minline-all-stringops",
        "-I{}/include".format(SAPNWRFC_HOME),
    ]
    LINK_ARGS = ["-L{}/lib".format(SAPNWRFC_HOME)]
elif sys.platform.startswith("win"):
    MACROS = [
        ("_LARGEFILE_SOURCE", None),
        ("SAPwithUNICODE", None),
        ("_CONSOLE", None),
        ("WIN32", None),
        ("SAPonNT", None),
        ("SAP_PLATFORM_MAKENAME", "ntintel"),
        ("UNICODE", None),
        ("_UNICODE", None),
    ]
    COMPILE_ARGS = [
        "-I{}\\include".format(SAPNWRFC_HOME),
        "-I{}\\Include".format(PYTHONSOURCE),
        "-I{}\\Include\\PC".format(PYTHONSOURCE),
    ]
    LINK_ARGS = [
        "-LIBPATH:{}\\lib".format(SAPNWRFC_HOME),
        "-LIBPATH:{}\\PCbuild".format(PYTHONSOURCE),
    ]
elif sys.platform.startswith("darwin"):
    MACOS_VERSION_MIN = "10.10"
    # unicode paths fix
    # https://apple.stackexchange.com/questions/337940/why-is-usr-include-missing-i-have-xcode-and-command-line-tools-installed-moja
    # https://github.com/neovim/neovim/issues/9050#issuecomment-424417456
    # $ MACOS_UNICODE_INC=/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk/usr/include/unicode
    # $ sudo ln -s $MACOS_UNICODE_INC/uchar.h $SAPNWRFC_HOME/include
    # $ sudo ln -s $MACOS_UNICODE_INC $SAPNWRFC_HOME/include/unicode
    MACROS = [
        ("NDEBUG", None),
        ("_LARGEFILE_SOURCE", None),
        ("_FILE_OFFSET_BITS", 64),
        ("SAPonUNIX", None),
        ("SAPwithUNICODE", None),
        ("SAPwithTHREADS", None),
        ("SAPonLIN", None),
    ]
    COMPILE_ARGS = [
        "-Wall",
        "-O2",
        "-fexceptions",
        "-funsigned-char",
        "-fno-strict-aliasing",
        "-Wall",
        "-Wno-uninitialized",
        "-Wcast-align",
        "-fPIC",
        "-pthread",
        "-minline-all-stringops",
        "-isystem",
        "-std=c++11",
        "-mmacosx-version-min={}".format(MACOS_VERSION_MIN),
        "-I{}/include".format(SAPNWRFC_HOME),
    ]
    LINK_ARGS = [
        "-L{}/lib".format(SAPNWRFC_HOME),
        "-stdlib=libc++",
        "-mmacosx-version-min={}".format(MACOS_VERSION_MIN),
        # https://stackoverflow.com/questions/6638500/how-to-specify-rpath-in-a-makefile
        "-Wl,-rpath,{}/lib".format(SAPNWRFC_HOME),
    ]
else:
    sys.exit("Platform not supported: {}.".format(sys.platform))

# https://docs.python.org/3.7/distutils/apiref.html
extension = Extension(
    language="c++",
    name="%s._%s" % (NAME, NAME),
    sources=["src/%s/_%s.pyx" % (NAME, NAME)],
    include_dirs=INCLUDE_DIRS,
    libraries=LIBRARIES,
    define_macros=MACROS,
    extra_compile_args=COMPILE_ARGS,
    extra_link_args=LINK_ARGS,
)


# http://docs.python.org/distutils/setupscript.html#additional-meta-data
setup(
    name=NAME,
    version=_read("VERSION").strip(),
    description="Python bindings for SAP NetWeaver RFC Library (libsapnwrfc)",
    long_description=_read("README.md"),
    # long_description_content_type="text/markdown",
    classifiers=[  # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="%s sap" % NAME,
    author="Srdjan Boskovic",
    author_email="srdjan.boskovic@sap.com",
    url="https://github.com/SAP/pyrfc",
    license="OSI Approved :: Apache Software License",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={
        # If any package contains *.py files, include them:
        "": ["*.py"]
    },
    # http://packages.python.org/distribute/setuptools.html#setting-the-zip-safe-flag
    zip_safe=False,
    install_requires=["setuptools"],
    setup_requires=["setuptools-git", "Cython", "Sphinx"],
    cmdclass={"build_ext": Cython.Build.build_ext},
    # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#cythonize-arguments
    ext_modules=cythonize(extension, compiler_directives={"language_level": "3"}),
    test_suite="pyrfc",
)
