#!/usr/bin/env bash
# check is git installed or not
if ! [ -x "$(command -v git)" ]; then
    echo "git is not installed, please install it via package manager"
    exit 1
fi

#set cwd to script directory
cd "$(dirname "$0")" || exit

# check if folder exists
if [ ! -d "../src/thirdparties" ]; then
    echo "third-parties folder not found, creating..."
    mkdir -r ../src/thirdparties
else
    echo "Source code folder found."
fi

# setup git repo
cd ../src/thirdparties
if [ ! -d "./.git" ]; then
    echo "git folder not found, creating..."
    git init
else
    echo "git folder found."
fi
