#!/bin/bash

if test '!' -f "`pwd`/autolatex.pl"
then
  echo "You must launch this script from the AutoLaTeX root directory." >&2
  exit 255
fi

AUTOLATEX_DIR=`pwd`
AUTOLATEX_DIR=`readlink -f "$AUTOLATEX_DIR"`
# PYTHON GENERAL LIB
PYTHON_SOURCE_DIR="$AUTOLATEX_DIR/python"
# GEDIT
GEDIT_SOURCE_DIR="$AUTOLATEX_DIR/plugins/gedit"
GEDIT_DEST_DIR="$HOME/.local/share/gedit/plugins"
# SUBLIME TEXT
SUBLIME_SOURCE_DIR="$AUTOLATEX_DIR/plugins/sublime-text-2/autolatex"
SUBLIME_DEST_DIR="$HOME/.config/sublime-text-2/Packages/autolatex"

echo "AUTOLATEX_DIR=$AUTOLATEX_DIR"
echo "GEDIT_SOURCE=$GEDIT_SOURCE_DIR"
echo "GEDIT_DEST=$GEDIT_DEST_DIR"
echo "SUBLIME_SOURCE=$SUBLIME_SOURCE_DIR"
echo "SUBLIME_DEST=$SUBLIME_DEST_DIR"

if [ "$1" = "install" ]
then

  #
  # GEDIT
  #
  rm -rfv "$GEDIT_DEST_DIR/autolatex"*

  mkdir -pv "$GEDIT_DEST_DIR/autolatex/config"
  mkdir -pv "$GEDIT_DEST_DIR/autolatex/config/cli"
  mkdir -pv "$GEDIT_DEST_DIR/autolatex/config/plugin"
  mkdir -pv "$GEDIT_DEST_DIR/autolatex/ui"
  mkdir -pv "$GEDIT_DEST_DIR/autolatex/utils"
  mkdir -pv "$GEDIT_DEST_DIR/autolatex/widgets"

  ln -sv "$PYTHON_SOURCE_DIR/utils/"*.py "$GEDIT_DEST_DIR/autolatex/utils"

  ln -sv "$GEDIT_SOURCE_DIR/"*.plugin "$GEDIT_DEST_DIR/"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/"*.py "$GEDIT_DEST_DIR/autolatex/"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/icons" "$GEDIT_DEST_DIR/autolatex/"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/config/"*.py "$GEDIT_DEST_DIR/autolatex/config"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/config/cli/"*.py "$GEDIT_DEST_DIR/autolatex/config/cli"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/config/plugin/"*.py "$GEDIT_DEST_DIR/autolatex/config/plugin"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/ui/"*.ui "$GEDIT_DEST_DIR/autolatex/ui"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/utils/"*.py "$GEDIT_DEST_DIR/autolatex/utils"
  ln -sv "$GEDIT_SOURCE_DIR/autolatex/widgets/"*.py "$GEDIT_DEST_DIR/autolatex/widgets"

  #
  # SUBLIME TEXT
  #
  rm -rfv "$SUBLIME_DEST_DIR"

  mkdir -pv "$SUBLIME_DEST_DIR/utils"

  ln -sv "$PYTHON_SOURCE_DIR/utils/"*.py "$SUBLIME_DEST_DIR/utils"

  ln -sv "$SUBLIME_SOURCE_DIR/"*.sublime-* "$SUBLIME_DEST_DIR/"
  ln -sv "$SUBLIME_SOURCE_DIR/"*.py "$SUBLIME_DEST_DIR/"
  ln -sv "$SUBLIME_SOURCE_DIR/utils/"*.py "$SUBLIME_DEST_DIR/utils/"

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
  # SUBLIME TEXT
  #
  rm -rfv "$SUBLIME_DEST_DIR"

  #
  # CONFIG
  #
  cd "$AUTOLATEX_DIR"
  mv -fv default.cfg.orig default.cfg 2>/dev/null
else
  echo "`basename $0` install|remove" >&2
  exit 255
fi
