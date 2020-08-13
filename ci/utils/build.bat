:: SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
::
:: SPDX-License-Identifier: Apache-2.0

@echo off
python setup.py bdist_wheel
pip install --upgrade --no-index --find-links=dist pynwrfc
pytest -vv


