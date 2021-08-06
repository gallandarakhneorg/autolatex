#!/bin/bash

if which python3 2>/dev/null >/dev/null
then
  exec autolatex-config "$@"
else
  exec autolatex-gtk2 "$@"
fi
