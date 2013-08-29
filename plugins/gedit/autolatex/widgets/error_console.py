# autolatex/widgets/error_console.py
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
from gi.repository import Gdk, Gio, Gtk

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the plugin
class ErrorConsole(Gtk.TextView):
	__gtype_name__ = "AutoLaTeXErrorConsole"

	def __init__(self, window):
		Gtk.TextView.__init__(self)
		self.window = window
		self.set_editable(False)
		self.set_hscroll_policy(Gtk.ScrollablePolicy.NATURAL)
		self.set_vscroll_policy(Gtk.ScrollablePolicy.NATURAL)
		self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
		self.set_cursor_visible(False)
		self.connect('button-press-event', self.on_press_event)
		self._re_file_match = re.compile("^(.+):([0-9]+):")
		self._document_directory = None
		

	# Set the text of the log
	def set_log(self, log, document_directory):
		self.get_buffer().set_text(log)
		self._document_directory = Gio.File.new_for_path(document_directory)

	def on_press_event(self, widget, event, data=None):
		y = None
		if (event.button==1):
			if event.type==Gdk.EventType._2BUTTON_PRESS or event.type==Gdk.EventType._3BUTTON_PRESS:
				y = event.y
		elif (event.button==2):
			y = event.y
		if (y is not None):
			line_iter = self.get_line_at_y(y)[0]
			end_iter = line_iter.copy()
			end_iter.forward_line()
			text = line_iter.get_visible_text(end_iter)
			mo = re.match(self._re_file_match, text)
			if mo:
				filename = mo.group(1)
				linenumber = int(mo.group(2))
				filename = self._document_directory.resolve_relative_path(filename)
				# Try to active the document
				tab = self.window.get_tab_from_location(filename)
				if tab:
					# Switch to the tab and show the line
					self.window.set_active_tab(tab)
					document = tab.get_document()
					line_iter = document.get_iter_at_line(0)
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
				# Select the line
				if tab:
					view = tab.get_view()
					view.set_highlight_current_line(True)
					view.grab_focus()
