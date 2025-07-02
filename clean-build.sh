#!/bin/bash

# check for cmake build files
if [ -d "./build" ]
then
    # Clean build
    echo "Remove build"
    rm -rf ./build
fi

# check for python build files
if [ -d "./dist" ]
then
    # Clean dist
    echo "Remove dist"
    rm -rf ./dist
fi
if [ -d "./code_tools_grocsoftware/code_tools_grocsoftware.egg-info" ]
then
    # Clean egg-info
    echo "Remove .egg-info"
    rm -rf ./code_tools_grocsoftware/code_tools_grocsoftware.egg-info
fi

# check for doc files
if [ -d "./doc" ]
then
    # Clean doc files
    echo "Remove documantation"
    rm -rf ./doc
fi
