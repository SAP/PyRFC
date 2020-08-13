# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

echo `strings $SAPNWRFC_HOME/lib/libsapnwrfc.dylib | grep "Patch Level"`
