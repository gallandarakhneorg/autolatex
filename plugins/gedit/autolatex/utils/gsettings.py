#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/utils/gsettings.py
# Copyright (C) 2013  Stephane Galland <galland@arakhne.org>
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
# Class that is managing the settings
#---------------------------------

class Manager:

	def _is_schema_installed():
		for schema in Gio.Settings.list_schemas():
			if schema == _GSETTINGS_BASE_KEY:
				return True
		return False
	_is_schema_installed = staticmethod(_is_schema_installed)
	
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

	def unbind(self):
		if self.settings:
			self.settings.disconnect(self._sig_autolatex_cmd_changed)
			self.settings.disconnect(self._sig_autolatex_backend_cmd_changed)
			for datakey in self._sig_binded_signals:
				self.settings.disconnect(self._sig_binded_signals[datakey])
			self._sig_binded_signals = {}
			self.settings.apply()

	def connect(self, datakey, callback):
		if self.settings:
			self._sig_binded_signals[datakey] = self.settings.connect("changed::"+str(datakey), callback)

	def disconnect(self, datakey):
		if self.settings:
			self.settings.disconnect(self._sig_binded_signals[datakey])
			del self._sig_binded_signals[datakey]

	def _update_autolatex_cmd(self, cmd):
		if cmd and os.path.isfile(cmd) and os.access(cmd, os.X_OK):
			utils.AUTOLATEX_BINARY = cmd
		else:
			utils.AUTOLATEX_BINARY = utils.DEFAULT_AUTOLATEX_BINARY

	def _update_autolatex_backend_cmd(self, cmd):
		if cmd and os.path.isfile(cmd) and os.access(cmd, os.X_OK):
			utils.AUTOLATEX_BACKEND_BINARY = cmd
		else:
			utils.AUTOLATEX_BACKEND_BINARY = utils.DEFAULT_AUTOLATEX_BACKEND_BINARY

	def on_autolatex_cmd_changed(self, settings, key, data=None):
		if self.settings:
			self._update_autolatex_cmd(self.settings.get_string('autolatex-cmd'))

	def on_autolatex_backend_cmd_changed(self, settings, key, data=None):
		if self.settings:
			self._update_autolatex_backend_cmd(self.settings.get_string('autolatex-backend-cmd'))

	def get_autolatex_cmd(self):
		if self.settings:
			path = self.settings.get_string('autolatex-cmd')
			return path if path else None
		else:
			return None

	def set_autolatex_cmd(self,path):
		if self.settings:
			path = str(path) if path else ''
			self.settings.set_string('autolatex-cmd', path)
			self.settings.apply()
		else:
			self._update_autolatex_cmd(path)

	def get_autolatex_backend_cmd(self):
		if self.settings:
			path = self.settings.get_string('autolatex-backend-cmd')
			return path if path else None
		else:
			return None

	def set_autolatex_backend_cmd(self, path):
		if self.settings:
			path = str(path) if path else ''
			self.settings.set_string('autolatex-backend-cmd', path)
			self.settings.apply()
		else:
			self._update_autolatex_backend_cmd(path)

	def get_force_synctex(self):
		if self.settings:
			return self.settings.get_boolean('force-synctex')
		else:
			return self._data['force-synctex']

	def set_force_synctex(self, is_force):
		if self.settings:
			self.settings.set_boolean('force-synctex', bool(is_force))
			self.settings.apply()
		else:
			self._data['force-synctex'] = bool(is_force)

	def get_progress_info_visibility(self):
		if self.settings:
			return self.settings.get_boolean('show-progress-info')
		else:
			return self._data['show-progress-info']

	def set_progress_info_visibility(self, is_shown):
		if self.settings:
			self.settings.set_boolean('show-progress-info', bool(is_shown))
			self.settings.apply()
		else:
			self._data['show-progress-info'] = bool(is_shown)

	def get_save_before_run_autolatex(self):
		if self.settings:
			return self.settings.get_boolean('save-before-run-autolatex')
		else:
			return self._data['save-before-run-autolatex']

	def set_save_before_run_autolatex(self, is_saving):
		if self.settings:
			self.settings.set_boolean('save-before-run-autolatex', bool(is_saving))
			self.settings.apply()
		else:
			self._data['save-before-run-autolatex'] = bool(is_saving)

