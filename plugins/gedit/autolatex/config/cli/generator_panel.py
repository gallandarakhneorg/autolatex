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
from . import abstract_panel

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
class Panel(abstract_panel.AbstractPanel):
	__gtype_name__ = "AutoLaTeXGeneratorPanel"

	def __init__(self, is_document_level, directory, window):
		abstract_panel.AbstractPanel.__init__(self, is_document_level, directory, window)

	#
	# Fill the grid
	#
	def _init_widgets(self):
		table_row = 0
		if self._is_document_level:
			# Main TeX File
			self._ui_main_tex_file_editor = self._create_entry(
				_T("Main TeX file (optional)"))[1]
		# Execute the bibtex tools
		self._ui_run_biblio_checkbox = self._create_switch(
				_T("Execute the bibliography tool (BibTeX, Bibber...)"))[1]
		# Type of generation
		self._ui_generation_type_combo = self._create_combo(
				_T("Type of generation"),
				[ "PDF", "DVI", "Postscript" ],
				'generation_type')[1]
		# SyncTeX
		self._ui_run_synctex_checkbox = self._create_switch(
				_T("Use SyncTeX when generating the document"))[1]
		# Type of MakeIndex style
		self._ui_makeindex_type_combo = self._create_combo(
				_T("Type of style for MakeIndex"),
				[	_T("Specific '.ist' file"),
					_T("Autodetect the style inside the project directory"),
					_T("Use only the default AutoLaTeX style"),
					_T("No style is passed to MakeIndex"),
					_T("Custom definition by the user (do not change the original configuration)") ],
				'makeindex_style_type')[1]
		# File of the MakeIndex style
		label = _T("Style file for MakeIndex")
		self._ui_makeindex_file_field = Gtk.FileChooserButton()
		self._ui_makeindex_file_field.set_width_chars(40)
		self._ui_makeindex_file_field.set_title(label)
		self._ui_makeindex_file_label = self._create_row(
				label,
				self._ui_makeindex_file_field)[0]


	#
	# Initialize the content
	#
	def _init_content(self):
		self._read_settings('generation')
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
	def _connect_signals(self):
		self._ui_makeindex_type_combo.connect('changed',self.on_generation_type_changed)





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
		self._reset_settings_section()
		self._set_settings_str('main file', self._ui_main_tex_file_editor.get_text())
		self._set_settings_bool('biblio',
				self._ui_run_biblio_checkbox.get_active())
		self._set_settings_bool('synctex', 
				self._ui_run_synctex_checkbox.get_active())
		self._set_settings_str('generation type', 
				_GenerationType.label(self._ui_generation_type_combo.get_active()))
		self._set_settings_str('makeindex style', 
				_IndexType.label(self._ui_makeindex_type_combo.get_active(), self._makeindex_value))
		return utils.backend_set_configuration(self._directory, 'project' if self._is_document_level else 'user', self._settings)
