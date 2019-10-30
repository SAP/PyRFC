#!/bin/bash
ARG1=${1:--D}
for filename in lib/*.dylib; do
    otool "$ARG1" $filename
    printf "\n"
done
