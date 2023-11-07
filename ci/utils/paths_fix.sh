# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash

ICUV="50"

if [ -z "$SAPNWRFC_HOME" ]; then
    echo "SAPNWRFC_HOME env variable not set. Should point to SAP NWRFC SDK library root"
    exit 1
fi

# run from sap nwrfc sdk root folder

#
# lib folder fix
#

cd lib
RPATH="$SAPNWRFC_HOME/lib"
for filename in *.dylib; do
    # LC_RPATH
    install_name_tool -add_rpath $RPATH $filename
    # LC_ID_DYLIB
    install_name_tool -id @rpath/$filename $filename
done

# LC_LOAD_DYLIB
install_name_tool -change @loader_path/libicuuc.$ICUV.dylib @rpath/libicuuc.$ICUV.dylib libicui18n.$ICUV.dylib
install_name_tool -change @loader_path/libicudata.$ICUV.dylib @rpath/libicudata.$ICUV.dylib libicui18n.$ICUV.dylib
install_name_tool -change @loader_path/libicudata.$ICUV.dylib @rpath/libicudata.$ICUV.dylib libicuuc.$ICUV.dylib
cd ..

#
# bin folder fix
#

BINFILES="rfcexec startrfc"

cd bin
for filename in ${BINFILES}; do
    chmod +x $filename
    # LC_RPATH
    install_name_tool -add_rpath $RPATH $filename
    # LC_ID_DYLIB
    install_name_tool -id @rpath/$filename $filename
    # LC_LOAD_DYLIB
    install_name_tool -change @loader_path/libsapnwrfc.dylib @rpath/libsapnwrfc.dylib $filename
    install_name_tool -change @loader_path/libsapucum.dylib @rpath/libsapucum.dylib $filename
done
install_name_tool -change @loader_path/libsapucum.dylib @rpath/libsapucum.dylib ./startrfc
cd ..