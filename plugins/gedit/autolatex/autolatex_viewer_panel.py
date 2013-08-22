# autolatex - autolatex_viewer_panel.py
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

# Include the Glib, Gtk and Gedit libraries
from gi.repository import GObject, Gdk, Gtk, GdkPixbuf
# AutoLaTeX internal libs
import autolatex_utils as utils

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the viewer
class Panel(Gtk.Table):
	__gtype_name__ = "AutoLaTeXViewerPanel"

	def __init__(self, is_document_level, directory):
		Gtk.Table.__init__(self,
				2, #rows
				2, #columns
				False) #non uniform
		self._is_document_level = is_document_level
		self._directory = directory

		self._ui_launch_viewer_checkbox = Gtk.CheckButton(_T("Launch a viewer after compilation"))
		self.attach(	self._ui_launch_viewer_checkbox,
				0,2,0,1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		self._ui_viewer_command_label = Gtk.Label(_T("Command for launching the viewer (optional)"))
		self._ui_viewer_command_label.set_alignment(0, 0.5)
		self.attach(	self._ui_viewer_command_label, 
				0,1,1,2, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		self._ui_viewer_command_field = Gtk.Entry()
		self.attach(	self._ui_viewer_command_field,
				1,2,1,2, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		#
		# Initialize the content
		#
		self._settings = utils.backend_get_configuration(
						self._directory,
						'project' if self._is_document_level else 'user',
						'viewer')
		self._ui_launch_viewer_checkbox.set_active(self._get_settings_bool('view', True))
		self._ui_viewer_command_field.set_text(self._get_settings_str('viewer'))
		self._update_widget_states()
		#
		# Connect signals
		#
		self._ui_launch_viewer_checkbox.connect('toggled',self.on_launch_viewer_toggled)

	# Utility function to extract a string value from the settings
	def _get_settings_str(self, key, default_value=''):
		if self._settings.has_option('viewer', key):
			return str(self._settings.get('viewer', key))
		else:
			return str(default_value)

	# Utility function to extract a boolean value from the settings
	def _get_settings_bool(self, key, default_value=False):
		if self._settings.has_option('viewer', key):
			return bool(self._settings.getboolean('viewer', key))
		else:
			return bool(default_value)

	# Change the state of the widgets according to the state of other widgets
	def _update_widget_states(self):
		if self._ui_launch_viewer_checkbox.get_active():
			self._ui_viewer_command_label.set_sensitive(True)
			self._ui_viewer_command_field.set_sensitive(True)
		else:
			self._ui_viewer_command_label.set_sensitive(False)
			self._ui_viewer_command_field.set_sensitive(False)

	# Invoke when the flag 'launch viewer' has changed
	def on_launch_viewer_toggled(self, widget, data=None):
		self._update_widget_states()

	# Invoked when the changes in the panel must be saved
	def save(self):
		self._settings.remove_section('viewer')
		self._settings.add_section('viewer')
		self._settings.set('viewer', 'view', 
				'true' if self._ui_launch_viewer_checkbox.get_active() else 'false')
		self._settings.set('viewer', 'viewer', self._ui_viewer_command_field.get_text())
		return utils.backend_set_configuration(self._directory, 'project' if self._is_document_level else 'user', self._settings)
