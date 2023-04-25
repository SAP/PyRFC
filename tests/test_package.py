import pytest
import subprocess
import sys
import tomllib
from os import listdir
from os.path import isfile, join


@pytest.mark.skipif("darwin" not in sys.platform, reason="testing on Darwin only")
class TestPackage:

    def setup_class(self):
        self.package_name = "pyrfc"
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        self.package_name = data["project"]["name"]
        self.version = data["project"]["version"]
        assert subprocess.call(["bash", "tests/build_test.sh"]) == 0

    def test_package_files(self):
        package_path = join("tests", "tmp", self.package_name)
        package_files = [f for f in listdir(package_path) if isfile(join(package_path, f))]
        print(package_files)
        exts = set()
        # no cython and c sources, only python and 'so'
        for fn in package_files:
            ext = fn.rsplit(".", 1)[1]
            assert ext in ["py", "so"]
            exts.add(ext)
        assert "py" in exts
        assert "so" in exts

    def test_sdist_files(self):
        sdist_path = join("tests", "tmp", f"{self.package_name}-{self.version}", "src", self.package_name)
        sdist_files = [f for f in listdir(sdist_path) if isfile(join(sdist_path, f))]
        print(sdist_files)
        exts = set()
        # python, cython and c sources, no 'so'
        for fn in sdist_files:
            ext = fn.rsplit(".", 1)[1]
            assert ext in ["py", "pxd", "pyx", "cpp"]
            exts.add(ext)
        assert "py" in exts
        assert "pxd" in exts
        assert "pyx" in exts
        assert "cpp" in exts
