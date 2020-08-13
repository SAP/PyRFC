# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

declare -a PYTHONS=("380" "375" "369")

for PYTHON_VERSION in "${PYTHONS[@]}"
do
    rm -rf tests/__pycache__
    rm -rf tests/stfc-mrfc/__pycache__
    echo py$PYTHON_VERSION
    pyenv activate py$PYTHON_VERSION
    PYRFC_BUILD_CYTHON=yes python setup.py bdist_wheel
    pip install --upgrade --force --find-links=dist pynwrfc
    [[ $1 != skip ]] && pytest -vv
done
[[ $1 == sdist ]] && python setup.py sdist


