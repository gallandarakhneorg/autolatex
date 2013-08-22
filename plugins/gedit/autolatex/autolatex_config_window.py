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
import autolatex_generator_panel as generator_panel
import autolatex_figure_panel as figure_panel
import autolatex_figure_assignment_panel as figure_assignment_panel
import autolatex_translator_panel as translator_panel
import autolatex_viewer_panel as viewer_panel

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext

#---------------------------------
# Global function to open the dialog
#---------------------------------

def open_configuration_dialog(parent, is_document_level, directory):
	dialog = Window(parent, is_document_level, directory)
	dialog.run()
	dialog.destroy()

#---------------------------------
# CLASS NotbookTab
#---------------------------------

class NotebookTab(Gtk.HBox):
	__gtype_name__ = "AutoLaTeXConfigurationNotebookTab"

	def __init__(self, label, icon):
		Gtk.HBox.__init__(self,False,2)
		self._label = label
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(utils.make_notebook_icon_path(icon))
		iconwgt = Gtk.Image.new_from_pixbuf(pixbuf)
		self.add(iconwgt)
		labelwgt = Gtk.Label(self._label)
		labelwgt.set_alignment(0, 0.5)
		self.add(labelwgt)
		self.show_all()

	def get_text(self):
		return self._label

#---------------------------------
# CLASS AutoLaTeXConfigurationWindow
#---------------------------------

# Gtk window that is displaying the configuration panels
class Window(Gtk.Dialog):
	__gtype_name__ = "AutoLaTeXConfigurationWindow"

	def __init__(self, parent, is_document_level, directory):
		Gtk.Dialog.__init__(self,
			(_T("Document Configuration") if is_document_level else _T("User Configuration")),
			parent, 0,
			( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY))
		self.set_default_size(600, 500)
		# Notebook
		self._ui_notebook = Gtk.Notebook()
		self.get_content_area().add(self._ui_notebook);
		# Tab for translators
		tab = generator_panel.Panel(is_document_level, directory)
		self._ui_notebook.append_page(
				tab,
				NotebookTab(
					_T("Generator"), "autolatex-compile.png"))
		tab = figure_panel.Panel(is_document_level, directory, self)
		self._ui_notebook.append_page(
				tab,
				NotebookTab(
					_T("Figures"), "autolatex-images.png"))
		if is_document_level:
			tab = figure_assignment_panel.Panel(directory)
			self._ui_notebook.append_page(
					tab,
					NotebookTab(
						_T("List of figures"), "autolatex-images.png"))
		tab = translator_panel.Panel(is_document_level, directory)
		self._ui_notebook.append_page(
				tab,
				NotebookTab(
					_T("Translators"), "autolatex-images.png"))
		tab = viewer_panel.Panel(is_document_level, directory)
		self._ui_notebook.append_page(
				tab,
				NotebookTab(
					_T("Viewer"), "autolatex-view.png"))
		self.show_all()
		# Listening the response signal
		self.connect('response', self.on_response_signal);

	# Callback for response in the dialog
	def on_response_signal(self, action, data=None):
		if data == Gtk.ResponseType.APPLY:
			for i in range(self._ui_notebook.get_n_pages()):
				page = self._ui_notebook.get_nth_page(i)
				result = page.save()
				if not result:
					tab_label = self._ui_notebook.get_tab_label(page)
					dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _T("The page '%s' cannot save its fields.\n You will loose the changes on this pages.") % tab_label.get_text())
					answer = dialog.run()
					dialog.destroy()

