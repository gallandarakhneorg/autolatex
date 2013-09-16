#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/utils/gtk_utils.py
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

from gi.repository import GObject, Gtk, Gedit
import runner


class Runner(runner.Listener):

	def __init__(self, caller, label, show_progress, directory, directive, params):
		runner.Listener.__init__(self)
		self._caller = caller
		self._info_bar_label = label
		self._show_progress = bool(show_progress)
		self._info_bar = None
		self._sig_info_bar = 0
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
		GObject.idle_add(self._add_info_bar)

	def on_runner_remove_ui(self):
		GObject.idle_add(self._hide_info_bar)

	def on_runner_progress(self, amount, comment):
		GObject.idle_add(self._update_info_bar, amount, comment)

	def on_runner_finalize_execution(self, retcode, output, latex_warnings):
		GObject.idle_add(self._caller._update_action_validity,
			True, output, latex_warnings)

	def _add_info_bar(self):
		gedit_tab = self._caller.window.get_active_tab()
		self._info_bar = Gedit.ProgressInfoBar()
		self._info_bar.set_stock_image(Gtk.STOCK_EXECUTE)
		self._info_bar.set_text(self._info_bar_label)
		self._sig_info_bar = self._info_bar.connect(
				"response",
				self._on_cancel_action);
		self._info_bar.show()
		gedit_tab.set_info_bar(self._info_bar)

	def _hide_info_bar(self):
		if self._info_bar:
			self._info_bar.disconnect(self._sig_info_bar);
			self._info_bar.destroy()
			self._info_bar = None

	def _on_cancel_action(self, widget, response, data=None):
		if response == Gtk.ResponseType.CANCEL:
			self.cancel()

	def _update_info_bar(self, progress_value, comment):
		if self._info_bar:
			self._info_bar.set_fraction(progress_value)
			if comment:
				self._info_bar.set_text(comment)


