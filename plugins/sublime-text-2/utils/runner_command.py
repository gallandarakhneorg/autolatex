#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/utils/runner_command.py
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

import os
import sublime
import utils, runner
import gettext

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

_T = gettext.gettext


class AbstractRunnerCommand(runner.Listener):

	def __init__(self):
		runner.Listener.__init__(self)
		self._thread = None
		self._show_progress = True

	def cancel_task(self):
		if self._thread:
				self._thread.cancel()

	def start_task(self, show_progress, encoding, working_dir, directive, params):
		self._encoding = encoding
		self._show_progress = show_progress

		# Default the to the current files directory if no working directory was given
		if (working_dir == "" and self.window.active_view()
			        and self.window.active_view().file_name()):
		    working_dir = os.path.dirname(self.window.active_view().file_name())

		if not hasattr(self, 'output_view'):
		    # Try not to call get_output_panel until the regexes are assigned
		    self.output_view = self.window.get_output_panel("autolatex")

		self.output_view.settings().set("result_file_regex", "^(.*?):([0-9]+):(?:([0-9]+):)?\\s*(.*?)\\s*$")
		self.output_view.settings().set("result_line_regex", "^l\\.([0-9]+)\\s+")
		self.output_view.settings().set("result_base_dir", working_dir)

		# Call get_output_panel a second time after assigning the above
		# settings, so that it'll be picked up as a result buffer
		self.window.get_output_panel("autolatex")

		# Show the progress
		if self._show_progress:
			sublime.status_message(_T("Building [%d%%]") % int(0))

		autolatex_directory = utils.find_AutoLaTeX_directory(working_dir)
		self._thread = runner.Runner(
				self,
				autolatex_directory,
				directive,
				params)
		self._thread.start()
		

	def get_runner_progress(self):
		return self._show_progress

	def on_runner_add_ui(self):
		sublime.status_message(_T("Building [%d%%]") % 0)
		show_panel_on_build = sublime.load_settings("Preferences.sublime-settings").get("show_panel_on_build", True)
		if show_panel_on_build:
			self.window.run_command("show_panel", {"panel": "output.autolatex"})

	def on_runner_remove_ui(self):
		pass

	def on_runner_progress(self, amount, comment):
		if comment:
			sublime.status_message(_T("Building [%d%%]: %s") % (int(amount * 100), comment))
		else:
			sublime.status_message(_T("Building [%d%%]") % int(amount * 100))

	def on_runner_finalize_execution(self, retcode, output, latex_warnings):
		messages = []
		if retcode != 0:
			messages.append(output)
		else:
			for warning in latex_warnings:
				messages.append(warning[1]+":1: "+warning[0])

		for message in messages:
			try:
			    message = message.decode(self._encoding)
			except:
			    message = _T("[Decode error - output not %s]") % self._encoding

			# Normalize newlines, Sublime Text always uses a single \n separator
			# in memory.
			message = message.replace('\r\n', '\n').replace('\r', '\n')

		        selection_was_at_end = (len(self.output_view.sel()) == 1
			    and self.output_view.sel()[0]
				== sublime.Region(self.output_view.size()))

			self.output_view.set_read_only(False)
			edit = self.output_view.begin_edit()
			self.output_view.insert(edit, self.output_view.size(), message)
			if selection_was_at_end:
			    self.output_view.show(self.output_view.size())
			self.output_view.end_edit(edit)
			self.output_view.set_read_only(True)

		if retcode!=0:
		    sublime.status_message(_T("Build finished with an error"))
		elif len(latex_warnings) == 0:
		    sublime.status_message(_T("Build finished"))
		else:
		    sublime.status_message(_T("Build finished with %d warnings") % len(latex_warnings))

		# Set the selection to the start, so that next_result will work as expected
		edit = self.output_view.begin_edit()
		self.output_view.sel().clear()
		self.output_view.sel().add(sublime.Region(0))
		self.output_view.end_edit(edit)
