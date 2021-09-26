#!/usr/bin/env bash

CDIR=`dirname $0`

export PYTHONPATH="$PYTHONPATH:$CDIR/src"

exec python3 -B -m autolatex2.cli.autolatex "$@"

