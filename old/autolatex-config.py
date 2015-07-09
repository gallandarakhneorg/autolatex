#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Include the Gtk library
import gettext
import os
import argparse
from gi.repository import Gtk

# Only for debug
#import sys
#sys.path.append('/home/sgalland/git/autolatex/libs/gtk3')

# AutoLaTeX shared libs
from autolatex.utils import utils
from autolatex.config import window as cli_config

_T = gettext.gettext

utils.init_application_configuration(__file__, 'autolatex-config')

# Check if the AutoLaTeX is correctly installed
if not utils.AUTOLATEX_BINARY and not utils.AUTOLATEX_BACKEND_BINARY:
  dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _T("The programs 'autolatex' and 'autolatex-backend'\nwere not found.\nPlease fix the configuration of the AutoLaTeX plugin."))
  answer = dialog.run()
  dialog.destroy()
elif not utils.AUTOLATEX_BINARY:
  dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _T("The program 'autolatex' was not found.\nPlease fix the configuration of the AutoLaTeX plugin."))
  answer = dialog.run()
  dialog.destroy()
elif not utils.AUTOLATEX_BACKEND_BINARY:
  dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _T("The program 'autolatex-backend' was not found.\nPlease fix the configuration of the AutoLaTeX plugin."))
  answer = dialog.run()
  dialog.destroy()

# Parsing the command line
parser = argparse.ArgumentParser()
parser.add_argument("--user", help=_T("change the user configuration"), action="store_true")
parser.add_argument("--document", help=_T("change the document configuration"), action="store_true")
parser.add_argument("--create", help=_T("create the configuration file"), action="store_true")
parser.add_argument("--directory", help=_T("directory where the TeX file is located"))
args = parser.parse_args()

# Open the dialogs
if (args.user):

  config_file = utils.get_autolatex_user_config_file()
  path = args.directory
  if not path or not os.path.isdir(path):
    path = os.path.expanduser("~")
  if not os.path.isfile(config_file):
    if (args.create):
      fid = open(config_file, "a")
      if fid:
        fid.close()
      else:
        sys.stderr.write(_T("Unable to create the configuration file: %s\n") % config_file)
        exit(255)
    else:
      sys.stderr.write(_T("Unable to find a document, file not found: %s\n") % config_file)
      exit(255)
  cli_config.open_configuration_dialog(None, False, path)

else:

  path = args.directory
  if not path or not os.path.isdir(path):
    path = os.getcwd()
  directory = utils.find_AutoLaTeX_directory(path)
  if not directory:
    config_file = utils.get_autolatex_document_config_file(path)
    if (args.create):
      fid = open(config_file, "a")
      if fid:
        fid.close()
      else:
        sys.stderr.write(_T("Unable to create the configuration file: %s\n") % config_file)
        exit(255)
    else:
      sys.stderr.write(_T("Unable to find a document, file not found: %s\n") % config_file)
      exit(255)
  cli_config.open_configuration_dialog(None, True, directory)

exit(0)
