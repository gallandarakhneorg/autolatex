# autolatex - autolatex_generator_panel.py
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
# CLASS GenerationType
#---------------------------------

class GenerationType:
	PDF = 'pdf'
	DVI = 'dvi'
	POSTSCRIPT = 'ps'

	def index(v):
		if v == GenerationType.POSTSCRIPT: return 2
		elif v == GenerationType.DVI: return 1
		else: return 0

	def label(i):
		if i == 2: return GenerationType.POSTSCRIPT
		elif i == 1: return GenerationType.DVI
		else: return GenerationType.PDF

	index = staticmethod(index)
	label = staticmethod(label)

#---------------------------------
# CLASS IndexType
#---------------------------------

class IndexType:
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
				if t[0] == '@detect' and t[1] == '@system': return IndexType.DETECTION
				else: return IndexType.USER
			elif len(t) == 1:
				if t[0] == '@detect': return IndexType.DETECTION
				elif t[0] == '@system': return IndexType.DEFAULT
				elif not t[0] or t[0] == '@none': return IndexType.NONE
				else: return IndexType.USER
			else:
				return IndexType.USER
		else:
			return IndexType.NONE

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
class Panel(Gtk.Table):
	__gtype_name__ = "AutoLaTeXGeneratorPanel"

	def __init__(self, is_document_level, directory):
		Gtk.Table.__init__(self,
				5, #rows
				2, #columns
				False) #non uniform
		self._is_document_level = is_document_level
		self._directory = directory

		table_row = 0

		if self._is_document_level:
			ui_label = Gtk.Label(_T("Main TeX file (optional)"))
			ui_label.set_alignment(0, 0.5)
			self.attach(	ui_label,
					0,1,table_row,table_row+1, # left, right, top and bottom columns
					Gtk.AttachOptions.SHRINK, # x options
					Gtk.AttachOptions.SHRINK, # y options
					2,5) # horizontal and vertical paddings
			self._ui_main_tex_file_editor = Gtk.Entry()
			self.attach(	self._ui_main_tex_file_editor, 
					1,2,table_row,table_row+1, # left, right, top and bottom columns
					Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
					Gtk.AttachOptions.SHRINK, # y options
					2,5) # horizontal and vertical paddings
			table_row = table_row + 1

		hbox = Gtk.HBox()
		self.attach(	hbox, 
				0,2,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		table_row = table_row + 1
		ui_label = Gtk.Label(_T("Execute the bibliography tool (BibTeX, Bibber...)"))
		ui_label.set_alignment(0, 0.5)
		hbox.add(ui_label)
		self._ui_run_biblio_checkbox = Gtk.Switch()
		hbox.add(self._ui_run_biblio_checkbox)

		ui_label = Gtk.Label(_T("Type of generation"))
		ui_label.set_alignment(0, 0.5)
		self.attach(	ui_label, 
				0,1,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5) # horizontal and vertical paddings

		self._ui_generation_type_combo = Gtk.ComboBoxText()
		self._ui_generation_type_combo.set_name('generation_type')
		self._ui_generation_type_combo.append_text("PDF")
		self._ui_generation_type_combo.append_text("DVI")
		self._ui_generation_type_combo.append_text("Postscript")
		self.attach(	self._ui_generation_type_combo, 
				1,2,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		table_row = table_row + 1

		hbox = Gtk.HBox()
		self.attach(	hbox, 
				0,2,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		table_row = table_row + 1
		ui_label = Gtk.Label(_T("Use SyncTeX when generating the document"))
		ui_label.set_alignment(0, 0.5)
		hbox.add(ui_label)
		self._ui_run_synctex_checkbox = Gtk.Switch()
		hbox.add(self._ui_run_synctex_checkbox)

		ui_label = Gtk.Label(_T("Type of style for MakeIndex"))
		ui_label.set_alignment(0, 0.5)
		self.attach(	ui_label, 
				0,1,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5) # horizontal and vertical paddings

		self._ui_makeindex_type_combo = Gtk.ComboBoxText()
		self._ui_makeindex_type_combo.set_name('makeindex_style_type')
		self._ui_makeindex_type_combo.append_text(_T("Specific '.ist' file"))
		self._ui_makeindex_type_combo.append_text(_T("Autodetect the style inside the project directory"))
		self._ui_makeindex_type_combo.append_text(_T("Use only the default AutoLaTeX style"))
		self._ui_makeindex_type_combo.append_text(_T("No style is passed to MakeIndex"))
		self._ui_makeindex_type_combo.append_text(_T("Custom definition by the user (do not change the original configuration)"))
		self.attach(	self._ui_makeindex_type_combo, 
				1,2,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5); # horizontal and vertical paddings
		table_row = table_row + 1

		label = _T("Style file for MakeIndex")
		self._ui_makeindex_file_label = Gtk.Label(label)
		self._ui_makeindex_file_label.set_alignment(0, 0.5)
		self.attach(	self._ui_makeindex_file_label, 
				0,1,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.SHRINK, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5) # horizontal and vertical paddings
		self._ui_makeindex_file_field = Gtk.FileChooserButton()
		self._ui_makeindex_file_field.set_width_chars(40)
		self._ui_makeindex_file_field.set_title(label)
		self.attach(	self._ui_makeindex_file_field, 
				1,2,table_row,table_row+1, # left, right, top and bottom columns
				Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL, # x options
				Gtk.AttachOptions.SHRINK, # y options
				2,5) # horizontal and vertical paddings
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
				GenerationType.index(self._get_settings_str('generation type', GenerationType.PDF)))
		self._makeindex_value = self._get_settings_str('makeindex style', '@detect, @system')
		makeindex_type = IndexType.index(IndexType.parse(self._makeindex_value))
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
		if makeindex_type == IndexType.FILE:
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
				GenerationType.label(self._ui_generation_type_combo.get_active()))
		self._settings.set('generation', 'makeindex style', 
				IndexType.label(self._ui_makeindex_type_combo.get_active(), self._makeindex_value))
		return utils.backend_set_configuration(self._directory, 'project' if self._is_document_level else 'user', self._settings)
