#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021 Stephane Galland <galland@arakhne.org>
#
# This program is free library; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; see the file COPYING.  If not,
# write to the Free Software Foundation, Inc., 59 Temple Place - Suite
# 330, Boston, MA 02111-1307, USA.

import logging
import sys

from autolatex2.cli.commands.document import MakerAction as extended_maker_action
from autolatex2.utils.runner import Runner
from autolatex2.make.maketool import AutoLaTeXMaker
import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.utils as texutils

import gettext
_T = gettext.gettext

# Extends MakerAction from document module (alias extended_maker_action) in order
# to inherit from this super action.
class MakerAction(extended_maker_action):

	id = 'view'

	help = _T('Performs all processing actions that are required to produce the PDF, DVI or Postscript and to view it with the specified PDF viewer')

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		#
		# DANGER: Do not call the super.run() function because it has not the expected behavior for the current command.
		#
		# Create the maker
		maker = self._internal_create_maker(args)
		self._internal_run_images(maker,  args)
		if self._internal_run_build(maker,  args):
			return self._internal_run_viewer(maker,  args)

	def _internal_run_viewer(self,  maker : AutoLaTeXMaker,  args) -> bool:
		'''
		Run the internal viewer of the 'view' command.
		:param maker: the AutoLaTeX maker.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		files = maker.rootFiles
		if not files:
			logging.error(_T("Unable to find the name of the generated file for the viewer"))
			return False

		for input_file in files:
			if not input_file:
				logging.error(_T("Unable to find the name of the generated file for the viewer"))
				return False

			pdf_file = genutils.basename2(input_file,  texutils.getTeXFileExtensions()) + '.pdf'
			logging.debug(_T("VIEWER: %s") % (pdf_file))
			
			cli = self.configuration.view.viewerCLI
			if not cli:
				logging.error(_T("Unable to find the command-line for the viewing action. Did you set the configuration?"))
				sys.exit(255)
			
			cmd = list(cli)
			cmd.append(pdf_file)
			cmd = Runner.normalizeCommand(cmd)
			if self.configuration.view.asyncview:
				if not Runner.startCommandWithoutRedirect(*cmd):
					return False
			else:
				if not Runner.runCommandWithoutRedirect(*cmd):
					return False
		return True
