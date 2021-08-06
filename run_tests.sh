#!/bin/bash

DIR=`dirname "$0"`

if test "-$DIR" = "-."; then
	ADIR=`pwd`
else
	ADIR="$DIR"
fi

clear

cd "$DIR/python/libs"
PYTHONPATH=":`pwd`:$ADIR:$ADIR/dev-resources" python3 -B -m unittest discover -s "." -p '*_test.py'

