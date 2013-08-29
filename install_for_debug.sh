#!/bin/bash

AUTOLATEX_DIR=`dirname "$0"`
AUTOLATEX_DIR=`readlink -f "$AUTOLATEX_DIR"`
SOURCE_DIR="$AUTOLATEX_DIR/plugins/gedit"
DEST_DIR="$HOME/.local/share/gedit/plugins"

echo "AUTOLATEX_DIR=$AUTOLATEX_DIR"
echo "SOURCE=$SOURCE_DIR"
echo "DEST=$DEST_DIR"

if [ "$1" = "install" ]
then

  rm -rfv "$DEST_DIR/autolatex"*

  mkdir -pv "$DEST_DIR/autolatex/config"
  mkdir -pv "$DEST_DIR/autolatex/config/cli"
  mkdir -pv "$DEST_DIR/autolatex/config/plugin"
  mkdir -pv "$DEST_DIR/autolatex/ui"
  mkdir -pv "$DEST_DIR/autolatex/utils"
  mkdir -pv "$DEST_DIR/autolatex/widgets"

  ln -sv "$SOURCE_DIR/"*.plugin "$DEST_DIR/"
  ln -sv "$SOURCE_DIR/autolatex/"*.py "$DEST_DIR/autolatex/"
  ln -sv "$SOURCE_DIR/autolatex/icons" "$DEST_DIR/autolatex/"
  ln -sv "$SOURCE_DIR/autolatex/config/"*.py "$DEST_DIR/autolatex/config"
  ln -sv "$SOURCE_DIR/autolatex/config/cli/"*.py "$DEST_DIR/autolatex/config/cli"
  ln -sv "$SOURCE_DIR/autolatex/config/plugin/"*.py "$DEST_DIR/autolatex/config/plugin"
  ln -sv "$SOURCE_DIR/autolatex/ui/"*.ui "$DEST_DIR/autolatex/ui"
  ln -sv "$SOURCE_DIR/autolatex/utils/"*.py "$DEST_DIR/autolatex/utils"
  ln -sv "$SOURCE_DIR/autolatex/widgets/"*.py "$DEST_DIR/autolatex/widgets"

  mv -fv "$AUTOLATEX_DIR/default.cfg" "$AUTOLATEX_DIR/default.cfg.orig"
  cp -fv "$AUTOLATEX_DIR/default_debug.cfg" "$AUTOLATEX_DIR/default.cfg"

elif [ "$1" = "remove" ]
then
  rm -rfv "$DEST_DIR/autolatex"
  rm -fv "$DEST_DIR/autolatex.plugin"

  cd "$AUTOLATEX_DIR"
  mv -fv default.cfg.orig default.cfg 2>/dev/null
else
  echo "`basename $0` install|remove" >&2
  exit 255
fi
