#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/config/cli/translator_panel.py
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

# Include standard libraries
import os
import shutil
import re
# Include the Glib, Gtk and Gedit libraries
from gi.repository import GObject, Gdk, Gtk, GdkPixbuf, GtkSource
# AutoLaTeX internal libs
from ...utils import utils
from ...utils import gtk_utils
from . import abstract_panel

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS _IconType
#---------------------------------

class _IconType:
    INHERITED = 0
    INCLUDED = 1
    EXCLUDED = 2
    INHERITED_CONFLICT = 3
    CONFLICT = 4

#---------------------------------
# CLASS _IconType
#---------------------------------

class _Level:
    SYSTEM = 0
    USER = 1
    PROJECT = 2

#---------------------------------
# CLASS _TranslatorCreationDialog
#---------------------------------

class _TranslatorCreationDialog(Gtk.Dialog):
	__gtype_name__ = "AutoLaTeXTranslatorCreationDialog"

	def __init__(self, parent):
		Gtk.Dialog.__init__(self,
			_T("Create a translator"),
			parent, 0,
			( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		self.set_default_size(600, 500)
		# Prepare the grid for the widgets
		self._grid = Gtk.Grid()
		self.get_content_area().add(self._grid)
		self._grid.set_row_homogeneous(False)
		self._grid.set_column_homogeneous(False)
		self._grid.set_row_spacing(5)
		self._grid.set_column_spacing(5)
		self._grid.set_property('margin', 5)
		self._grid.set_property('vexpand', False)
		self._grid.set_property('hexpand', True)
		self._grid_row = 0
		# Top label
		self._insert_row(self._create_label(
			_T("Note: read the tooltips of the fields for help.")))
		# Input extensions
		self._ui_input_extensions = self._create_row(
				_T("Input extensions"), Gtk.Entry())[1]
		self._ui_input_extensions.set_tooltip_text(
			_T("List of filename extensions, separated by spaces. Ex: .svg .svgz"))
		# Output extension
		self._ui_output_extension = Gtk.ComboBoxText()
		self._ui_output_extension.set_name('output_extension')
		self._ui_output_extension.append_text(_T("PDF or Postscript"))
		self._ui_output_extension.append_text(_T("TeX macros inside PDF or Postscript"))
		self._ui_output_extension.append_text(_T("Beamer Layer"))
		self._ui_output_extension.append_text(_T("TeX macros inside Beamer Layer"))
		self._ui_output_extension.append_text(_T("PNG Picture"))
		self._create_row(_T("Output"), self._ui_output_extension)
		# Variante
		self._ui_variante = self._create_row(_T("Variante"), Gtk.Entry())[1]
		# Execution mode
		self._ui_execution_mode = Gtk.ComboBoxText()
		self._ui_execution_mode.set_name('execution_mode')
		self._ui_execution_mode.append_text(_T("Shell Command line"))
		regex = re.compile('^([a-z0-9_]+)\.pm$')
		script_modes = ['perl']
		interpreter_dir = os.path.join(utils.AUTOLATEX_PM_PATH, 'AutoLaTeX', 'Interpreter')
		for c in os.listdir(interpreter_dir):
			mo = re.match(regex, c)
			if mo:
				script_modes.append(mo.group(1))
		script_modes.sort()
		self._script_modes = []
		for c in script_modes:
			self._ui_execution_mode.append_text(_T("Script in %s") % c)
			self._script_modes.append(c)
		self._create_row(_T("Execution mode"), self._ui_execution_mode)
		# Command line
		tab = self._create_row(_T("Command line"), Gtk.Entry())
		self._ui_command_line_label = tab[0]
		self._ui_command_line = tab[1]
		self._ui_command_line.set_tooltip_text(
			_T("Type a command line. Type:\n$in for the input filename;\n$out for the output filename;\n$outbasename for the basename with the dirname and extension;\n$outwoext for filename without the extension;\n$NAME for any environment variable named 'NAME'."))
		# Script code
		self._lang_manager = GtkSource.LanguageManager.get_default()
		self._ui_script_source = GtkSource.View()
		self._ui_script_source_buffer = GtkSource.Buffer()
		self._ui_script_source.set_buffer(self._ui_script_source_buffer)
		self._ui_script_source_buffer.set_highlight_syntax(True)
		scroll = Gtk.ScrolledWindow()
		scroll.add(self._ui_script_source)
		scroll.set_size_request(300, 200)
		scroll.set_policy(
			Gtk.PolicyType.AUTOMATIC,
			Gtk.PolicyType.AUTOMATIC)
		scroll.set_shadow_type(Gtk.ShadowType.IN)
		scroll.set_property('hexpand', True)
		scroll.set_property('vexpand', True)
		self._ui_script_source_label = self._insert_row(
				self._create_label(_T("Script source code"), True))[0]
		self._insert_row(scroll)
		# Files to clean
		self._ui_files_to_clean = self._create_row(
				_T("Files to clean"), Gtk.Entry())[1]
		self._ui_files_to_clean.set_tooltip_text(
			_T("Type list of patterns, separated by spaces. Type:\n$in for the input basename without the extension and without the directory;\n$out for the output basename without the extension and without the directory."))
		# Connect signals
		self._ui_execution_mode.connect('changed', self.on_execution_mode_changed)
		# Initialize fields
		self._ui_script_source_label.set_sensitive(False)
		self._ui_script_source.set_sensitive(False)
		self._ui_output_extension.set_active(0)
		self._ui_execution_mode.set_active(0)
		# Finalization
		self.show_all()

	def on_execution_mode_changed(self, widget, data=None):
		execution_mode = self._ui_execution_mode.get_active()
		is_command_line_mode = (execution_mode == 0)
		self._ui_command_line_label.set_sensitive(is_command_line_mode)
		self._ui_command_line.set_sensitive(is_command_line_mode)
		self._ui_script_source_label.set_sensitive(not is_command_line_mode)
		self._ui_script_source.set_sensitive(not is_command_line_mode)
		if execution_mode>0:
			lang_txt = self._script_modes[execution_mode-1]
			lang = self._lang_manager.get_language(lang_txt)
			if lang:
				self._ui_script_source_buffer.set_language(lang)
				self._ui_script_source_buffer.set_highlight_syntax(True)
			else:
				self._ui_script_source_buffer.set_highlight_syntax(False)
			text = _T("Type a source code. Type:\n#1in for the input filename;\n#1out for the output filename;\n#1outbasename for the basename without extension and dirname;\n#1outwoext for the filename without extension;\n#2inexts is the array of the input extensions;\n#1outext is the first output extension;\n#2outexts is the array of the output extensions;\n#1ispdfmode indicates if the translator is used in PDF mode;\n#1isepsmode indicates if the translator is used in EPS mode.")
			if lang_txt == 'perl':
				scalar_prefix = '$'
				array_prefix = '@'
			elif lang_txt == 'sh':
				scalar_prefix = '$_'
				array_prefix = '$_'
			elif lang_txt == 'batch' or lang_txt == 'wincmd':
				scalar_prefix = '%_'
				array_prefix = '%_'
			else:
				scalar_prefix = '_'
				array_prefix = '_'
			text = text.replace('#1', scalar_prefix)
			text = text.replace('#2', array_prefix)
			self._ui_script_source.set_tooltip_text(text)

	def _create_row(self, label_text, right_widget):
		ui_label = self._create_label(label_text)
		right_widget.set_property('hexpand', True)
		right_widget.set_property('vexpand', False)
		return self._insert_row(ui_label, right_widget)

	# Utility function to create a label
	def _create_label(self, text, hexpand=False):
		ui_label = Gtk.Label(text)
		ui_label.set_property('hexpand', hexpand)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		return ui_label

	# Utility function to create a row in a grid
	def _insert_row(self, left_widget, right_widget=None):
		if right_widget:
			self._grid.attach(	left_widget,
					0,self._grid_row,1,1) # left, top, width, height
			self._grid.attach(	right_widget, 
					1,self._grid_row,1,1) # left, top, width, height
		else:
			self._grid.attach(	left_widget, 
					0,self._grid_row,2,1) # left, top, width, height
		self._grid_row = self._grid_row + 1
		return [ left_widget, right_widget ]

	def _append(self, txt1, prefix, txt2):
		if txt2:
			return txt1 + prefix + "=" + txt2 + "\n\n"
		return txt1

	# Generate the basename for the new translator
	def generate_translator_basename(self):
		tmp = self._ui_input_extensions.get_text()
		tmp = re.split('\s+', tmp)
		for t in tmp:
			if t:
				input_extension = t
				break
		input_extension = input_extension[1:]
		
		active = self._ui_output_extension.get_active()
		if active == 1:
			output_extension = "pdf"
			flag = "+tex"
		elif active == 2:
			output_extension = "pdf"
			flag = "+layers"
		elif active == 3:
			output_extension = "pdf"
			flag = "+layers+tex"
		elif active == 4:
			output_extension = "png"
			flag = ""
		else:
			output_extension = "pdf"
			flag = ""

		variante = self._ui_variante.get_text()

		filename = input_extension + '2' + output_extension + flag
		if variante:
			filename = filename + '_' + variante

		mo = re.match("^[a-zA-Z0-9_]+2[a-zA-Z0-9_]+(?:\\+[^_.]+)*(?:\\_.+)?$", filename)
		if mo:
			filename = filename + '.transdef'
			return filename
		return None

	# Generate the content of the file .transdef 
	def generate_translator_spec(self):
		content = self._append(
				'',
				'INPUT_EXTENSIONS',
				self._ui_input_extensions.get_text())

		active = self._ui_output_extension.get_active()
		if active == 1:
			content = content+"OUTPUT_EXTENSIONS for pdf=.pdf .pdftex_t\n"
			content = content+"OUTPUT_EXTENSIONS for eps=.eps .pstex_t\n\n"
		elif active == 2:
			content = content+"OUTPUT_EXTENSIONS for pdf=.pdftex_t .pdf\n"
			content = content+"OUTPUT_EXTENSIONS for eps=.pstex_t .eps\n\n"
		elif active == 3:
			content = content+"OUTPUT_EXTENSIONS for pdf=.pdftex_t .pdf\n"
			content = content+"OUTPUT_EXTENSIONS for eps=.pstex_t .eps\n\n"
		elif active == 4:
			content = content+"OUTPUT_EXTENSIONS=.png\n"
		else:
			content = content+"OUTPUT_EXTENSIONS for pdf=.pdf\n"
			content = content+"OUTPUT_EXTENSIONS for eps=.eps\n\n"

		active = self._ui_execution_mode.get_active()
		if active==0:
			content = self._append(
					content,
					"COMMAND_LINE",
					self._ui_command_line.get_text())
		else:
			lang_txt = self._script_modes[active-1]
			start_iter = self._ui_script_source_buffer.get_start_iter()
			end_iter = self._ui_script_source_buffer.get_end_iter()
			script_text = self._ui_script_source_buffer.get_text(
					start_iter,
					end_iter,
					False)
			if lang_txt == 'perl':
				content = self._append(
						content,
						"TRANSLATOR_FUNCTION",
						"<<ENDOFSCRIPT\n"+script_text+"\nENDOFSCRIPT")
			else:
				content = self._append(
						content,
						"TRANSLATOR_FUNCTION with "+lang_txt,
						"<<ENDOFSCRIPT\n"+script_text+"\nENDOFSCRIPT")

		content = self._append(
				content,
				"FILES_TO_CLEAN",
				self._ui_files_to_clean.get_text())

		return content

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the translators
class Panel(abstract_panel.AbstractPanel):
	__gtype_name__ = "AutoLaTeXTranslatorPanel"

	def __init__(self, is_document_level, directory, window):
		abstract_panel.AbstractPanel.__init__(self, is_document_level, directory, window)

	#
	# Fill the grid
	#
	def _init_widgets(self):
		# Preload the images
		self._preload_icons()
		# Top label
		ui_label = self._create_label(_T("List of available translators:\n(click on the second column to change the loading state of the translators)"))
		self._insert_row(ui_label, None, False)
		# List of translators
		self._ui_translator_list = Gtk.ListStore(
						GdkPixbuf.Pixbuf.__gtype__,
						GdkPixbuf.Pixbuf.__gtype__,
						str,
						str)
		self._ui_translator_list_widget = Gtk.TreeView()
		self._ui_translator_list_widget.set_model(self._ui_translator_list)
		if self._is_document_level:
			label1 = _T('usr')
			self._clickable_column_label = _T('doc')
		else:
			label1 = 'sys'
			self._clickable_column_label = _T('usr')
		column = Gtk.TreeViewColumn(label1, Gtk.CellRendererPixbuf(), pixbuf=0)
		self._ui_translator_list_widget.append_column(column)
		column = Gtk.TreeViewColumn(self._clickable_column_label, Gtk.CellRendererPixbuf(), pixbuf=1)
		self._ui_translator_list_widget.append_column(column)
		column = Gtk.TreeViewColumn(_T("name"), Gtk.CellRendererText(), text=2)
		self._ui_translator_list_widget.append_column(column)
		column = Gtk.TreeViewColumn(_T("description"), Gtk.CellRendererText(), text=3)
		self._ui_translator_list_widget.append_column(column)
		self._ui_translator_list_widget.set_headers_clickable(False)
		self._ui_translator_list_widget.set_headers_visible(True)
		# Scrolling pane for translator list
		ui_translator_list_scroll = self._create_scroll_for(self._ui_translator_list_widget)
		# Management buttons
		ui_right_toolbar = Gtk.Box(False, 5)
		ui_right_toolbar.set_property('orientation', Gtk.Orientation.VERTICAL)
		ui_right_toolbar.set_property('hexpand', False)
		ui_right_toolbar.set_property('vexpand', True)
		# Button "New"
		self._ui_button_new_translator = Gtk.Button.new_from_stock(Gtk.STOCK_NEW)
		ui_right_toolbar.add(self._ui_button_new_translator)
		# Button "Import"
		self._ui_button_import_translator = Gtk.Button(_T("Import"))
		ui_right_toolbar.add(self._ui_button_import_translator)
		# Button "Delete"
		self._ui_button_delete_translator = Gtk.Button.new_from_stock(Gtk.STOCK_DELETE)
		self._ui_button_delete_translator.set_sensitive(False)
		ui_right_toolbar.add(self._ui_button_delete_translator)
		# Separator
		ui_separator = Gtk.Separator()
		ui_separator.set_orientation(Gtk.Orientation.HORIZONTAL)
		ui_right_toolbar.add(ui_separator)
		# Help - Part 1
		if self._is_document_level:
			label1 = _T('Current user')
			label2 = _T('Current document')
		else:
			label1 = _T('All users')
			label2 = _T('Current user')
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(0), label1))
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(1), label2))
		# Separator
		ui_separator = Gtk.Separator()
		ui_separator.set_orientation(Gtk.Orientation.HORIZONTAL)
		ui_right_toolbar.add(ui_separator)
		# Help - Part 2
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(1), _T('Loaded, no conflict')))
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(1, _IconType.CONFLICT), _T('Loaded, conflict')))
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(1, _IconType.EXCLUDED), _T('Not loaded')))
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(1, _IconType.INHERITED), _T('Unspecified, no conflict')))
		ui_right_toolbar.add(self._make_legend(self._get_level_icon(1, _IconType.INHERITED_CONFLICT), _T('Unspecified, conflict')))
		# Add the list and the toolbar
		self._insert_row(ui_translator_list_scroll, ui_right_toolbar, False)


	#
	# Initialize the content
	#
	def _init_content(self):
		if self._is_document_level:
			left_level = _Level.USER
			right_level = _Level.PROJECT
		else:
			left_level = _Level.SYSTEM
			right_level = _Level.USER
		# Get the data from the backend
		self._translator_config = utils.backend_get_translators(self._directory)
		self._load_config = utils.backend_get_loads(self._directory)
		# Build the conflict map and the inclusion states
		self._translator_conflict_candidates = {}
		self._translator_inclusions_constants = {}
		self._translator_inclusions = {}
		self._translator_deletions = []
		for translator in self._translator_config.sections():
			source = self._translator_config.get(translator, 'full-source')
			if source not in self._translator_conflict_candidates:
				self._translator_conflict_candidates[source] = []
			self._translator_conflict_candidates[source].append(translator)
			self._translator_inclusions_constants[translator] = self._compute_inclusion_state(translator, left_level, right_level)
			self._translator_inclusions[translator] = self._compute_inclusion_state(translator, right_level, right_level)
		# Detect initial conflicts
		for translator in self._translator_config.sections():
			self._update_translator_states(translator)
		# Fill the table
		self._translator_indexes = {}
		index = 0
		for translator in self._translator_config.sections():
			human_readable = self._translator_config.get(translator, 'human-readable')
			icon1 = self._get_level_icon(0, self._translator_inclusions_constants[translator])
			icon2 = self._get_level_icon(1, self._translator_inclusions[translator])
			self._ui_translator_list.append( [ icon1, icon2, translator, human_readable ] )
			self._translator_indexes[translator] = index
			index = index + 1


	#
	# Connect signals
	#
	def _connect_signals(self):
		self._ui_translator_list_widget.connect(
			'button-press-event', self.on_list_click_action);
		self._ui_button_new_translator.connect(
			'button-press-event', self.on_new_button_click_action);
		self._ui_button_import_translator.connect(
			'button-press-event', self.on_import_button_click_action);
		self._ui_button_delete_translator.connect(
			'button-press-event', self.on_delete_button_click_action);

	def update_widget_states(self):
		pass

	# Preloading the states' icons
	def _preload_icons(self):
		if self._is_document_level:
			left_level = _Level.USER
			right_level = _Level.PROJECT
		else:
			left_level = _Level.SYSTEM
			right_level = _Level.USER
		# Preload icons
		self._preloaded_icons = [[None,None,None,None,None],[None,None,None,None,None]]
		for i in range(5):
			self._preloaded_icons[0][i] = self.__get_level_icon(left_level, i)
			self._preloaded_icons[1][i] = self.__get_level_icon(right_level, i)

	# Load the bitmap of an icon
	def __get_level_icon(self, level, icon_type=_IconType.INCLUDED):
		if level == _Level.SYSTEM:
			icon_name = 'systemLevel'
		elif level == _Level.USER:
			icon_name = 'userLevel'
		else:
			icon_name = 'projectLevel'
		
		if icon_type == _IconType.INHERITED_CONFLICT:
			icon_name = icon_name + '_uc'
		elif icon_type == _IconType.INHERITED:
			icon_name = icon_name + '_u'
		elif icon_type == _IconType.CONFLICT:
			icon_name = icon_name + '_c'
		elif icon_type == _IconType.EXCLUDED:
			icon_name = icon_name + '_ko'
		icon_name = icon_name + '.png'
		return GdkPixbuf.Pixbuf.new_from_file(utils.make_table_icon_path(icon_name))

	# Replies an icon
	def _get_level_icon(self, column, icon_type=_IconType.INCLUDED):
		return self._preloaded_icons[column][int(icon_type)]

	# Utility function  to create the "help" legend
	def _make_legend(self, icon, label, top_padding=0):
		legend_alignment = Gtk.Box(False, 3)
		legend_alignment.set_property('vexpand', False)
		legend_alignment.set_property('hexpand', False)
		legend_alignment.set_property('orientation', Gtk.Orientation.HORIZONTAL)
		icon_label = Gtk.Image.new_from_pixbuf(icon)
		icon_label.set_property('vexpand', False)
		icon_label.set_property('hexpand', False)
		legend_alignment.add(icon_label)
		text = Gtk.Label(label)
		text.set_property('vexpand', False)
		text.set_property('hexpand', False)
		text.set_property('valign', Gtk.Align.CENTER)
		text.set_property('halign', Gtk.Align.START)
		legend_alignment.add(text)
		return legend_alignment

	# Replies if the given translator, in the given state, may be assumed as included
	def _is_includable_with(self, translator, state):
		if state == _IconType.INHERITED:
			state = self._translator_inclusions_constants[translator]
		elif state == _IconType.INHERITED_CONFLICT:
			state = self._add_conflict_in_state(self._translator_inclusions_constants[translator])
		if state == _IconType.INCLUDED or state == _IconType.CONFLICT:
			return 1 # Sure, it is included
		if state == _IconType.EXCLUDED:
			return 0 # Sure, it is not included
		return -1 # Don't know

	# Detect a conflict for the given translator, and update
	# the states of all the translators in the same group
	def _update_translator_states(self, translator):
		translators_to_update = []
		inclusion_state = self._translator_inclusions[translator]
		if inclusion_state != _IconType.EXCLUDED:
			# Detect any conflict
			is_includable = self._is_includable_with(translator, inclusion_state)
			source = self._translator_config.get(translator, 'full-source')
			for candidate in self._translator_conflict_candidates[source]:
				if translator != candidate:
					other_state = self._translator_inclusions[candidate]
					is_other_includable = self._is_includable_with(candidate, other_state)
					if is_includable and is_other_includable:
						inclusion_state = self._add_conflict_in_state(inclusion_state)
			# change the state of the other translators
			if inclusion_state == _IconType.CONFLICT or inclusion_state == _IconType.INHERITED_CONFLICT:
				for candidate in self._translator_conflict_candidates[source]:
					if translator != candidate:
						other_state = self._translator_inclusions[candidate]
						new_other_state = self._add_conflict_in_state(other_state)
						if other_state!=new_other_state:
							self._translator_inclusions[candidate] = new_other_state
							translators_to_update.append(candidate)
		self._translator_inclusions[translator] = inclusion_state
		for translator in translators_to_update:
			self._update_translator_states(translator)
		return inclusion_state

	# Compute the state of a translator for the given level
	def _compute_inclusion_state(self, translator, query_level, editable_level):
		flag = _IconType.INHERITED
		if query_level < editable_level:
			if self._load_config.has_option('system', translator):
				flag = _IconType.INCLUDED if self._load_config.getboolean('system', translator) else _IconType.EXCLUDED
			if query_level > _Level.SYSTEM:
				if self._load_config.has_option('user', translator):
					flag = _IconType.INCLUDED if self._load_config.getboolean('user', translator) else _IconType.EXCLUDED
				if query_level > _Level.USER:
					if self._load_config.has_option('project', translator):
						flag = _IconType.INCLUDED if self._load_config.getboolean('project', translator) else _IconType.EXCLUDED
		elif query_level == _Level.SYSTEM:
			if self._load_config.has_option('system', translator):
				flag = _IconType.INCLUDED if self._load_config.getboolean('system', translator) else _IconType.EXCLUDED
		elif query_level == _Level.USER:
			if self._load_config.has_option('user', translator):
				flag = _IconType.INCLUDED if self._load_config.getboolean('user', translator) else _IconType.EXCLUDED
		else:
			if self._load_config.has_option('project', translator):
				flag = _IconType.INCLUDED if self._load_config.getboolean('project', translator) else _IconType.EXCLUDED
		return flag

	# Translate the state by removing the conflict flag
	def _remove_conflict_in_state(self, state):
		if state == _IconType.CONFLICT:
			return _IconType.INCLUDED
		elif state == _IconType.INHERITED_CONFLICT:
			return _IconType.INHERITED
		return state
		
	# Translate the state by adding the conflict flag
	def _add_conflict_in_state(self, state):
		if state == _IconType.INCLUDED:
			return _IconType.CONFLICT
		elif state == _IconType.INHERITED:
			return _IconType.INHERITED_CONFLICT
		return state

	# Callback for changing the state of a translator
	def on_list_click_action(self, action, data=None):
		delete_button_sensitivity = False
		x, y = data.get_coords() #Gdk.Event
		path, column, cell_x, cell_y = action.get_path_at_pos(x,y)
		if path:
			# Get the translator name
			list_iter = self._ui_translator_list.get_iter(path)
			translator = self._ui_translator_list[list_iter][2]
			# Update the buttons
			translator_filename = self._translator_config.get(translator, 'file')
			if translator_filename:
				translator_filename = os.path.dirname(translator_filename)
				delete_button_sensitivity = os.access(translator_filename, os.W_OK)
			# Change the state of the translator if queried
			title = column.get_title()
			if title == self._clickable_column_label:
				inclusion_state = self._translator_inclusions[translator]
				inclusion_state = self._remove_conflict_in_state(inclusion_state)
				# Move up
				inclusion_state = (inclusion_state + 1) % 3
				# Reset the states for the group
				source = self._translator_config.get(translator, 'full-source')
				for candidate in self._translator_conflict_candidates[source]:
					if translator != candidate:
						other_state = self._translator_inclusions[candidate]
						other_state = self._remove_conflict_in_state(other_state)
						self._translator_inclusions[candidate] = other_state
				self._translator_inclusions[translator] = inclusion_state
				# Detect conflicts in the group
				for candidate in self._translator_conflict_candidates[source]:
					self._update_translator_states(candidate)
				# Update the UI
				for translator in self._translator_conflict_candidates[source]:
					inclusion_state = self._translator_inclusions[translator]
					index = self._translator_indexes[translator]
					path = Gtk.TreePath(index)
					list_iter = self._ui_translator_list.get_iter(path)
					self._ui_translator_list[list_iter][1] = self._get_level_icon(1, inclusion_state)
		self._ui_button_delete_translator.set_sensitive(delete_button_sensitivity)

	# Callback for adding a translator
	def on_new_button_click_action(self, action, data=None):
		dialog = _TranslatorCreationDialog(self._window)
		dialog.set_modal(True)
		answer = dialog.run()
		if answer == Gtk.ResponseType.ACCEPT:
			file_content = dialog.generate_translator_spec()
			basename = dialog.generate_translator_basename()
			dialog.destroy()
			if basename:
				directory = self._prepare_config_directory()
				target_filename = os.path.join(directory, basename)
				make_copy = True
				if os.path.isfile(target_filename):
					dialog = Gtk.MessageDialog(
							self._window, 
							Gtk.DialogFlags.MODAL, 
							Gtk.MessageType.QUESTION,
							Gtk.ButtonsType.YES_NO,
							_T("The translator file '%s' already exists.\nDo you want to replace it with the selected file?") % basename)
					answer = dialog.run()
					dialog.destroy()
					make_copy = (answer == Gtk.ResponseType.YES)
				if make_copy:
					fo = open(target_filename, "wt")
					fo.write(file_content)
					fo.close()
					self._register_translator(target_filename)
			else:
				dialog = Gtk.MessageDialog(
						self._window, 
						Gtk.DialogFlags.MODAL, 
						Gtk.MessageType.ERROR,
						Gtk.ButtonsType.OK,
						_T("Cannot compute a valid basename with the inputs."))
				answer = dialog.run()
				dialog.destroy()
		else:
			dialog.destroy()

	# Callback for importing a translator
	def on_import_button_click_action(self, action, data=None):
		dialog = Gtk.FileChooserDialog(_T("Select a translator definition"), 
						self._window,
						Gtk.FileChooserAction.OPEN,
						[ Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
						  Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT ])
		file_filter = Gtk.FileFilter()
		file_filter.set_name(_T("AutoLaTeX Translator"))
		file_filter.add_pattern("*.transdef")
		dialog.set_modal(True)
		dialog.set_select_multiple(True)
		dialog.set_filter(file_filter)
		response = dialog.run()
		filename = dialog.get_filename()
		dialog.destroy()
		if response == Gtk.ResponseType.ACCEPT:
			directory = self._prepare_config_directory()
			basename = os.path.basename(filename)
			target_filename = os.path.join(directory, basename)
			make_copy = True
			if os.path.isfile(target_filename):
				dialog = Gtk.MessageDialog(
						self._window, 
						Gtk.DialogFlags.MODAL, 
						Gtk.MessageType.QUESTION,
						Gtk.ButtonsType.YES_NO,
						_T("The translator file '%s' already exists.\nDo you want to replace it with the selected file?") % basename)
				answer = dialog.run()
				dialog.destroy()
				make_copy = (answer == Gtk.ResponseType.YES)
			if make_copy:
				shutil.copyfile(filename, target_filename)
				self._register_translator(target_filename)

	def _prepare_config_directory(self):
		directory = utils.get_autolatex_user_config_directory()
		if not os.path.isdir(directory):
			conf_file = utils.get_autolatex_user_config_file()
			tmpfile = None
			if os.path.isfile(conf_file):
				tmpfile = conf_file+".tmp"
				shutil.move(conf_file, tmpfile)
			os.makedirs(directory)
			if tmpfile:
				shutil.move(tmpfile, os.path.join(directory, 'autolatex.conf'))
		directory = os.path.join(directory, 'translators')
		if not os.path.isdir(directory):
			os.makedirs(directory)
		return directory

	def _register_translator(self, filename):
		# Reload the translator informations
		self._translator_config = utils.backend_get_translators(self._directory)
		# Search the new translator
		translator = ''
		for t in self._translator_config.sections():
			if self._translator_config.has_option(t, 'file'):
				f = self._translator_config.get(t, 'file')
				if f == filename:
					translator = t
					break
		if translator:
			# Determine the levels of the columns
			if self._is_document_level:
				left_level = _Level.USER
				right_level = _Level.PROJECT
			else:
				left_level = _Level.SYSTEM
				right_level = _Level.USER
			# Update the conflict map and the inclusion states
			source = self._translator_config.get(translator, 'full-source')
			if source not in self._translator_conflict_candidates:
				self._translator_conflict_candidates[source] = []
			self._translator_conflict_candidates[source].append(translator)
			self._translator_inclusions_constants[translator] = self._compute_inclusion_state(translator, left_level, right_level)
			self._translator_inclusions[translator] = self._compute_inclusion_state(translator, right_level, right_level)
			# Detect new conflicts
			for t in self._translator_config.sections():
				self._update_translator_states(t)
			# Add in the table
			human_readable = self._translator_config.get(translator, 'human-readable')
			icon1 = self._get_level_icon(0, self._translator_inclusions_constants[translator])
			icon2 = self._get_level_icon(1, self._translator_inclusions[translator])
			insert_index = gtk_utils.get_insert_index_dichotomic(
						self._ui_translator_list,
						2,
						translator)
			if insert_index>=0:
				insert_iter = self._ui_translator_list.insert(insert_index)
				self._ui_translator_list.set(insert_iter, 
								0, icon1,
								1, icon2,
								2, translator,
								3, human_readable )
				self._translator_indexes[translator] = insert_index
			else:
				self._ui_translator_list.append( [ icon1, icon2, translator, human_readable ] )
				self._translator_indexes[translator] = self._ui_translator_list.iter_n_children(None) - 1
			# Update the UI
			for t in self._translator_conflict_candidates[source]:
				if t != translator:
					inclusion_state = self._translator_inclusions[t]
					index = self._translator_indexes[t]
					if index>=insert_index:
						index = index + 1
						self._translator_indexes[t] = index
					path = Gtk.TreePath(index)
					list_iter = self._ui_translator_list.get_iter(path)
					self._ui_translator_list[list_iter][1] = self._get_level_icon(1, inclusion_state)
		else:
			# Something wrong append
			dialog = Gtk.MessageDialog(
					self._window, 
					Gtk.DialogFlags.MODAL, 
					Gtk.MessageType.ERROR,
					Gtk.ButtonsType.OK,
					_T("There is a problem when reading the translator's definition.\nPlease close and re-open the configuration dialog\nfor trying to read the configuration of the new translator."))
			dialog.run()
			dialog.destroy()

	# Callback for deleting a translator
	def on_delete_button_click_action(self, action, data=None):
		select_iter = self._ui_translator_list_widget.get_selection().get_selected()[1]
		translator = self._ui_translator_list[select_iter][2]
		dialog = Gtk.MessageDialog(
				self._window, 
				Gtk.DialogFlags.MODAL, 
				Gtk.MessageType.QUESTION,
				Gtk.ButtonsType.YES_NO,
				_T("Do you want to delete the translator '%s'?") % translator)
		answer = dialog.run()
		dialog.destroy()
		if answer == Gtk.ResponseType.YES:
			# Remove the file
			translator_filename = self._translator_config.get(translator, 'file')
			os.unlink(translator_filename)
			# Remove from the table
			self._ui_translator_list.remove(select_iter)
			# Update the indexes
			the_index = self._translator_indexes[translator]
			for t in self._translator_indexes:
				if the_index<=self._translator_indexes[t]:
					self._translator_indexes[t] = self._translator_indexes[t] - 1
			# Clear the conflict map and the inclusion states
			source = self._translator_config.get(translator, 'full-source')
			self._translator_conflict_candidates[source].remove(translator)
			del self._translator_inclusions[translator]
			self._translator_deletions.append(translator)
			# Reset the states of the other translators related to the removed one.
			for other_translator in self._translator_conflict_candidates[source]:
				other_state = self._translator_inclusions[other_translator]
				other_state = self._remove_conflict_in_state(other_state)
				self._translator_inclusions[other_translator] = other_state
			# Update the states of the other translators related to the removed one.
			for other_translator in self._translator_conflict_candidates[source]:
				self._update_translator_states(other_translator)
			# Remove the translator from the backend data
			self._translator_config.remove_section(translator)
			if self._is_document_level:
				section_name = 'project'
			else:
				section_name = 'user'
			if self._load_config.has_section(section_name) and self._load_config.has_option(section_name, translator):
				self._load_config.remove_option(section_name, translator)
			# Update the UI
			for translator in self._translator_conflict_candidates[source]:
				inclusion_state = self._translator_inclusions[translator]
				index = self._translator_indexes[translator]
				path = Gtk.TreePath(index)
				list_iter = self._ui_translator_list.get_iter(path)
				self._ui_translator_list[list_iter][1] = self._get_level_icon(1, inclusion_state)



	# Invoked when the changes in the panel must be saved
	def save(self):
		if self._is_document_level:
			section_name = 'project'
		else:
			section_name = 'user'
		self._load_config.remove_section(section_name)
		self._load_config.add_section(section_name)
		# Save the loading state of the translators
		for translator in self._translator_inclusions:
			state = self._translator_inclusions[translator]
			if state == _IconType.INCLUDED or state == _IconType.CONFLICT:
				self._load_config.set(section_name, translator, 'true')
			elif state == _IconType.EXCLUDED:
				self._load_config.set(section_name, translator, 'false')
		# Force the removed translators to be removed from the configuration
		for translator in self._translator_deletions:
			self._load_config.set(section_name, translator, utils.CONFIG_EMPTY_VALUE)
		return utils.backend_set_loads(self._directory, self._load_config)
