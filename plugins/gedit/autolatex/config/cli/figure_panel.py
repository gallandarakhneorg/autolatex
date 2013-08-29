# autolatex/config/cli/figure_panel.py
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
from ...utils import utils
from . import abstract_panel

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the figures
class Panel(abstract_panel.AbstractPanel):
	__gtype_name__ = "AutoLaTeXFigurePanel"

	def __init__(self, is_document_level, directory, window):
		abstract_panel.AbstractPanel.__init__(self, is_document_level, directory, window)
		

	#
	# Fill the grid
	#
	def _init_widgets(self):
		# Automatic generation of figures
		self._ui_is_figure_generated_checkbox = self._create_switch(
				_T("Automatic generation of pictures with translators"))[1]
		# Toolbar for the search paths
		self._ui_figure_path_label = self._create_label(
					_T("Search paths for the pictures"))
		hbox = Gtk.Box()
		hbox.set_property('orientation', Gtk.Orientation.HORIZONTAL)
		hbox.set_property('hexpand', False)
		hbox.set_property('vexpand', False)
		hbox.set_property('halign', Gtk.Align.END)
		hbox.set_property('valign', Gtk.Align.CENTER)
		self._insert_row(self._ui_figure_path_label, hbox)

		# Button 1
		self._ui_figure_path_add_button = Gtk.Button()
		self._ui_figure_path_add_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_add_button)
		# Button 2
		self._ui_figure_path_remove_button = Gtk.Button()
		self._ui_figure_path_remove_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_remove_button)
		# Button 3
		self._ui_figure_path_up_button = Gtk.Button()
		self._ui_figure_path_up_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_up_button)
		# Button 4
		self._ui_figure_path_down_button = Gtk.Button()
		self._ui_figure_path_down_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_GO_DOWN, Gtk.IconSize.BUTTON))
		hbox.add(self._ui_figure_path_down_button)
		# List
		self._ui_figure_path_store = Gtk.ListStore(str)
		self._ui_figure_path_widget = Gtk.TreeView()
		self._ui_figure_path_widget.set_model(self._ui_figure_path_store)
		self._ui_figure_path_widget.append_column(Gtk.TreeViewColumn("path", Gtk.CellRendererText(), text=0))
		self._ui_figure_path_widget.set_headers_clickable(False)
		self._ui_figure_path_widget.set_headers_visible(False)
		self._ui_figure_path_selection = self._ui_figure_path_widget.get_selection()
		self._ui_figure_path_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
		# Scroll
		ui_figure_path_scroll = self._create_scroll_for(
						self._ui_figure_path_widget, 400, 100)
		self._insert_row(ui_figure_path_scroll)


	#
	# Initialize the content
	#
	def _init_content(self):
		self._read_settings('generation')
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
	def _connect_signals(self):
		self._ui_is_figure_generated_checkbox.connect('notify::active',self.on_generate_image_toggled)
		self._ui_figure_path_selection.connect('changed',self.on_figure_path_selection_changed)
		self._ui_figure_path_add_button.connect('clicked',self.on_figure_path_add_button_clicked)
		self._ui_figure_path_remove_button.connect('clicked',self.on_figure_path_remove_button_clicked)
		self._ui_figure_path_up_button.connect('clicked',self.on_figure_path_up_button_clicked)
		self._ui_figure_path_down_button.connect('clicked',self.on_figure_path_down_button_clicked)


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
		dialog = Gtk.FileChooserDialog(_T("Select a figure path"), 
						self._window,
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
		self._reset_settings_section()
		self._set_settings_bool('generate images', 
				self._ui_is_figure_generated_checkbox.get_active())
		path = ''
		for row in self._ui_figure_path_store:
			if path: path = path + os.pathsep
			path = path + row[0].strip()
		self._set_settings_str('image directory', path)
		return utils.backend_set_configuration(self._directory, 'project' if self._is_document_level else 'user', self._settings)
