# autolatex - autolatex_figure_panel.py
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
# Include the Glib, Gtk and Gedit libraries
from gi.repository import Gtk, Gio
# AutoLaTeX internal libs
import autolatex_utils as utils

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the figures
class Panel(Gtk.Table):
	__gtype_name__ = "AutoLaTeXFigurePanel"

	def __init__(self, is_document_level, directory, window):
		Gtk.Table.__init__(self,
				3, #rows
				2, #columns
				False) #non uniform
		self._is_document_level = is_document_level
		self._directory = directory
		self.window = window

		hbox = Gtk.HBox()
		self.attach(	hbox,
				0,2,0,1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		ui_label = Gtk.Label("Automatic generation of pictures with translators")
		ui_label.set_alignment(0, 0.5)
		hbox.add(ui_label)
		self._ui_is_figure_generated_checkbox = Gtk.Switch()
		hbox.add(self._ui_is_figure_generated_checkbox)

		self._ui_figure_path_label = Gtk.Label("Search paths for the pictures")
		self._ui_figure_path_label.set_alignment(0, 0.5)
		self.attach(	self._ui_figure_path_label,
				0,1,1,2, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,2); # horizontal and vertical paddings
		self._ui_figure_path_label.set_justify(Gtk.Justification.LEFT)
		hbox = Gtk.HButtonBox()
		self.attach(	hbox,
				1,2,1,2, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,2); # horizontal and vertical paddings
		self._ui_figure_path_add_button = Gtk.Button()
		self._ui_figure_path_add_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_add_button)
		self._ui_figure_path_remove_button = Gtk.Button()
		self._ui_figure_path_remove_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_remove_button)
		self._ui_figure_path_up_button = Gtk.Button()
		self._ui_figure_path_up_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_up_button)
		self._ui_figure_path_down_button = Gtk.Button()
		self._ui_figure_path_down_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GO_DOWN, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_down_button)
		self._ui_figure_path_store = Gtk.ListStore(str)
		self._ui_figure_path_widget = Gtk.TreeView()
		self._ui_figure_path_widget.set_model(self._ui_figure_path_store)
		self._ui_figure_path_widget.append_column(Gtk.TreeViewColumn("path", Gtk.CellRendererText(), text=0))
		self._ui_figure_path_widget.set_headers_clickable(False)
		self._ui_figure_path_widget.set_headers_visible(False)
		self._ui_figure_path_selection = self._ui_figure_path_widget.get_selection()
		self._ui_figure_path_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
		self._ui_figure_path_scroll = Gtk.ScrolledWindow()
		self._ui_figure_path_scroll.add(self._ui_figure_path_widget)
		self._ui_figure_path_scroll.set_size_request(200,100)
		self._ui_figure_path_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
		self._ui_figure_path_scroll.set_shadow_type(Gtk.ShadowType.IN)
		self.attach(	self._ui_figure_path_scroll, 
				0,2,2,3, # left, right, top and bottom columns
				Gtk.AttachOptions.FILL|Gtk.AttachOptions.EXPAND, # x option
				Gtk.AttachOptions.SHRINK, # y options
				5,5) # horizontal and vertical paddings
		#
		# Initialize the content
		#
		self._settings = utils.backend_get_configuration(
						self._directory,
						'project' if self._is_document_level else 'user',
						'generation')
		self._ui_is_figure_generated_checkbox.set_active(self._get_settings_bool('generate images', True))
		full_path = self._get_settings_str('image directory', '')
		if full_path:
			full_path = full_path.split(os.pathsep)
			for path in full_path:
				self._ui_figure_path_store.append( [ path.strip() ] )
		self._tmp_figure_path_moveup = False
		self._tmp_figure_path_movedown = False
		self._update_widget_states()
		#
		# Connect signals
		#
		self._ui_is_figure_generated_checkbox.connect('button-release-event',self.on_generate_image_toggled)
		self._ui_figure_path_selection.connect('changed',self.on_figure_path_selection_changed)
		self._ui_figure_path_add_button.connect('clicked',self.on_figure_path_add_button_clicked)
		self._ui_figure_path_remove_button.connect('clicked',self.on_figure_path_remove_button_clicked)
		self._ui_figure_path_up_button.connect('clicked',self.on_figure_path_up_button_clicked)
		self._ui_figure_path_down_button.connect('clicked',self.on_figure_path_down_button_clicked)

	# Utility function to extract a string value from the settings
	def _get_settings_str(self, key, default_value=''):
		if self._settings.has_option('generation', key):
			return str(self._settings.get('generation', key))
		else:
			return str(default_value)

	# Utility function to extract a boolean value from the settings
	def _get_settings_bool(self, key, default_value=False):
		if self._settings.has_option('generation', key):
			return bool(self._settings.getboolean('generation', key))
		else:
			return bool(default_value)

	# Change the state of the widgets according to the state of other widgets
	def _update_widget_states(self):
		if self._ui_is_figure_generated_checkbox.get_active():
			self._ui_figure_path_label.set_sensitive(True)
			self._ui_figure_path_add_button.set_sensitive(True)
			self._ui_figure_path_widget.set_sensitive(True)
			if self._ui_figure_path_selection.count_selected_rows() > 0:
				self._ui_figure_path_remove_button.set_sensitive(True)
				self._ui_figure_path_up_button.set_sensitive(self._tmp_figure_path_moveup)
				self._ui_figure_path_down_button.set_sensitive(self._tmp_figure_path_movedown)
			else:
				self._ui_figure_path_remove_button.set_sensitive(False)
				self._ui_figure_path_up_button.set_sensitive(False)
				self._ui_figure_path_down_button.set_sensitive(False)
		else:
			self._ui_figure_path_label.set_sensitive(False)
			self._ui_figure_path_add_button.set_sensitive(False)
			self._ui_figure_path_widget.set_sensitive(False)
			self._ui_figure_path_remove_button.set_sensitive(False)
			self._ui_figure_path_up_button.set_sensitive(False)
			self._ui_figure_path_down_button.set_sensitive(False)

	# Invoke when the flag 'generate images' has changed
	def on_generate_image_toggled(self, widget, data=None):
		self._update_widget_states()

	def _check_figure_path_up_down(self, selection):
		n_data = len(self._ui_figure_path_store)
		self._tmp_figure_path_moveup = False
		self._tmp_figure_path_movedown = False
		selected_rows = selection.get_selected_rows()[1]
		i = 0
		last_row = len(selected_rows)-1
		while (i<=last_row and (not self._tmp_figure_path_moveup or not self._tmp_figure_path_movedown)):
			c_idx = selected_rows[i].get_indices()[0]
			if (i==0 and c_idx>0) or (i>0 and c_idx-1 > selected_rows[i-1].get_indices()[0]):
				self._tmp_figure_path_moveup = True
			if (i==last_row and c_idx<n_data-1) or (i<last_row and c_idx+1 < selected_rows[i+1].get_indices()[0]):
				self._tmp_figure_path_movedown = True
			i = i + 1

	# Invoked when the selection in the lsit of figure paths has changed
	def on_figure_path_selection_changed(self, selection, data=None):
		self._check_figure_path_up_down(selection)
		self._update_widget_states()

	# Invoked when the button "Add figure figure" was clicked
	def on_figure_path_add_button_clicked(self, button, data=None):
		dialog = Gtk.FileChooserDialog("Select a figure path", 
						self.window,
						Gtk.FileChooserAction.SELECT_FOLDER,
						[ Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
						  Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT ])
		dialog.set_modal(True)
		response = dialog.run()
		filename = dialog.get_filename()
		dialog.destroy()
		if response == Gtk.ResponseType.ACCEPT:
			if self._is_document_level:
				c = Gio.File.new_for_path(filename)
				p = Gio.File.new_for_path(self._directory)
				r = p.get_relative_path(c)
				if r: filename = r
			self._ui_figure_path_store.append( [filename] )

	# Invoked when the button "Remove figure figure" was clicked
	def on_figure_path_remove_button_clicked(self, button, data=None):
		count = self._ui_figure_path_selection.count_selected_rows()
		if count > 0:
			selections = self._ui_figure_path_selection.get_selected_rows()[1]
			for i in range(len(selections)-1, -1, -1):
				list_iter = self._ui_figure_path_store.get_iter(selections[i])
				self._ui_figure_path_store.remove(list_iter)

	# Invoked when the button "Move up the figure paths" was clicked
	def on_figure_path_up_button_clicked(self, button, data=None):
		n_sel = self._ui_figure_path_selection.count_selected_rows()
		if n_sel > 0:
			selected_rows = self._ui_figure_path_selection.get_selected_rows()[1]
			movable = False
			p_idx = -1
			for i in range(0, n_sel):
				c_idx = selected_rows[i].get_indices()[0]
				if not movable and c_idx-1>p_idx: movable = True
				if movable:
					self._ui_figure_path_store.swap(
							self._ui_figure_path_store.get_iter(
								Gtk.TreePath(c_idx-1)),
							self._ui_figure_path_store.get_iter(selected_rows[i]))
				else: p_idx = c_idx
		self._check_figure_path_up_down(self._ui_figure_path_selection)
		self._update_widget_states()

	# Invoked when the button "Move down the figure paths" was clicked
	def on_figure_path_down_button_clicked(self, button, data=None):
		n_sel = self._ui_figure_path_selection.count_selected_rows()
		if n_sel > 0:
			selected_rows = self._ui_figure_path_selection.get_selected_rows()[1]
			movable = False
			p_idx = len(self._ui_figure_path_store)
			for i in range(n_sel-1, -1, -1):
				c_idx = selected_rows[i].get_indices()[0]
				if not movable and c_idx+1<p_idx: movable = True
				if movable:
					self._ui_figure_path_store.swap(
							self._ui_figure_path_store.get_iter(
								Gtk.TreePath(c_idx+1)),
							self._ui_figure_path_store.get_iter(selected_rows[i]))
				else: p_idx = c_idx
		self._check_figure_path_up_down(self._ui_figure_path_selection)
		self._update_widget_states()

	# Invoked when the changes in the panel must be saved
	def save(self):
		self._settings.remove_section('generation')
		self._settings.add_section('generation')
		self._settings.set('generation', 'generate images', 
				'true' if self._ui_is_figure_generated_checkbox.get_active() else 'false')
		path = ''
		for row in self._ui_figure_path_store:
			if path: path = path + os.pathsep
			path = path + row[0].strip()
		self._settings.set('generation', 'image directory', path)
		return utils.backend_set_configuration(self._directory, 'project' if self._is_document_level else 'user', self._settings)
