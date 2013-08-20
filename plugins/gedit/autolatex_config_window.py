# autolatex - autolatex_config_window.py
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
from gi.repository import Gtk, GdkPixbuf
# AutoLaTeX internal libs
import autolatex_utils as utils
import autolatex_translator_panel as translator_panel

#---------------------------------
# Global function to open the dialog
#---------------------------------

def open_configuration_dialog(parent, isDocumentLevel, directory):
	dialog = Window(parent, isDocumentLevel, directory)
	dialog.run()
	dialog.destroy()

#---------------------------------
# CLASS AutoLaTeXConfigurationWindow
#---------------------------------

# Gtk window that is displaying the configuration panels
class Window(Gtk.Dialog):
	__gtype_name__ = "AutoLaTeXConfigurationWindow"

	def __init__(self, parent, isDocumentLevel, directory):
		Gtk.Dialog.__init__(self,
			("Document Configuration" if isDocumentLevel else "User Configuration"),
			parent, 0,
			( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY))
		self.set_default_size(600, 500)
		# Notebook
		self._ui_notebook = Gtk.Notebook()
		self.get_content_area().add(self._ui_notebook);
		# Tab for translators
		self._ui_translatorTab = translator_panel.Panel(isDocumentLevel, directory)
		self._ui_notebook.append_page(
				self._ui_translatorTab,
				self._make_notebook_tab(
					"Translators", "autolatex-images.png"))
		self.show_all()
		# Init the notebook
		self._ui_translatorTab.init()
		# Listening the response signal
		self.connect('response', self.on_response_signal);

	def _make_notebook_tab(self, label, icon=''):
		hbox = Gtk.HBox(False,2)
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(utils.make_notebook_icon_path(icon))
		iconwgt = Gtk.Image.new_from_pixbuf(pixbuf)
		hbox.add(iconwgt)
		labelwgt = Gtk.Label(label)
		hbox.add(labelwgt)
		hbox.show_all()
		return hbox

	# Callback for response in the dialog
	def on_response_signal(self, action, data=None):
		if data == Gtk.ResponseType.APPLY:
			self._ui_translatorTab.save()
