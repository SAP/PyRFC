# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic srdjan.boskovic@sap.com
#
# SPDX-License-Identifier: Apache-2.0

#
# ci/utils/build.sh
#   pip - update pip
#   test - only test, no build, otherwise build and test
#

$python_versions = "3.7.9 3.8.10 3.9.13 3.10.10 3.11.2"

$env:PYRFC_BUILD_CYTHON="yes"

$action=$args[0]

$python_versions.Split(" ") | ForEach {
    $version = $_

    pyenv shell $version
    python -V

    If($action -eq "pip") {
        python -m pip install --upgrade pip
    } else {
        If($action -ne "test") {
            python setup.py bdist_wheel 
            pip install --upgrade --force --find-links=dist pyrfc
        }
        If($action -ne "skip-test") {
            pytest -vvx
        }
    }
}
