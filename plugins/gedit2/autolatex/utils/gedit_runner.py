#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/utils/gtk_utils.py
# Copyright (C) 2013-14  Stephane Galland <galland@arakhne.org>
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

from gi.repository import GObject, Gtk, Gedit
import runner

# List of all the runners
_all_runners = []

def kill_all_runners():
	runner.kill_all_runners()

class Runner(runner.Listener):

	def __init__(self, caller, label, show_progress, directory, directive, params):
		runner.Listener.__init__(self)
		self._caller = caller
		self._info_bar_label = label
		self._show_progress = bool(show_progress)
		self._gedit_tab = None
		self._info_bar = None
		self._sig_info_bar_response = 0
		self._sig_info_bar_remove = 0
		self._automatic_bar_creation = False
		self._last_fraction = 0
		self._last_comment = None
		self._thread = runner.Runner(self, directory, directive, params)

	def start(self):
		if self._thread:
			self._thread.start()

	def cancel(self):
		if self._thread:
			self._thread.cancel()
			self._thread = None
			if self._info_bar:
				self._info_bar.set_response_sensitive(
					Gtk.ResponseType.CANCEL,
					False)

	def get_runner_progress(self):
		return self._show_progress and self._info_bar_label is not None

	def on_runner_add_ui(self):
		self._gedit_tab = self._caller.window.get_active_tab()
		GObject.idle_add(self._add_info_bar)

	def on_runner_remove_ui(self):
		GObject.idle_add(self._hide_info_bar)

	def on_runner_progress(self, amount, comment):
		GObject.idle_add(self._update_info_bar, amount, comment)

	def on_runner_finalize_execution(self, retcode, output, latex_warnings):
		self._automatic_bar_creation = False
		GObject.idle_add(self._caller._update_action_validity,
			True, output, latex_warnings)

	def _add_info_bar(self):
		if self._gedit_tab:
			self._info_bar = Gedit.ProgressInfoBar()
			self._info_bar.set_stock_image(Gtk.STOCK_EXECUTE)
			self._info_bar.set_text(self._info_bar_label)
			self._sig_info_bar_response = self._info_bar.connect(
					"response",
					self._on_cancel_action)
			self._sig_info_bar_remove = self._info_bar.connect(
					"parent-set",
					self._on_parent_remove_action)
			self._gedit_tab.set_info_bar(self._info_bar)
			self._info_bar.show()
			self._gedit_tab.grab_focus();

	def _hide_info_bar(self):
		if self._info_bar:
			self._info_bar.hide()
			self._info_bar.disconnect(self._sig_info_bar_response);
			self._info_bar.disconnect(self._sig_info_bar_remove);
			self._info_bar.destroy()
			self._info_bar = None
		self._gedit_tab.grab_focus();

	def _on_cancel_action(self, widget, response, data=None):
		if response == Gtk.ResponseType.CANCEL:
			self.cancel()

	def _on_parent_remove_action(self, widget, oldParent=None, data=None):
		# The progress bar was removed by an other info bar
		bar = self._info_bar
		if bar and bar.get_parent() == None:
			self._hide_info_bar()
			self._automatic_bar_creation = True
			GObject.idle_add(self._update_info_bar,
				self._last_fraction, self._last_comment)

	def __has_info_child(self):
		if self._gedit_tab:
			for child in self._gedit_tab.get_children():
				if isinstance(child, Gtk.InfoBar):
					return True # Search says: has info bar
			return False # Search says: no info bar
		return True # Assume that the panel is inside

	def _update_info_bar(self, progress_value, comment):
		#print "MOVE TO "+str(progress_value)+"/"+str(comment)
		self._last_fraction = progress_value
		self._last_comment = comment
		if self._automatic_bar_creation and not self._info_bar and not self.__has_info_child():
			self._automatic_bar_creation = False
			GObject.idle_add(self._add_info_bar)
		GObject.idle_add(self.__set_info_bar_data, progress_value, comment)

	def __set_info_bar_data(self, progress_value, comment):
		#print "MOVE TO "+str(progress_value)+"/"+str(comment)
		if self._info_bar:
			self._info_bar.set_fraction(progress_value)
			if comment:
				self._info_bar.set_text(comment)
			self._info_bar.show()

