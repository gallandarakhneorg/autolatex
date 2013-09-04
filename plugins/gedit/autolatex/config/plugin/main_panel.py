# autolatex/config/plugin/main_panel.py
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
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the plugin
class Panel(Gtk.Grid):

	def __init__(self, settings, window):
		Gtk.Grid.__init__(self)
		self.set_row_homogeneous(False)
		self.set_column_homogeneous(False)
		self.set_row_spacing(5)
		self.set_property('orientation', Gtk.Orientation.VERTICAL)
		self.set_property('margin', 5)
		self.set_property('vexpand', False)
		self._settings = settings
		self.window = window

		# Create the components

		# Row 1: Paths
		ui_frame = Gtk.Frame()
		ui_frame.set_label(_T("Paths of the tools"));
		ui_frame.set_property('margin', 5)
		self.add(ui_frame)
		ui_table = Gtk.Grid()
		ui_table.set_row_homogeneous(True)
		ui_table.set_column_homogeneous(False)
		ui_table.set_row_spacing(5)
		ui_table.set_column_spacing(5)
		ui_table.set_property('margin', 5)
		ui_frame.add(ui_table)
		label = _T("Path of 'autolatex'")
		ui_label = Gtk.Label(label)
		ui_label.set_property('hexpand', False)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(ui_label, 
				0,0,1,1) # left, top, width, height
		self._ui_edit_autolatex_cmd = Gtk.FileChooserButton()
		self._ui_edit_autolatex_cmd.set_width_chars(40)
		self._ui_edit_autolatex_cmd.set_title(label)
		self._ui_edit_autolatex_cmd.set_create_folders(False)
		self._ui_edit_autolatex_cmd.set_property('hexpand', True)
		self._ui_edit_autolatex_cmd.set_property('vexpand', False)
		ui_table.attach(self._ui_edit_autolatex_cmd, 
				1,0,1,1) # left, top, width, height
		label = _T("Path to 'autolatex-backend'")
		ui_label = Gtk.Label(label)
		ui_label.set_property('hexpand', False)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(ui_label, 
				0,1,1,1) # left, right, top and bottom columns
		self._ui_edit_autolatex_backend_cmd = Gtk.FileChooserButton()
		self._ui_edit_autolatex_backend_cmd.set_width_chars(40)
		self._ui_edit_autolatex_backend_cmd.set_title(label)
		self._ui_edit_autolatex_backend_cmd.set_create_folders(False)
		self._ui_edit_autolatex_backend_cmd.set_property('hexpand', True)
		self._ui_edit_autolatex_backend_cmd.set_property('vexpand', False)
		ui_table.attach(self._ui_edit_autolatex_backend_cmd, 
				1,1,1,1) # left, top, width, height

		# Row 2: SyncTex
		ui_frame = Gtk.Frame()
		ui_frame.set_label(_T("SyncTeX"));
		ui_frame.set_property('margin', 5)
		self.add(ui_frame)
		ui_table = Gtk.Grid()
		ui_table.set_row_homogeneous(True)
		ui_table.set_column_homogeneous(False)
		ui_table.set_row_spacing(5)
		ui_table.set_column_spacing(5)
		ui_table.set_property('margin', 5)
		ui_frame.add(ui_table)
		ui_label = Gtk.Label(_T("Enable SyncTeX (overriding the configurations)"))
		ui_label.set_property('hexpand', True)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(ui_label, 
				0,0,1,1) # left, right, width, height
		self._ui_use_synctex = Gtk.Switch()
		self._ui_use_synctex.set_property('hexpand', False)
		self._ui_use_synctex.set_property('vexpand', False)
		self._ui_use_synctex.set_property('halign', Gtk.Align.END)
		self._ui_use_synctex.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(self._ui_use_synctex, 
				1,0,1,1) # left, top, width, height

		# Row 3: UI parameters
		ui_frame = Gtk.Frame()
		ui_frame.set_label(_T("Configuration of the UI"));
		ui_frame.set_property('margin', 5)
		self.add(ui_frame)
		ui_table = Gtk.Grid()
		ui_table.set_row_homogeneous(True)
		ui_table.set_column_homogeneous(False)
		ui_table.set_row_spacing(5)
		ui_table.set_column_spacing(5)
		ui_table.set_property('margin', 5)
		ui_frame.add(ui_table)
		ui_label = Gtk.Label(_T("Show the progress info bar"))
		ui_label.set_property('hexpand', True)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(ui_label, 
				0,0,1,1) # left, right, width, height
		self._ui_show_progress_info_bar = Gtk.Switch()
		self._ui_show_progress_info_bar.set_property('hexpand', False)
		self._ui_show_progress_info_bar.set_property('vexpand', False)
		self._ui_show_progress_info_bar.set_property('halign', Gtk.Align.END)
		self._ui_show_progress_info_bar.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(self._ui_show_progress_info_bar, 
				1,0,1,1) # left, top, width, height

		# Row 4: Document parameters
		ui_frame = Gtk.Frame()
		ui_frame.set_label(_T("Configuration of the documents"));
		ui_frame.set_property('margin', 5)
		self.add(ui_frame)
		ui_table = Gtk.Grid()
		ui_table.set_row_homogeneous(True)
		ui_table.set_column_homogeneous(False)
		ui_table.set_row_spacing(5)
		ui_table.set_column_spacing(5)
		ui_table.set_property('margin', 5)
		ui_frame.add(ui_table)
		ui_label = Gtk.Label(_T("Save before running AutoLaTeX"))
		ui_label.set_property('hexpand', True)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(ui_label, 
				0,0,1,1) # left, right, width, height
		self._ui_save_before_run = Gtk.Switch()
		self._ui_save_before_run.set_property('hexpand', False)
		self._ui_save_before_run.set_property('vexpand', False)
		self._ui_save_before_run.set_property('halign', Gtk.Align.END)
		self._ui_save_before_run.set_property('valign', Gtk.Align.CENTER)
		ui_table.attach(self._ui_save_before_run, 
				1,0,1,1) # left, top, width, height

		# Set the initial values
		self.on_initialize_fields()
		# Attach signals
		self._ui_hierarchy_connect_id = self.connect('hierarchy-changed', self.on_hierarchy_changed)

	def on_hierarchy_changed(self, widget, previous_toplevel, data=None):
		if previous_toplevel:
			self._settings.disconnect('autolatex-cmd')
			self._settings.disconnect('autolatex-backend-cmd')
			self._settings.disconnect('force-synctex')
			self._settings.disconnect('show-progress-info')
			self._settings.disconnect('save-before-run-autolatex')
			self.disconnect(self._ui_hierarchy_connect_id)
			self.on_save_changes()
		else:
			self._settings.connect('autolatex-cmd', self.on_gsettings_changed)
			self._settings.connect('autolatex-backend-cmd', self.on_gsettings_changed)
			self._settings.connect('force-synctex', self.on_gsettings_changed)
			self._settings.connect('show-progress-info', self.on_gsettings_changed)
			self._settings.connect('save-before-run-autolatex', self.on_gsettings_changed)

	# Invoked when the different fields in the preference box must be initialized
	def on_initialize_fields(self):
		cmd = self._settings.get_autolatex_cmd()
		if cmd:	self._ui_edit_autolatex_cmd.set_filename(cmd)
		else: self._ui_edit_autolatex_cmd.unselect_all()
		cmd = self._settings.get_autolatex_backend_cmd()
		if cmd:	self._ui_edit_autolatex_backend_cmd.set_filename(cmd)
		else: self._ui_edit_autolatex_backend_cmd.unselect_all()
		flag = self._settings.get_force_synctex()
		self._ui_use_synctex.set_active(flag)
		flag = self._settings.get_progress_info_visibility()
		self._ui_show_progress_info_bar.set_active(flag)
		flag = self._settings.get_save_before_run_autolatex()
		self._ui_save_before_run.set_active(flag)

	# Invoked when the changes in the preference dialog box should be saved
	def on_save_changes(self):
		filename = self._ui_edit_autolatex_cmd.get_filename()
		self._settings.set_autolatex_cmd(filename)
		filename = self._ui_edit_autolatex_backend_cmd.get_filename()
		self._settings.set_autolatex_backend_cmd(filename)
		force_synctex = self._ui_use_synctex.get_active()
		self._settings.set_force_synctex(force_synctex)
		show_info_bar = self._ui_show_progress_info_bar.get_active()
		self._settings.set_progress_info_visibility(show_info_bar)
		save_before_run = self._ui_save_before_run.get_active()
		self._settings.set_save_before_run_autolatex(save_before_run)
	
	def on_gsettings_changed(self, settings, key, data=None):
		if key == 'autolatex-cmd':
			gsettings_cmd = self._settings.get_autolatex_cmd()
			window_cmd = self._ui_edit_autolatex_cmd.get_filename()
			if gsettings_cmd != window_cmd:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _T("The path of AutoLaTeX has been changed by an external software. The new path is different from the one you have entered. Do you want to use the new path?"))
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					if gsettings_cmd: self._ui_edit_autolatex_cmd.set_filename(gsettings_cmd)
					else: self._ui_edit_autolatex_cmd.unselect_all()
		elif key == 'autolatex-backend-cmd':
			gsettings_cmd = self._settings.get_autolatex_backend_cmd()
			window_cmd = self._ui_edit_autolatex_backend_cmd.get_filename()
			if gsettings_cmd != window_cmd:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _T("The path of AutoLaTeX Backend has been changed by an external software. The new path is different from the one you have entered. Do you want to use the new path?"))
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					if gsettings_cmd: self._ui_edit_autolatex_backend_cmd.set_filename(gsettings_cmd)
					else: self._ui_edit_autolatex_backend_cmd.unselect_all()
		elif key == 'force-synctex':
			gsettings_flag = self._settings.get_force_synctex()
			window_flag = self._ui_use_synctex.get_active()
			if gsettings_flag != window_flag:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _T("The enabling flag for SyncTeX has been changed by an external software. The new flag is different from the one inside the preference dialog box. Do you want to use the new flag?"))
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					self._ui_use_synctex.set_active(gsettings_flag)
		elif key == 'show-progress-info':
			gsettings_flag = self._settings.get_progress_info_visibility()
			window_flag = self._ui_show_progress_info_bar.get_active()
			if gsettings_flag != window_flag:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _T("The enabling flag for the progress info bar has been changed by an external software. The new flag is different from the one inside the preference dialog box. Do you want to use the new flag?"))
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					self._ui_show_progress_info_bar.set_active(gsettings_flag)
		elif key == 'save-before-run-autolatex':
			gsettings_flag = self._settings.get_save_before_run_autolatex()
			window_flag = self._ui_save_before_run.get_active()
			if gsettings_flag != window_flag:
				dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _T("The flag to save before running AutoLaTeX has been changed by an external software. The new flag is different from the one inside the preference dialog box. Do you want to use the new flag?"))
				answer = dialog.run()
				dialog.destroy()
				if  answer == Gtk.ResponseType.YES:
					self._ui_show_progress_info_bar.set_active(gsettings_flag)

