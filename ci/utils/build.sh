# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

#
# . ci/utils/build.sh
#   pip - update pip
#   test - only test, no build, otherwise build and test
#

python_versions="3.7.16 3.8.16 3.9.16 3.10.10 3.11.2"

rm -rf build

for version in $( echo "$python_versions")
do
    rm -rf tests/__pycache__
    rm -rf tests/stfc-mrfc/__pycache__
    echo py$version
    pyenv activate py$version
    if [[ $1 == pip ]]; then
        pip install --upgrade pip
    else
        if [[ $1 != test ]]; then
            PYRFC_BUILD_CYTHON=yes python setup.py bdist_wheel
            pip install --upgrade --force --find-links=dist pyrfc
        fi
        if [[ $1 != skip-test ]]; then
            pytest -vvx
        fi
    fi
done
python setup.py sdist
