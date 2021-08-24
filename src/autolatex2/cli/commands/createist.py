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
import shutil
import sys

from autolatex2.cli.main import AbstractMakerAction
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'createist'

	help = _T('Create a default MakeIndex style file into the document directory. The created file will be named \'default.ist\'. If a file with this name already exists, it will be overwritten')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		action_parser.add_argument('--force', 
			action = 'store_true', 
			help=_T('Force to overwrite the IST file if it exists'))

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		'''
		fin = self.configuration.get_system_ist_file()
		dout = self.configuration.documentDirectory
		fout = os.path.join(dout,  'default.ist')
		if os.path.isfile(fout) and not args.force:
			logging.error(_T("File already exists: %s") % (fout))
			sys.exit(255)
		try:
			logging.info(_T("Copying %s to %s") % (fin,  dout))
			genutils.unlink(fout)
			os.makedirs(dout, exist_ok=True)
			shutil.copyfile(fin,  fout)
			return True
		except object as ex:
			logging.error(str(ex))
			return False
