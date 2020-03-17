import inspect
import os
import sys
import subprocess
from codecs import open
from setuptools import setup, find_packages, Extension

# Check prerequisites: Cython
try:
    import Cython.Distutils
    from Cython.Build import cythonize
except ImportError:
    sys.exit("Cython not installed.")


# Check prerequisites: SAP NW RFC SDK
SAPNWRFC_HOME = os.environ.get("SAPNWRFC_HOME")
if not SAPNWRFC_HOME:
    sys.exit(
        "Environment variable SAPNWRFC_HOME not set. Please specify this variable with the root directory of the SAP NW RFC Library."
    )

# Python sources
PYTHONSOURCE = os.environ.get("PYTHONSOURCE")
if not PYTHONSOURCE:
    PYTHONSOURCE = inspect.getfile(inspect).split("/inspect.py")[0]
    # sys.exit('Environment variable PYTHONSOURCE not set. Please specify this variable with the root directory of the PYTHONSOURCE Library.')

NAME = "pyrfc"
PYPIPACKAGE = "pynwrfc"
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "VERSION"), "rb", "utf-8") as version_file:
    VERSION = version_file.read().strip()
with open(os.path.join(HERE, "README.md"), "rb", "utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read().strip()

# https://launchpad.support.sap.com/#/notes/2573953
if sys.platform.startswith("linux"):
    subprocess.call("./ci/utils/nwrfcsdk-version-linux.sh", shell=True)
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
    subprocess.call("ci\\utils\\nwrfcsdk-version.bat", shell=True)
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
        "-EHs",
        "-Gy",
        "-J",
        "-MD",
        "-nologo",
        "-W3",
        "-Z7",
        "-GL",
        "-O2",
        "-Oy-",
        "/we4552",
        "/we4700",
        "/we4789",
    ]

    LINK_ARGS = [
        "-LIBPATH:{}\\lib".format(SAPNWRFC_HOME),
        "-LIBPATH:{}\\PCbuild".format(PYTHONSOURCE),
        "-NXCOMPAT",
        "-STACK:0x2000000",
        "-SWAPRUN:NET",
        "-DEBUG",
        "-OPT:REF",
        "-DEBUGTYPE:CV,FIXUP",
        "-MACHINE:amd64",
        "-nologo",
        "-LTCG",
    ]
elif sys.platform.startswith("darwin"):
    subprocess.call("./ci/utils/nwrfcsdk-version-darwin.sh", shell=True)
    MACOS_VERSION_MIN = "10.10"

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
    # https://stackoverflow.com/questions/8024805/cython-compiled-c-extension-importerror-dynamic-module-does-not-define-init-fu
    name="%s.%s" % (NAME, NAME),
    sources=["src/%s/_%s.pyx" % (NAME, NAME)],
    libraries=LIBS,
    define_macros=MACROS,
    extra_compile_args=COMPILE_ARGS,
    extra_link_args=LINK_ARGS,
)

# cf. http://docs.python.org/distutils/setupscript.html#additional-meta-data
setup(
    name=PYPIPACKAGE,
    version=VERSION,
    description=("Python bindings for SAP NetWeaver RFC Library"),
    long_description=LONG_DESCRIPTION,
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="%s %s pyrfc sap rfc nwrfc sapnwrfc" % (NAME, PYPIPACKAGE),
    author="SAP SE",
    url="https://github.com/SAP/pyrfc",
    license="OSI Approved :: Apache Software License",
    maintainer="Srdjan Boskovic",
    maintainer_email="srdjan.boskovic@sap.com",
    packages=find_packages(where="src", exclude=("../material", "../examples/**.*",)),
    package_dir={"": "src"},
    # include_package_data=True,
    # http://packages.python.org/distribute/setuptools.html#setting-the-zip-safe-flag
    zip_safe=False,
    install_requires=["setuptools"],
    setup_requires=["setuptools-git", "Cython", "Sphinx"],
    cmdclass={"build_ext": Cython.Distutils.build_ext},
    ext_modules=cythonize(PYRFC_EXT, annotate=True, language_level="3"),
    test_suite="pyrfc",
)
