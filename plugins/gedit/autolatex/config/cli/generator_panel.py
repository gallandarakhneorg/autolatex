# autolatex/config/cli/generator_panel.py
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
from ...utils import utils

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS _GenerationType
#---------------------------------

class _GenerationType:
	PDF = 'pdf'
	DVI = 'dvi'
	POSTSCRIPT = 'ps'

	def index(v):
		if v == _GenerationType.POSTSCRIPT: return 2
		elif v == _GenerationType.DVI: return 1
		else: return 0

	def label(i):
		if i == 2: return _GenerationType.POSTSCRIPT
		elif i == 1: return _GenerationType.DVI
		else: return _GenerationType.PDF

	index = staticmethod(index)
	label = staticmethod(label)

#---------------------------------
# CLASS _IndexType
#---------------------------------

class _IndexType:
	FILE = 0 # [ <str> ]
	DETECTION = 1 # [@detect] or [@detect, @system]
	DEFAULT = 2 # [@system]
	NONE = 3 # empty or [@none]
	USER = 4 # other

	def parse(s):
		tab = s.split(',')
		for i in range(len(tab)):
			tab[i] = tab[i].strip()
		return tab

	def index(t):
		if t and len(t)>0:
			if len(t) == 2:
				if t[0] == '@detect' and t[1] == '@system': return _IndexType.DETECTION
				else: return _IndexType.USER
			elif len(t) == 1:
				if t[0] == '@detect': return _IndexType.DETECTION
				elif t[0] == '@system': return _IndexType.DEFAULT
				elif not t[0] or t[0] == '@none': return _IndexType.NONE
				else: return _IndexType.USER
			else:
				return _IndexType.USER
		else:
			return _IndexType.NONE

	def label(i, original_value):
		if i == 0: return original_value
		elif i == 1: return '@detect, @system'
		elif i == 2: return '@system'
		elif i == 3: return '@none'
		else: return original_value

	parse = staticmethod(parse)
	index = staticmethod(index)
	label = staticmethod(label)

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the generator
class Panel(Gtk.Box):
	__gtype_name__ = "AutoLaTeXGeneratorPanel"

	def __init__(self, is_document_level, directory):
		# Use an intermediate GtkBox to be sure that
		# the child GtkGrid will not be expanded vertically
		Gtk.Box.__init__(self)
		self._is_document_level = is_document_level
		self._directory = directory
		#
		# Create the grid for the panel
		#
		self.set_property('orientation', Gtk.Orientation.VERTICAL)
		grid = Gtk.Grid()
		self.pack_start(grid, False, False, 0)
		grid.set_row_homogeneous(False)
		grid.set_column_homogeneous(False)
		grid.set_row_spacing(5)
		grid.set_column_spacing(5)
		grid.set_property('margin', 5)
		grid.set_property('vexpand', False)
		grid.set_property('hexpand', True)
		#
		# Fill the grid
		#
		table_row = 0
		if self._is_document_level:
			# Label
			ui_label = Gtk.Label(_T("Main TeX file (optional)"))
			ui_label.set_property('hexpand', False)
			ui_label.set_property('vexpand', False)
			ui_label.set_property('halign', Gtk.Align.START)
			ui_label.set_property('valign', Gtk.Align.CENTER)
			grid.attach(	ui_label,
					0,table_row,1,1) # left, top, width, height
			# Text field
			self._ui_main_tex_file_editor = Gtk.Entry()
			self._ui_main_tex_file_editor.set_property('hexpand', True)
			self._ui_main_tex_file_editor.set_property('vexpand', False)
			grid.attach(	self._ui_main_tex_file_editor, 
					1,table_row,1,1) # left, top, width, height
			table_row = table_row + 1
		# Label
		ui_label = Gtk.Label(_T("Execute the bibliography tool (BibTeX, Bibber...)"))
		ui_label.set_property('hexpand', False)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	ui_label, 
				0,table_row,1,1) # left, top, width, height
		# Switch
		self._ui_run_biblio_checkbox = Gtk.Switch()
		self._ui_run_biblio_checkbox.set_property('hexpand', False)
		self._ui_run_biblio_checkbox.set_property('vexpand', False)
		self._ui_run_biblio_checkbox.set_property('halign', Gtk.Align.END)
		self._ui_run_biblio_checkbox.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	self._ui_run_biblio_checkbox, 
				1,table_row,1,1) # left, top, width, height
		table_row = table_row + 1
		# Label
		ui_label = Gtk.Label(_T("Type of generation"))
		ui_label.set_property('hexpand', False)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	ui_label, 
				0,table_row,1,1) # left, top, width, height
		# Combo box
		self._ui_generation_type_combo = Gtk.ComboBoxText()
		self._ui_generation_type_combo.set_name('generation_type')
		self._ui_generation_type_combo.append_text("PDF")
		self._ui_generation_type_combo.append_text("DVI")
		self._ui_generation_type_combo.append_text("Postscript")
		self._ui_generation_type_combo.set_property('hexpand', True)
		self._ui_generation_type_combo.set_property('vexpand', False)
		grid.attach(	self._ui_generation_type_combo, 
				1,table_row,1,1) # left, top, width, height
		table_row = table_row + 1
		# Label
		ui_label = Gtk.Label(_T("Use SyncTeX when generating the document"))
		ui_label.set_property('hexpand', False)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	ui_label, 
				0,table_row,1,1) # left, top, width, height
		# Switch
		self._ui_run_synctex_checkbox = Gtk.Switch()
		self._ui_run_synctex_checkbox.set_property('hexpand', False)
		self._ui_run_synctex_checkbox.set_property('vexpand', False)
		self._ui_run_synctex_checkbox.set_property('halign', Gtk.Align.END)
		self._ui_run_synctex_checkbox.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	self._ui_run_synctex_checkbox, 
				1,table_row,1,1) # left, top, width, height
		table_row = table_row + 1
		# Label
		ui_label = Gtk.Label(_T("Type of style for MakeIndex"))
		ui_label.set_property('hexpand', False)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	ui_label, 
				0,table_row,1,1) # left, top, width, height
		# Combo box
		self._ui_makeindex_type_combo = Gtk.ComboBoxText()
		self._ui_makeindex_type_combo.set_name('makeindex_style_type')
		self._ui_makeindex_type_combo.append_text(_T("Specific '.ist' file"))
		self._ui_makeindex_type_combo.append_text(_T("Autodetect the style inside the project directory"))
		self._ui_makeindex_type_combo.append_text(_T("Use only the default AutoLaTeX style"))
		self._ui_makeindex_type_combo.append_text(_T("No style is passed to MakeIndex"))
		self._ui_makeindex_type_combo.append_text(_T("Custom definition by the user (do not change the original configuration)"))
		self._ui_makeindex_type_combo.set_property('hexpand', True)
		self._ui_makeindex_type_combo.set_property('vexpand', False)
		grid.attach(	self._ui_makeindex_type_combo, 
				1,table_row,1,1) # left, top, width, height
		table_row = table_row + 1
		# Label
		label = _T("Style file for MakeIndex")
		self._ui_makeindex_file_label = Gtk.Label(label)
		self._ui_makeindex_file_label.set_property('hexpand', False)
		self._ui_makeindex_file_label.set_property('vexpand', False)
		self._ui_makeindex_file_label.set_property('halign', Gtk.Align.START)
		self._ui_makeindex_file_label.set_property('valign', Gtk.Align.CENTER)
		grid.attach(	self._ui_makeindex_file_label, 
				0,table_row,1,1) # left, top, width, height
		# File chooser button
		self._ui_makeindex_file_field = Gtk.FileChooserButton()
		self._ui_makeindex_file_field.set_width_chars(40)
		self._ui_makeindex_file_field.set_title(label)
		self._ui_makeindex_file_field.set_property('hexpand', True)
		self._ui_makeindex_file_field.set_property('vexpand', False)
		grid.attach(	self._ui_makeindex_file_field, 
				1,table_row,1,1) # left, top, width, height
		table_row = table_row + 1
		#
		# Initialize the content
		#
		self._settings = utils.backend_get_configuration(
						self._directory,
						'project' if self._is_document_level else 'user',
						'generation')
		if self._is_document_level:
			self._ui_main_tex_file_editor.set_text(self._get_settings_str('main file'))
		self._ui_run_biblio_checkbox.set_active(self._get_settings_bool('biblio', True))
		self._ui_run_synctex_checkbox.set_active(self._get_settings_bool('synctex', False))
		self._ui_generation_type_combo.set_active(
				_GenerationType.index(self._get_settings_str('generation type', _GenerationType.PDF)))
		self._makeindex_value = self._get_settings_str('makeindex style', '@detect, @system')
		makeindex_type = _IndexType.index(_IndexType.parse(self._makeindex_value))
		self._ui_makeindex_type_combo.set_active(makeindex_type)
		self._update_widget_states()
		#
		# Connect signals
		#
		self._ui_makeindex_type_combo.connect('changed',self.on_generation_type_changed)

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
		makeindex_type = self._ui_makeindex_type_combo.get_active()
		if makeindex_type == _IndexType.FILE:
			self._ui_makeindex_file_field.set_filename(self._makeindex_value)
			self._ui_makeindex_file_label.set_sensitive(True)
			self._ui_makeindex_file_field.set_sensitive(True)
		else:
			self._ui_makeindex_file_field.unselect_all()
			self._ui_makeindex_file_label.set_sensitive(False)
			self._ui_makeindex_file_field.set_sensitive(False)

	# Invoke when the style of MakeIndex has changed
	def on_generation_type_changed(self, widget, data=None):
		self._update_widget_states()

	# Invoked when the changes in the panel must be saved
	def save(self):
		self._settings.remove_section('generation')
		self._settings.add_section('generation')
		self._settings.set('generation', 'main file', self._ui_main_tex_file_editor.get_text())
		self._settings.set('generation', 'biblio', 
				'true' if self._ui_run_biblio_checkbox.get_active() else 'false')
		self._settings.set('generation', 'synctex', 
				'true' if self._ui_run_synctex_checkbox.get_active() else 'false')
		self._settings.set('generation', 'generation type', 
				_GenerationType.label(self._ui_generation_type_combo.get_active()))
		self._settings.set('generation', 'makeindex style', 
				_IndexType.label(self._ui_makeindex_type_combo.get_active(), self._makeindex_value))
		return utils.backend_set_configuration(self._directory, 'project' if self._is_document_level else 'user', self._settings)
