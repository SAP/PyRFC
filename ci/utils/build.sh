# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

#
# . ci/utils/build.sh
#   pip - update pip
#   test - only test, no build, otherwise build and test
#

python_versions="3.7.16 3.8.16 3.9.16 3.10.11 3.11.3"

rm -rf build

for version in $( echo "$python_versions")
do
    rm -rf tests/__pycache__
    rm -rf tests/stfc-mrfc/__pycache__
    echo py$version
    pyenv activate py$version
    if [[ $1 == tools ]]; then
        pip install --upgrade pip build setuptools cython wheel pytest pytest-tetdox tox
    else
        if [[ $1 != test ]]; then
            PYRFC_BUILD_CYTHON=yes python -m build --no-isolation --wheel --outdir dist
            pip install --upgrade --force --find-links=dist pyrfc
        else
            pytest -vvx
        fi
    fi
done
if [[ $1 != tools ]]; then
    # build sdist on Linux
    python -m build --no-isolation --sdist --outdir dist
    pytest -vvx
fi
