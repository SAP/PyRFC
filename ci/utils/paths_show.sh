# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash
ARG1=${1:--D}
for filename in lib/*.dylib; do
    otool "$ARG1" $filename
    printf "\n"
done
