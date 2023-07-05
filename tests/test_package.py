# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys
from contextlib import suppress
from os import listdir
from os.path import isfile, join

import pytest

from tests.config import latest_python_version

with suppress(ModuleNotFoundError):
    import tomllib


@pytest.mark.skipif(
    "tomllib" not in sys.modules
    or "darwin" not in sys.platform
    or sys.version_info < latest_python_version,
    reason="package check on latest python only",
)
class TestPackageContent:
    """Wheel and sdist package content check."""

    def setup_class(self):
        self.package_name = "pyrfc"
        with open("pyproject.toml", "rb") as file:
            pyproject = tomllib.load(file)
        self.package_name = pyproject["project"]["name"]
        self.version = pyproject["project"]["version"]
        self.temp_dir = join(".tox", "pack", "tmp")
        # assert subprocess.call(["bash", "tests/build_test.sh"]) == 0

    def test_wheel_package(self):
        package_path = join(self.temp_dir, self.package_name)
        package_files = [
            fn for fn in listdir(package_path) if isfile(join(package_path, fn))
        ]
        exts = set()
        # no cython and c sources, only python and 'so'
        for fn in package_files:
            exts.add(fn.rsplit(".")[-1])
        assert exts == {"py", "so"}

    def test_sdist_package(self):
        sdist_path = join(
            self.temp_dir,
            f"{self.package_name}-{self.version}",
            "src",
            self.package_name,
        )
        sdist_files = [fn for fn in listdir(sdist_path) if isfile(join(sdist_path, fn))]
        print(sdist_files)
        exts = set()
        # python, cython and c sources, no 'so'
        for fn in sdist_files:
            exts.add(fn.rsplit(".")[-1])
        assert exts == {"py", "pxd", "pyx", "cpp"}
