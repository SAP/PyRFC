# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import os
import sys
from codecs import open
from setuptools import setup, find_packages, Extension

PACKAGE_NAME = "pyrfc"
MODULE_NAME = "_cyrfc"

# long description = readme.md
_here_ = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(_here_, "README.md"), "rb", "utf-8") as readme_file:
    readme_md = readme_file.read().strip()

# set version
__version__ = ""
with open(os.path.join(_here_, "src", PACKAGE_NAME, "version.py")) as version_py:
    exec(version_py.read())

BUILD_CYTHON = bool(os.getenv("PYRFC_BUILD_CYTHON")) or sys.platform.startswith("linux")
CMDCLASS = {}

if BUILD_CYTHON:
    try:
        from Cython.Distutils import build_ext
        from Cython.Build import cythonize
    except ImportError:
        sys.exit("Cython not installed: https://cython.readthedocs.io/en/latest/src/quickstart/install.html")
    CMDCLASS = {"build_ext": build_ext}

# Check if SAP NWRFC SDK configured
SAPNWRFC_HOME = os.environ.get("SAPNWRFC_HOME")
if not SAPNWRFC_HOME:
    sys.exit("Environment variable SAPNWRFC_HOME not set.\n" "Please specify this variable with the root directory of the SAP NWRFC Library.")

print("pyrfc version", __version__)

# https://launchpad.support.sap.com/#/notes/2573953
if sys.platform.startswith("linux"):
    os.system('strings $SAPNWRFC_HOME/lib/libsapnwrfc.so | grep "Patch Level"')
    LIBS = ["sapnwrfc", "sapucum"]
    MACROS = [
        ("NDEBUG", None),
        ("_LARGEFILE_SOURCE", None),
        ("_CONSOLE", None),
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
        "-Wno-deprecated-declarations",
        "-Wno-unused-function",
        "-Wcast-align",
        "-fPIC",
        "-pthread",
        "-minline-all-stringops",
        "-I{}/include".format(SAPNWRFC_HOME),
    ]
    LINK_ARGS = ["-L{}/lib".format(SAPNWRFC_HOME)]
elif sys.platform.startswith("win"):
    # https://docs.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-alphabetically

    # Python sources
    PYTHONSOURCE = os.environ.get("PYTHONSOURCE")
    if not PYTHONSOURCE:
        PYTHONSOURCE = inspect.getfile(inspect).split("/inspect.py")[0]
        # sys.exit('Environment variable PYTHONSOURCE not set. Please specify this variable with the root directory of the PYTHONSOURCE Library.')

    os.system("findstr Patch %SAPNWRFC_HOME%\\lib\\sapnwrfc.dll")
    LIBS = ["sapnwrfc", "libsapucum"]

    MACROS = [
        ("SAPonNT", None),
        ("_CRT_NON_CONFORMING_SWPRINTFS", None),
        ("_CRT_SECURE_NO_DEPRECATES", None),
        ("_CRT_NONSTDC_NO_DEPRECATE", None),
        ("_AFXDLL", None),
        ("WIN32", None),
        ("_WIN32_WINNT", "0x0502"),
        ("WIN64", None),
        ("_AMD64_", None),
        ("NDEBUG", None),
        ("SAPwithUNICODE", None),
        ("UNICODE", None),
        ("_UNICODE", None),
        ("SAPwithTHREADS", None),
        ("_ATL_ALLOW_CHAR_UNSIGNED", None),
        ("_LARGEFILE_SOURCE", None),
        ("_CONSOLE", None),
        ("SAP_PLATFORM_MAKENAME", "ntintel"),
    ]

    COMPILE_ARGS = [
        "-I{}\\include".format(SAPNWRFC_HOME),
        "-I{}\\Include".format(PYTHONSOURCE),
        "-I{}\\Include\\PC".format(PYTHONSOURCE),
        "/EHs",
        "/Gy",
        "/J",
        "/MD",
        "/nologo",
        "/W3",
        "/Z7",
        "/GL",
        "/O2",
        "/Oy-",
        "/we4552",
        "/we4700",
        "/we4789",
    ]

    LINK_ARGS = [
        "-LIBPATH:{}\\lib".format(SAPNWRFC_HOME),
        "-LIBPATH:{}\\PCbuild".format(PYTHONSOURCE),
        "/NXCOMPAT",
        "/STACK:0x2000000",
        "/SWAPRUN:NET",
        "/DEBUG",
        "/OPT:REF",
        "/DEBUGTYPE:CV,FIXUP",
        "/MACHINE:amd64",
        "/nologo",
        "/LTCG",
    ]
elif sys.platform.startswith("darwin"):
    os.system('strings $SAPNWRFC_HOME/lib/libsapnwrfc.dylib | grep "Patch Level"')
    MACOS_VERSION_MIN = "10.15"

    LIBS = ["sapnwrfc", "sapucum"]
    MACROS = [
        ("NDEBUG", None),
        ("_LARGEFILE_SOURCE", None),
        ("_CONSOLE", None),
        ("_FILE_OFFSET_BITS", 64),
        ("SAPonUNIX", None),
        ("SAPwithUNICODE", None),
        ("SAPwithTHREADS", None),
        ("SAPonDARW", None),
    ]
    COMPILE_ARGS = [
        "-Wall",
        "-O2",
        "-fexceptions",
        "-funsigned-char",
        "-fno-strict-aliasing",
        "-Wno-uninitialized",
        "-Wcast-align",
        "-fPIC",
        "-pthread",
        "-minline-all-stringops",
        "-isystem",
        "-std=c++11",
        "-mmacosx-version-min={}".format(MACOS_VERSION_MIN),
        "-I{}/include".format(SAPNWRFC_HOME),
        "-Wno-cast-align",
        "-Wno-deprecated-declarations",
        "-Wno-unused-function",
        "-Wno-nullability-completeness",
        "-Wno-expansion-to-defined",
        "-Wno-unreachable-code-fallthrough",
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

# https://docs.python.org/2/distutils/apiref.html
PYRFC_EXT = Extension(
    language="c++",
    name=f"{PACKAGE_NAME}.{MODULE_NAME}",
    sources=[f"src/{PACKAGE_NAME}/{MODULE_NAME}.pyx"],
    define_macros=MACROS,
    extra_compile_args=COMPILE_ARGS,
    extra_link_args=LINK_ARGS,
    libraries=LIBS,
)

# cf. http://docs.python.org/distutils/setupscript.html#additional-meta-data
setup(
    name=PACKAGE_NAME,
    version=__version__,
    description=("Python bindings for SAP NetWeaver RFC SDK"),
    long_description=readme_md,
    long_description_content_type="text/markdown",
    download_url="https://github.com/SAP/PyRFC/tarball/master",
    classifiers=[  # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=f"{MODULE_NAME} {PACKAGE_NAME} pyrfc sap rfc nwrfc sapnwrfc",
    author="SAP SE",
    url="https://github.com/SAP/pyrfc",
    license="OSI Approved :: Apache Software License",
    maintainer="Srdjan Boskovic",
    maintainer_email="srdjan.boskovic@sap.com",
    packages=find_packages(where="src", exclude=["*.cpp", "*.pxd", "*.html"]),
    package_dir={"": "src"},
    # http://packages.python.org/distribute/setuptools.html#setting-the-zip-safe-flag
    zip_safe=False,
    install_requires=["setuptools"],
    setup_requires=["setuptools-git"],
    extras_require={':"linux" in sys_platform': ["cython"]},
    cmdclass=CMDCLASS,  # type: ignore
    ext_modules=cythonize(PYRFC_EXT, annotate=True, compiler_directives={"language_level": "1"})  # type: ignore
    if BUILD_CYTHON
    else [PYRFC_EXT],  # type: ignore
    test_suite=MODULE_NAME,
)
