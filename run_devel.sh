#!/bin/bash

DIR=`dirname "$0"`

clear

cd "$DIR/python/libs"
PYTHONPATH=":`pwd`" python3 -B "$@"

