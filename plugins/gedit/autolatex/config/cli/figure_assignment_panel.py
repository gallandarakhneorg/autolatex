# autolatex/config/cli/figure_assignment_panel.py
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
import re
import ConfigParser
# Include the Glib, Gtk and Gedit libraries
from gi.repository import Gtk
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

# Gtk panel that is managing the configuration of the figure assignments
class Panel(abstract_panel.AbstractPanel):
	__gtype_name__ = "AutoLaTeXFigureAssignmentPanel"

	def __init__(self, is_document_level, directory, window):
		abstract_panel.AbstractPanel.__init__(self, is_document_level, directory, window)
		

	#
	# Fill the grid
	#
	def _init_widgets(self):
		# Comment
		ui_label = self._create_label(_T("List of the figures detected in your document's directory.\nYou can edit the second column to set the translator used for a particular figure."))
		self._insert_row(ui_label)
		# List of figures
		self._ui_figure_edit_store = Gtk.ListStore(str)
		self._ui_figure_store = Gtk.ListStore(str, str)
		ui_figure_widget = Gtk.TreeView()
		ui_figure_widget.set_model(self._ui_figure_store)
		ui_figure_widget.append_column(Gtk.TreeViewColumn(_T("Figure"), Gtk.CellRendererText(), text=0))
		renderer_combo = Gtk.CellRendererCombo()
		renderer_combo.set_property("editable", True)
		renderer_combo.set_property("model", self._ui_figure_edit_store)
		renderer_combo.set_property("text-column", 0)
		renderer_combo.set_property("has-entry", False)
		renderer_combo.connect("edited", self.on_figure_translator_changed)
		ui_figure_widget.append_column(Gtk.TreeViewColumn(_T("Translator"), renderer_combo, text=1))
		ui_figure_widget.set_headers_clickable(False)
		ui_figure_widget.set_headers_visible(True)
		self._ui_figure_selection = ui_figure_widget.get_selection()
		self._ui_figure_selection.set_mode(Gtk.SelectionMode.SINGLE)
		# Scroll
		ui_figure_scroll = self._create_scroll_for(ui_figure_widget)
		self._insert_row(ui_figure_scroll)


	#
	# Initialize the content
	#
	def _init_content(self):
		self._settings = utils.backend_get_translators(self._directory)
		self._translators = {}
		self._regex = re.compile('^([^2]+)')
		for translator in self._settings.sections():
			result = re.match(self._regex, translator)
			if result:
				source = result.group(1)
				if source not in self._translators:
					self._translators[source] = []
				self._translators[source].append(translator)
				
		self._settings = utils.backend_get_images(self._directory)
		self._file_list = {}
		for translator in self._settings.sections():
			if self._settings.has_option(translator, 'automatic assignment'):
				data = self._settings.get(translator, 'automatic assignment')
				files = data.split(os.pathsep)
				for afile in files:
					if afile not in self._file_list:
						self._file_list[afile] = {}
					self._file_list[afile]['translator'] = translator
					self._file_list[afile]['override'] = False
					self._file_list[afile]['selected'] = translator
			if self._settings.has_option(translator, 'files to convert'):
				data = self._settings.get(translator, 'files to convert')
				files = data.split(os.pathsep)
				for afile in files:
					if afile not in self._file_list:
						self._file_list[afile] = {}
					self._file_list[afile]['translator'] = translator
					self._file_list[afile]['override'] = True
					self._file_list[afile]['selected'] = translator
			if self._settings.has_option(translator, 'overriden assignment'):
				data = self._settings.get(translator, 'overriden assignment')
				files = data.split(os.pathsep)
				for afile in files:
					if afile not in self._file_list:
						self._file_list[afile] = {}
					self._file_list[afile]['auto-translator'] = translator

		for filename in sorted(self._file_list):
			if 'translator' in self._file_list[filename]:
				self._ui_figure_store.append( [ filename, self._file_list[filename]['translator'] ] )


	#
	# Connect signals
	#
	def _connect_signals(self):
		self._ui_figure_selection.connect('changed',self.on_figure_selection_changed)

	# Invoked when the selection in the lsit of figure paths has changed
	def on_figure_selection_changed(self, selection, data=None):
		n_sel = self._ui_figure_selection.count_selected_rows()
		if n_sel > 0:
			path = self._ui_figure_selection.get_selected_rows()[1][0]
			sel_iter = self._ui_figure_store.get_iter(path)
			value = self._ui_figure_store.get_value(sel_iter, 1)
			afile = self._ui_figure_store.get_value(sel_iter, 0)
			self._ui_figure_edit_store.clear()
			result = re.match(self._regex, value)
			if result:
				source = result.group(1)
				if afile in self._file_list and self._file_list[afile]['override']:
					auto_translator = self._file_list[afile]['auto-translator']
				else:
					auto_translator = self._file_list[afile]['translator']
				for translator in self._translators[source]:
					label = translator
					if translator == auto_translator:
						label = label+' (default)'
					self._ui_figure_edit_store.append( [label] )

	# Invoked when the selection in the lsit of figure paths has changed
	def on_figure_translator_changed(self, combo, path, new_text, data=None):
		if new_text:
			if new_text.endswith(' (default)'):
				new_text = new_text[0:len(new_text)-10]
			sel_iter = self._ui_figure_store.get_iter(path)
			self._ui_figure_store.set_value(sel_iter, 1, new_text)
			afile = self._ui_figure_store.get_value(sel_iter, 0)
			self._file_list[afile]['selected'] = new_text

	def _append_file(self, config, section, option, afile):
		if config.has_option(section, option):
			path = config.get(section, option)
			if path:
				path = path+os.pathsep+afile
			else:
				path = afile
		else:
			path = afile
		config.set(section, option, path)

	# Invoked when the changes in the panel must be saved
	def save(self):
		config = ConfigParser.ConfigParser()
		for source in self._translators:
			for translator in self._translators[source]:
				config.add_section(translator)
		for afile in self._file_list:
			current = self._file_list[afile]['selected']
			if self._file_list[afile]['override']:
				std = self._file_list[afile]['auto-translator']
			else:
				std = self._file_list[afile]['translator']
			if current == std:
				self._append_file(config, current, 'automatic assignment', afile)
			else:
				self._append_file(config, current, 'files to convert', afile)
				self._append_file(config, std, 'overriden assignment', afile)
		return utils.backend_set_images(self._directory, config)
