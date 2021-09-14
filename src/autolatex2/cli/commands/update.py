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

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.utils.runner import Runner

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'update'

	help = _T('Update the current document from your preferred SCM system. Update is done through the dedicated command-line in the configuration')

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		cli = self.configuration.scm.updateCLI
		if not cli:
			logging.error(_T("Unable to find the command-line for the updating action. Did you set the configuration?"))
			sys.exit(255)
		
		cmd = list(cli)
		cmd = Runner.normalizeCommand(cmd)
		exit_code = Runner.runCommandWithoutRedirect(*cmd)
		return exit_code == 0
