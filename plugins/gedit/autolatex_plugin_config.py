# autolatex - autolatex_plugin_config.py
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

# Include the Gtk libraries
from gi.repository import Gtk

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the plugin
class Panel(Gtk.Table):

	def __init__(self, settings):
		Gtk.Table.__init__(self,
				2, #rows
				3, #columns
				False) #non uniform
		self._settings = settings
		# Create the components
		label = "Path to autolatex"
		ui_label = Gtk.Label(label)
		self.attach(ui_label, 
				0,1,0,1, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK, # x and y options
				0,0) # horizontal and vertical paddings
		self._ui_edit_autolatex_cmd = Gtk.FileChooserButton()
		self._ui_edit_autolatex_cmd.set_width_chars(40)
		self._ui_edit_autolatex_cmd.set_title(label)
		self._ui_edit_autolatex_cmd.set_create_folders(False)
		self.attach(self._ui_edit_autolatex_cmd, 
				1,2,0,1, # left, right, top and bottom columns
				Gtk.AttachOptions.FILL|Gtk.AttachOptions.EXPAND, # x options
				Gtk.AttachOptions.SHRINK, # y options
				0,0) # horizontal and vertical paddings
		self._ui_error_autolatex_cmd = Gtk.Image()
		self.attach(self._ui_error_autolatex_cmd, 
				2,3,0,1, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, # x options
				Gtk.AttachOptions.SHRINK, # y options
				0,0) # horizontal and vertical paddings
		label = "Path to autolatex-backend"
		ui_label = Gtk.Label(label)
		self.attach(ui_label, 
				0,1,1,2, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK, # x and y options
				0,0) # horizontal and vertical paddings
		self._ui_edit_autolatex_backend_cmd = Gtk.FileChooserButton()
		self._ui_edit_autolatex_backend_cmd.set_width_chars(40)
		self._ui_edit_autolatex_backend_cmd.set_title(label)
		self._ui_edit_autolatex_backend_cmd.set_create_folders(False)
		self.attach(self._ui_edit_autolatex_backend_cmd, 
				1,2,1,2, # left, right, top and bottom columns
				Gtk.AttachOptions.FILL|Gtk.AttachOptions.EXPAND, # x options
				Gtk.AttachOptions.SHRINK, # y options
				0,0) # horizontal and vertical paddings
		# Set the initial values
		self._ui_edit_autolatex_cmd.set_filename(self._settings.get_autolatex_cmd())
		self._ui_edit_autolatex_backend_cmd.set_filename(self._settings.get_autolatex_backend_cmd())
		# Attach signals
		self._ui_hierarchy_connect_id = self.connect('hierarchy-changed', self.on_hierarchy_changed)

	def on_hierarchy_changed(self, widget, previous_toplevel, data=None):
		if previous_toplevel:
			self._settings.disconnect('autolatex_cmd')
			self._settings.disconnect('autolatex_backend_cmd')
			self._ui_edit_autolatex_cmd.disconnect(self._ui_edit_autolatex_cmd_connect_id)
			self._ui_edit_autolatex_backend_cmd.disconnect(self._ui_edit_autolatex_backend_cmd_connect_id)
			self.disconnect(self._ui_hierarchy_connect_id)
		else:
			self._ui_edit_autolatex_cmd_connect_id = self._ui_edit_autolatex_cmd.connect('file-set', self.on_autolatex_cmd_field_changed)
			self._ui_edit_autolatex_backend_cmd_connect_id = self._ui_edit_autolatex_backend_cmd.connect('file-set', self.on_autolatex_backend_cmd_field_changed)
			self._settings.connect('autolatex_cmd', self.on_gsettings_changed)
			self._settings.connect('autolatex_backend_cmd', self.on_gsettings_changed)
	
	def on_gsettings_changed(self, settings, key, data=None):
		if key == 'autolatex_cmd':
			self._ui_edit_autolatex_cmd.set_filename(self._settings.get_autolatex_cmd())
		elif key == 'autolatex_backend_cmd':
			self._ui_edit_autolatex_backend_cmd.set_filename(self._settings.get_autolatex_backend_cmd())
		
	def on_autolatex_cmd_field_changed(self, widget, data=None):
		filename = self._ui_edit_autolatex_cmd.get_filename()
		self._settings.set_autolatex_cmd(filename)
		if filename != self._settings.get_autolatex_cmd():
			self._ui_error_autolatex_cmd.set_from_stock(Gtk.STOCK_STOP, Gtk.IconSize.MENU)
		else:
			self._ui_error_autolatex_cmd.clear()

	def on_autolatex_backend_cmd_field_changed(self, widget, data=None):
		self._settings.set_autolatex_backend_cmd(self._ui_edit_autolatex_backend_cmd.get_filename())

