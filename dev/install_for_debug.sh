#!/bin/bash

if test '!' -f "`pwd`/autolatex.pl"
then
  echo "You must launch this script from the AutoLaTeX root directory." >&2
  exit 255
fi

AUTOLATEX_DIR=`pwd`
AUTOLATEX_DIR=`readlink -f "$AUTOLATEX_DIR"`
# GEDIT
GTK3_SOURCE_DIR="$AUTOLATEX_DIR/libs/gtk3/autolatex"
# GEDIT
GEDIT_SOURCE_DIR="$AUTOLATEX_DIR/plugins/gedit3"
GEDIT_DEST_DIR="$HOME/.local/share/gedit/plugins"

echo "AUTOLATEX_DIR=$AUTOLATEX_DIR"
echo "GEDIT_SOURCE=$GEDIT_SOURCE_DIR"
echo "GEDIT_DEST=$GEDIT_DEST_DIR"

if [ "$1" = "install" ]
then

  #
  # GEDIT
  #
  mkdir -p "$GEDIT_DEST_DIR"

  rm -rfv "$GEDIT_DEST_DIR/autolatexeditor"
  rm -f "$GEDIT_DEST_DIR/autolatexeditor.plugin"

  cp -Rfs "$GEDIT_SOURCE_DIR/"* "$GEDIT_DEST_DIR/"

  cp -Rs "$GTK3_SOURCE_DIR/"* "$GEDIT_DEST_DIR/autolatex/"

  #
  # CONFIG
  #
  mv -fv "$AUTOLATEX_DIR/default.cfg" "$AUTOLATEX_DIR/default.cfg.orig"
  cp -fv "$AUTOLATEX_DIR/default_debug.cfg" "$AUTOLATEX_DIR/default.cfg"

elif [ "$1" = "remove" ]
then
  #
  # GEDIT
  #
  rm -rfv "$GEDIT_DEST_DIR/autolatex"
  rm -fv "$GEDIT_DEST_DIR/autolatex.plugin"

  #
  # CONFIG
  #
  cd "$AUTOLATEX_DIR"
  mv -fv default.cfg.orig default.cfg 2>/dev/null
else
  echo "`basename $0` install|remove" >&2
  exit 255
fi
