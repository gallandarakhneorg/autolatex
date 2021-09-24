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

import os
import logging

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.utils.extprint import eprint

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'showconfigfiles'

	help = _T('Display the list of the detected configuration files that will be read by autolatex')

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		system_path = self.configuration.systemConfigFile
		if system_path is not None:
			if os.path.isfile(system_path):
				if os.access(system_path, os.R_OK):
					eprint(system_path)
				else:
					logging.error(_T("%s (unreable)") % (system_path))
			else:
				logging.error(_T("%s (not found)") % (system_path))

		user_path = self.configuration.userConfigFile
		if user_path is not None:
			if os.path.isfile(user_path):
				if os.access(user_path, os.R_OK):
					eprint(user_path)
				else:
					logging.error(_T("%s (unreadable)") % (user_path))
			else:
				logging.error(_T("%s (not found)") % (user_path))

		document_directory = self.configuration.documentDirectory
		if document_directory is None:
			logging.error(_T("Cannot detect document directory"))
		else:
			doc_path = self.configuration.makeDocumentConfigFilename(document_directory)
			if doc_path is not None:
				if os.path.isfile(doc_path):
					if os.access(doc_path, os.R_OK):
						eprint(doc_path)
					else:
						logging.error(_T("%s (unreadable)") % (doc_path))
				else:
					logging.error(_T("%s (not found)") % (doc_path))

		return True
