# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: CC0-1.0

#!/bin/bash
ARG1=${1:--D}
for filename in lib/*.dylib; do
    otool "$ARG1" $filename
    printf "\n"
done
