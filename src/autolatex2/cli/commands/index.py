#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021 Stephane Galland <galland@arakhne.org>
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

import logging
import os

import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.utils as texutils
from autolatex2.cli.main import AbstractMakerAction
from autolatex2.make.maketool import AutoLaTeXMaker

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'index'

	alias = 'makeindex'

	help = _T('Performs all processing that permits to generate the index (makeindex)')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--nochdir', 
			action = 'store_true', 
			help=_T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		ddir = self.configuration.documentDirectory
		if ddir and not args.nochdir:
			os.chdir(ddir)
		maker = AutoLaTeXMaker.create(self.configuration)
		idxExt = texutils.getIndexFileExtensions()[0]
		for root_file in maker.rootFiles:
			idxFile = genutils.basename2(root_file,  texutils.getTeXFileExtensions()) + idxExt
			if not maker.run_makeindex(idxFile):
				logging.error(_T("Error when running the indexing tool"))
				return False
		return True
