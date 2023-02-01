# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

python_versions="3.7.16 3.8.16 3.9.16 3.10.9 3.11.1"

rm -rf build

for version in $( echo "$python_versions")
do
    rm -rf tests/__pycache__
    rm -rf tests/stfc-mrfc/__pycache__
    echo py$version
    pyenv activate py$version
    PYRFC_BUILD_CYTHON=yes python setup.py bdist_wheel
    pip install --upgrade --force --find-links=dist pyrfc
    #[[ $1 != skip ]] && pytest -vv
done
[[ $1 == sdist ]] && python setup.py sdist


