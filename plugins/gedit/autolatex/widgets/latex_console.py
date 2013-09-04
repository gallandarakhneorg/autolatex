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
from gi.repository import GdkPixbuf, Gdk, Gio, Gtk

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

	def __init__(self, window):
		Gtk.ScrolledWindow.__init__(self)
		self.window = window
		self._re_file_match = re.compile("^(.+):([0-9]+):\\s*(.*?)\\s*$", re.DOTALL)
		self._document_directory = None
		# Create the store
		self._messages = Gtk.ListStore(str, str, str, long)
		# Create the list
		self._message_widget = Gtk.TreeView()
		self._message_widget.set_model(self._messages)
		column = Gtk.TreeViewColumn("Level", Gtk.CellRendererPixbuf(), stock_id=0)
		self._message_widget.append_column(column)
		column = Gtk.TreeViewColumn("Text", Gtk.CellRendererText(), text=1)
		self._message_widget.append_column(column)
		self._message_widget.set_headers_clickable(False)
		self._message_widget.set_headers_visible(False)
		# Init the scroll
		self.add(self._message_widget)
		self.set_size_request(300, 200)
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
					[ ui_icon, m, filename, linenumber ])
				self._messages.append(
					[ None, message, filename, linenumber ])
			else:
				self._messages.append(
					[ ui_icon, message, filename, linenumber ])
		elif latex_warnings:
			# Add the warnings
			ui_icon = Gtk.STOCK_DIALOG_WARNING
			for latex_warning in latex_warnings:
				self._messages.append(
					[ ui_icon, latex_warning, None, long(0) ])
		if log:
			return ConsoleMode.SHOW
		if latex_warnings:
			return ConsoleMode.OPTIONAL
		return ConsoleMode.HIDE

	def on_list_click_action(self, widget, event, data=None):
		if (event.button==1 and (event.type==Gdk.EventType._2BUTTON_PRESS or event.type==Gdk.EventType._3BUTTON_PRESS)) or event.button==2:
			x, y = event.get_coords()
			path, column, cell_x, cell_y = widget.get_path_at_pos(x,y)
			if path:
				list_iter = self._messages.get_iter(path)
				row = self._messages[list_iter]
				# Get the filename and the line number
				filename = row[2]
				if filename:
					linenumber = row[3]
					filename = self._document_directory.resolve_relative_path(filename)
					linenumber = linenumber if linenumber>=1 else 1
					# Open the file or select the tab
					tab = self.window.get_tab_from_location(filename)
					if tab:
						# Switch to the tab and show the line
						self.window.set_active_tab(tab)
						document = tab.get_document()
						line_iter = document.get_iter_at_line(linenumber)
						view = tab.get_view()
						view.scroll_to_iter(
							line_iter,
							0,
							True,
							0, 0.5)
					else:
						# Open a new tab at the line
						tab = self.window.create_tab_from_location(
							filename,
							None, # encoding
							linenumber, # row
							0, # column
							False, # Do not create an empty file
							True) # Switch to the tab
					# Grap the focus
					if tab:
						view = tab.get_view()
						view.grab_focus()

