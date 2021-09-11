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
import sys

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.config.configwriter import OldStyleConfigWriter
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'createconfig'

	help = _T('Create a configuration file. The configuration file is \'.autolatex_project.cfg\' on Unix and \'autolatex_project.cfg\' on other platforms. '
		'The content of the configuration file depends on the current state of the configuration')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--force', 
			action = 'store_true', 
			help=_T('Force to overwrite the configuration file if it exists'))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		dout = self.configuration.documentDirectory
		fout = self.configuration.makeDocumentConfigFilename(dout)
		if os.path.isfile(fout) and not args.force:
			logging.error(_T("File already exists: %s") % (fout))
			sys.exit(255)
		writer = OldStyleConfigWriter()
		try:
			logging.info(_T("Creating configuration file %s") % (fout))
			genutils.unlink(fout)
			os.makedirs(dout, exist_ok=True)
			writer.write(fout,  self.configuration)
			return True
		except BaseException as ex:
			logging.error(str(ex))
			return False
