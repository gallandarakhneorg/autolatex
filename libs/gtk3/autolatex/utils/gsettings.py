#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-14  Stephane Galland <galland@arakhne.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

#---------------------------------
# IMPORTS
#---------------------------------

# Standard libraries
import os
# Include the Gio, Gtk and Gedit libraries
from gi.repository import Gio, Gtk
# AutoLaTeX internal libs
from . import utils

#---------------------------------
# Constants
#---------------------------------

_GSETTINGS_BASE_KEY = "apps.autolatex"

#---------------------------------
# CLASS: Manager
#---------------------------------

#
# Manager of settings in the standard Gnome settings (gsettings).
#
class Manager:

  # Replies if the Gsettings schemas associated to AutoLaTeX are installed.
  def _is_schema_installed():
    for schema in Gio.Settings.list_schemas():
      if schema == _GSETTINGS_BASE_KEY:
        return True
    return False
  _is_schema_installed = staticmethod(_is_schema_installed)
  
  # Constructor.
  def __init__(self):
    if Manager._is_schema_installed(): 
      self._sig_binded_signals = {}
      self.settings = Gio.Settings.new(_GSETTINGS_BASE_KEY)
      # Force application of gsettings
      self._update_autolatex_cmd(self.settings.get_string('autolatex-cmd'))
      self._update_autolatex_backend_cmd(self.settings.get_string('autolatex-backend-cmd'))
      # Listen on changes
      self._sig_autolatex_cmd_changed = self.settings.connect("changed::autolatex-cmd", self.on_autolatex_cmd_changed)
      self._sig_autolatex_backend_cmd_changed = self.settings.connect("changed::autolatex-backend-cmd", self.on_autolatex_backend_cmd_changed)
    else:
      self.settings = None
      self._data = {
        'force-synctex': True,
        'show-progress-info': True,
        'save-before-run-autolatex': True,
      }

  # Unbind this manager to the Gsettings daemon.
  def unbind(self):
    if self.settings:
      self.settings.disconnect(self._sig_autolatex_cmd_changed)
      self.settings.disconnect(self._sig_autolatex_backend_cmd_changed)
      for datakey in self._sig_binded_signals:
        self.settings.disconnect(self._sig_binded_signals[datakey])
      self._sig_binded_signals = {}
      self.settings.apply()

  # Connect this manager to the Gsettings daemon for the given key.
  # The Gsettings daemon will notify the given callback each time
  # the value associated with the given key has changed.
  # @param datakey - key of the data to be connected to.
  # @param callback
  def connect(self, datakey, callback):
    if self.settings:
      self._sig_binded_signals[datakey] = self.settings.connect("changed::"+str(datakey), callback)

  # Disconnect this manager to the Gsettings daemon for the given key.
  def disconnect(self, datakey):
    if self.settings:
      self.settings.disconnect(self._sig_binded_signals[datakey])
      del self._sig_binded_signals[datakey]

  # Invoked to set the command line of AutoLaTeX frontend program.
  def _update_autolatex_cmd(self, cmd):
    if cmd and os.path.isfile(cmd) and os.access(cmd, os.X_OK):
      utils.AUTOLATEX_BINARY = cmd
    else:
      utils.AUTOLATEX_BINARY = utils.DEFAULT_AUTOLATEX_BINARY

  # Invoked to set the command line of the AutoLaTeX backend program.
  def _update_autolatex_backend_cmd(self, cmd):
    if cmd and os.path.isfile(cmd) and os.access(cmd, os.X_OK):
      utils.AUTOLATEX_BACKEND_BINARY = cmd
    else:
      utils.AUTOLATEX_BACKEND_BINARY = utils.DEFAULT_AUTOLATEX_BACKEND_BINARY

  # Invoked when the command line of the AutoLaTeX frontend program
  # has been detected has changed in the Gsettings deamon.
  def on_autolatex_cmd_changed(self, settings, key, data=None):
    if self.settings:
      self._update_autolatex_cmd(self.settings.get_string('autolatex-cmd'))

  # Invoked when the command line of the AutoLaTeX backend program
  # has been detected has changed in the Gsettings deamon.
  def on_autolatex_backend_cmd_changed(self, settings, key, data=None):
    if self.settings:
      self._update_autolatex_backend_cmd(self.settings.get_string('autolatex-backend-cmd'))

  # Replies the command line of the AutoLaTeX frontend program.
  def get_autolatex_cmd(self):
    if self.settings:
      path = self.settings.get_string('autolatex-cmd')
      return path if path else None
    else:
      return None

  # Change the command line of the AutoLaTeX frontend program.
  def set_autolatex_cmd(self,path):
    if self.settings:
      path = str(path) if path else ''
      self.settings.set_string('autolatex-cmd', path)
      self.settings.apply()
    else:
      self._update_autolatex_cmd(path)

  # Replies the command line of the AutoLaTeX backend program.
  def get_autolatex_backend_cmd(self):
    if self.settings:
      path = self.settings.get_string('autolatex-backend-cmd')
      return path if path else None
    else:
      return None

  # Change the command line of the AutoLaTeX backend program.
  def set_autolatex_backend_cmd(self, path):
    if self.settings:
      path = str(path) if path else ''
      self.settings.set_string('autolatex-backend-cmd', path)
      self.settings.apply()
    else:
      self._update_autolatex_backend_cmd(path)

  # Replies if the flag "force SyncTeX" is set or unset.
  def get_force_synctex(self):
    if self.settings:
      return self.settings.get_boolean('force-synctex')
    else:
      return self._data['force-synctex']

  # Set or unset the flag "force SyncTeX".
  def set_force_synctex(self, is_force):
    if self.settings:
      self.settings.set_boolean('force-synctex', bool(is_force))
      self.settings.apply()
    else:
      self._data['force-synctex'] = bool(is_force)

  # Replies if progress information must be shown.
  def get_progress_info_visibility(self):
    if self.settings:
      return self.settings.get_boolean('show-progress-info')
    else:
      return self._data['show-progress-info']

  # Enable or disable the progress information.
  def set_progress_info_visibility(self, is_shown):
    if self.settings:
      self.settings.set_boolean('show-progress-info', bool(is_shown))
      self.settings.apply()
    else:
      self._data['show-progress-info'] = bool(is_shown)

  # Replies if the files must be saved before running AutoLaTeX.
  def get_save_before_run_autolatex(self):
    if self.settings:
      return self.settings.get_boolean('save-before-run-autolatex')
    else:
      return self._data['save-before-run-autolatex']

  # Set or unset the flag that indicates if the files must be saved
  # before running AutoLaTeX.
  def set_save_before_run_autolatex(self, is_saving):
    if self.settings:
      self.settings.set_boolean('save-before-run-autolatex', bool(is_saving))
      self.settings.apply()
    else:
      self._data['save-before-run-autolatex'] = bool(is_saving)

