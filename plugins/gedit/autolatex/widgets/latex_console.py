#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/widgets/latex_console.py
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
import re
# Include the Gtk libraries
from gi.repository import GObject, GdkPixbuf, Gdk, Gio, Gtk
# AutoLaTeX includes
from ..utils import latex_log_parser as log_parser

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS ConsoleMode
#---------------------------------
class ConsoleMode:
	HIDE = 0
	OPTIONAL = 1
	SHOW = 2

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the plugin
class Console(Gtk.ScrolledWindow):
	__gtype_name__ = "AutoLaTeXLaTeXConsole"

	def __init__(self, plugin):
		Gtk.ScrolledWindow.__init__(self)
		self.window = plugin.window
		self.plugin = plugin
		self._re_file_match = re.compile("^(.+):([0-9]+):\\s*(.*?)\\s*$", re.DOTALL)
		self._document_directory = None
		self._latex_parser = None
		self._current_error = -1
		# Create the store
		self._messages = Gtk.ListStore(str, str, str, long, str)
		# Create the list
		self._message_widget = Gtk.TreeView()
		self._message_widget.set_size_request(200, 150)
		self._message_widget.set_model(self._messages)
		column = Gtk.TreeViewColumn("Level", Gtk.CellRendererPixbuf(), stock_id=0)
		self._message_widget.append_column(column)
		column = Gtk.TreeViewColumn("Text", Gtk.CellRendererText(), text=1)
		self._message_widget.append_column(column)
		self._message_widget.set_headers_clickable(False)
		self._message_widget.set_headers_visible(False)
		# Init the scroll
		self.add(self._message_widget)
		self.set_size_request(200, 150)
		self.set_policy(
			Gtk.PolicyType.AUTOMATIC,
			Gtk.PolicyType.AUTOMATIC)
		self.set_shadow_type(Gtk.ShadowType.IN)
		self.set_property('hexpand', True)
		self.set_property('vexpand', True)
		#
		self.show_all()
		#
		self._message_widget.connect(
			'button-press-event', self.on_list_click_action);

	# Set the text of the log
	def set_log(self, log, latex_warnings, document_directory):
		# Reset attributes
		self._latex_parser = None
		self._current_error = -1
		self._document_directory = Gio.File.new_for_path(document_directory)
		# Clear the list
		self._messages.clear()
		# Add the errors in the log
		if log:
			mo = re.match(self._re_file_match, log)
			if mo:
				filename = mo.group(1)
				linenumber = long(mo.group(2))
				message = mo.group(3)
			else:
				filename = ''
				linenumber = long(0)
				message = log
			ui_icon = Gtk.STOCK_DIALOG_ERROR
			if filename:
				m = filename
				if linenumber>0:
					m = m + ":" + str(linenumber)
				self._messages.append(
					[ ui_icon, m+"\n"+message, filename, linenumber, None ])
			else:
				self._messages.append(
					[ ui_icon, message, filename, linenumber, None ])
		elif latex_warnings:
			# Add the warnings
			for latex_warning in latex_warnings:
				ui_icon = Gtk.STOCK_JUMP_TO if latex_warning[2] else Gtk.STOCK_DIALOG_WARNING
				self._messages.append(
					[ ui_icon, latex_warning[0], latex_warning[1], long(0), latex_warning[2] ])
		if log:
			return ConsoleMode.SHOW
		if latex_warnings:
			return ConsoleMode.OPTIONAL
		return ConsoleMode.HIDE

	def show_next_error(self):
		length = len(self._messages)
		if length>0 and self._current_error < (len(self._messages)-1):
			self._current_error = self._current_error + 1
			path = Gtk.TreePath(self._current_error)
			is_expanded = self._do_click_on_list(path)
			while is_expanded:
				is_expanded = self._do_click_on_list(path)
			self._message_widget.get_selection().select_path(path)
			self._message_widget.scroll_to_cell(
				path,
				self._message_widget.get_column(0),
				True, 0, 0)
			return ConsoleMode.SHOW
		return ConsoleMode.HIDE

	def has_next_error(self):
		length = len(self._messages)
		return length>0 and self._current_error < (length-1)

	def show_previous_error(self):
		if self._current_error > 0:
			self._current_error = self._current_error - 1
			path = Gtk.TreePath(self._current_error)
			is_expanded = self._do_click_on_list(path)
			while is_expanded:
				is_expanded = self._do_click_on_list(path)
			self._message_widget.get_selection().select_path(path)
			self._message_widget.scroll_to_cell(
				path,
				self._message_widget.get_column(0),
				True, 0, 0)
			return ConsoleMode.SHOW
		return ConsoleMode.HIDE

	def has_previous_error(self):
		return self._current_error > 0

	def _replace_by_undefined_reference_warnings(self, list_iter, log_file):
		if not self._latex_parser:
			self._latex_parser = log_parser.Parser(log_file)
		warnings = self._latex_parser.get_undefined_reference_warnings()
		if warnings:
			ui_icon = Gtk.STOCK_DIALOG_WARNING
			for warning in reversed(warnings):
				self._messages.insert_before(list_iter,
					[ ui_icon,
					  warning.get_message(),
					  warning.get_filename(),
					  long(warning.get_line_number()),
					  None ])
		else:
			# Issue 53: sometimes the LaTeX tool is saying
			# "There were undefined references" for a citation.
			warnings = self._latex_parser.get_undefined_citation_warnings()
			if warnings:
				ui_icon = Gtk.STOCK_DIALOG_WARNING
				for warning in reversed(warnings):
					self._messages.insert_before(list_iter,
						[ ui_icon,
						  warning.get_message(),
						  warning.get_filename(),
						  long(warning.get_line_number()),
						  None ])
			else:
				ui_icon = Gtk.STOCK_DIALOG_ERROR
				self._messages.insert_before(list_iter,
					[ ui_icon,
					  _T("Internal Error: Unable to retreive the undefined references from the LaTeX log"),
					  None,
					  long(0),
					  None ])
		self._messages.remove(list_iter)

	def _replace_by_multidefined_label_warnings(self, list_iter, log_file):
		if not self._latex_parser:
			self._latex_parser = log_parser.Parser(log_file)
		warnings = self._latex_parser.get_multidefined_label_warnings()
		if warnings:
			ui_icon = Gtk.STOCK_DIALOG_WARNING
			for warning in reversed(warnings):
				self._messages.insert_before(list_iter,
					[ ui_icon,
					  warning.get_message(),
					  warning.get_filename(),
					  long(warning.get_line_number()),
					  None ])
		else:
			ui_icon = Gtk.STOCK_DIALOG_ERROR
			self._messages.insert_before(list_iter,
				[ ui_icon,
				  _T("Internal Error: Unable to retreive the multidefined references from the LaTeX log"),
				  None,
				  long(0),
				  None ])
		self._messages.remove(list_iter)

	def _replace_by_undefined_citation_warnings(self, list_iter, log_file):
		if not self._latex_parser:
			self._latex_parser = log_parser.Parser(log_file)
		warnings = self._latex_parser.get_undefined_citation_warnings()
		if warnings:
			ui_icon = Gtk.STOCK_DIALOG_WARNING
			for warning in reversed(warnings):
				self._messages.insert_before(list_iter,
					[ ui_icon,
					  warning.get_message(),
					  warning.get_filename(),
					  long(warning.get_line_number()),
					  None ])
		else:
			ui_icon = Gtk.STOCK_DIALOG_ERROR
			self._messages.insert_before(list_iter,
				[ ui_icon,
				  _T("Internal Error: Unable to retreive the undefined citations from the LaTeX log"),
				  None,
				  long(0),
				  None ])
		self._messages.remove(list_iter)

	def _do_click_on_list(self, path):
		if path:
			list_iter = self._messages.get_iter(path)
			row = self._messages[list_iter]
			# Get the filename and the line number
			filename = row[2]
			wcode = row[4]
			if wcode:
				if wcode == 'W1':
					self._replace_by_multidefined_label_warnings(list_iter, filename)
					return True
				elif wcode == 'W2':
					self._replace_by_undefined_reference_warnings(list_iter, filename)
					return True
				elif wcode == 'W3':
					self._replace_by_undefined_citation_warnings(list_iter, filename)
					return True
			elif filename:
				linenumber = row[3]
				filename = self._document_directory.resolve_relative_path(filename)
				linenumber = linenumber if linenumber>=1 else 1
				# Open the file or select the tab
				tab = self.window.get_tab_from_location(filename)
				if tab:
					# Switch to the tab and show the line
					self.window.set_active_tab(tab)
					document = tab.get_document()
					view = tab.get_view()
					line_iter = document.get_iter_at_line(linenumber - 1)
					view.scroll_to_iter(
						line_iter,
						0,
						True,
						0, 0.5)
					view.grab_focus()
				else:
					# Open a new tab at the line
					tab = self.window.create_tab_from_location(
						filename,
						None, # encoding
						linenumber, # row
						0, # column
						False, # Do not create an empty file
						True) # Switch to the tab
					view = tab.get_view()
					view.grab_focus()
				GObject.idle_add(self._on_differed_selection, tab, linenumber)
		return False

	def _on_differed_selection(self, tab, linenumber):
		if tab:
			document = tab.get_document()
			line_iter = document.get_iter_at_line(linenumber - 1)
			end_line_iter = line_iter.copy()
			end_line_iter.forward_to_line_end()
			document.select_range(line_iter, end_line_iter)		

	def on_list_click_action(self, widget, event, data=None):
		if (event.button==1 and (event.type==Gdk.EventType._2BUTTON_PRESS or event.type==Gdk.EventType._3BUTTON_PRESS)) or event.button==2:
			x, y = event.get_coords()
			path, column, cell_x, cell_y = widget.get_path_at_pos(x,y)
			if path:
				self._current_error = (int)(path.get_indices()[0])
			else:
				self._current_error = -1
			self._do_click_on_list(path)
			self.plugin.do_update_state()

