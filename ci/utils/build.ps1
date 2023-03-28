# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic srdjan.boskovic@sap.com
#
# SPDX-License-Identifier: Apache-2.0

$python_versions = "3.7.9 3.8.10 3.9.13 3.10.9 3.11.2"

$PYRFC_BUILD_CYTHON="yes"

$python_versions.Split(" ") | ForEach {
    $version = $_
    Write-Output $version
    pyenv global $version
    python setup.py bdist_wheel
    pip install --upgrade --force --find-links=dist pyrfc
}
