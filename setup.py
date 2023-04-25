# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import sys
import os
from setuptools import setup, Extension

PACKAGE_NAME = "pyrfc"
MODULE_NAME = "_cyrfc"

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
        f"-I{SAPNWRFC_HOME}/include",
    ]
    LINK_ARGS = [f"-L{SAPNWRFC_HOME}/lib"]
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
        f"-I{SAPNWRFC_HOME}\\include",
        f"-I{PYTHONSOURCE}\\Include",
        f"-I{PYTHONSOURCE}\\Include\\PC",
        "/EHs",
        "/GL",
        "/Gy",
        "/J",
        "/MD",
        "/nologo",
        "/O2",
        "/Oy-",
        "/we4552",
        "/we4700",
        "/we4789",
        "/W3",
        "/Z7",
    ]

    LINK_ARGS = [
        f"-LIBPATH:{SAPNWRFC_HOME}\\lib",
        f"-LIBPATH:{PYTHONSOURCE}\\PCbuild",
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
        f"-mmacosx-version-min={MACOS_VERSION_MIN}",
        f"-I{SAPNWRFC_HOME}/include",
        "-Wno-cast-align",
        "-Wno-deprecated-declarations",
        "-Wno-unused-function",
        "-Wno-nullability-completeness",
        "-Wno-expansion-to-defined",
        "-Wno-unreachable-code-fallthrough",
    ]
    LINK_ARGS = [
        f"-L{SAPNWRFC_HOME}/lib",
        "-stdlib=libc++",
        f"-mmacosx-version-min={MACOS_VERSION_MIN}",
        # https://stackoverflow.com/questions/6638500/how-to-specify-rpath-in-a-makefile
        f"-Wl,-rpath,{SAPNWRFC_HOME}/lib",
    ]
else:
    sys.exit(f"Platform not supported: {sys.platform}.")


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
    # install_requires=["setuptools"],
    cmdclass=CMDCLASS,  # type: ignore
    ext_modules=cythonize(PYRFC_EXT, annotate=True, compiler_directives={"language_level": "3"})  # type: ignore
    if BUILD_CYTHON
    else [PYRFC_EXT],  # type: ignore
    test_suite=MODULE_NAME,
)
