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

	def __init__(self, settings, window):
		Gtk.Table.__init__(self,
				2, #rows
				2, #columns
				False) #non uniform
		self._settings = settings
		self.window = window

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
		cmd = self._settings.get_autolatex_cmd()
		if cmd:	self._ui_edit_autolatex_cmd.set_filename(cmd)
		else: self._ui_edit_autolatex_cmd.unselect_all()
		cmd = self._settings.get_autolatex_backend_cmd()
		if cmd:	self._ui_edit_autolatex_backend_cmd.set_filename(cmd)
		else: self._ui_edit_autolatex_backend_cmd.unselect_all()
		# Attach signals
		self._ui_hierarchy_connect_id = self.connect('hierarchy-changed', self.on_hierarchy_changed)

	def on_hierarchy_changed(self, widget, previous_toplevel, data=None):
		if previous_toplevel:
			self._settings.disconnect('autolatex-cmd')
			self._settings.disconnect('autolatex-backend-cmd')
			self.disconnect(self._ui_hierarchy_connect_id)
			# Set the autolatex-cmd
			filename = self._ui_edit_autolatex_cmd.get_filename()
			self._settings.set_autolatex_cmd(filename)
			filename = self._ui_edit_autolatex_backend_cmd.get_filename()
			self._settings.set_autolatex_backend_cmd(filename)
		else:
			self._settings.connect('autolatex-cmd', self.on_gsettings_changed)
			self._settings.connect('autolatex-backend-cmd', self.on_gsettings_changed)
	
	def on_gsettings_changed(self, settings, key, data=None):
		if key == 'autolatex-cmd':
			gsettings_cmd = self._settings.get_autolatex_cmd()
			window_cmd = self._ui_edit_autolatex_cmd.get_filename()
			if gsettings_cmd != window_cmd:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "The path of AutoLaTeX has been changed by an external program. The new path is different from the one you have entered. Do you want to use the new path?")
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					if gsettings_cmd: self._ui_edit_autolatex_cmd.set_filename(gsettings_cmd)
					else: self._ui_edit_autolatex_cmd.unselect_all()
		elif key == 'autolatex-backend-cmd':
			gsettings_cmd = self._settings.get_autolatex_backend_cmd()
			window_cmd = self._ui_edit_autolatex_backend_cmd.get_filename()
			if gsettings_cmd != window_cmd:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "The path of AutoLaTeX Backend has been changed by an external program. The new path is different from the one you have entered. Do you want to use the new path?")
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					if gsettings_cmd: self._ui_edit_autolatex_backend_cmd.set_filename(gsettings_cmd)
					else: self._ui_edit_autolatex_backend_cmd.unselect_all()

