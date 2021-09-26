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

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.utils.extprint import eprint

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'showloadedtranslators'

	alias = 'translators'

	help = _T('Display the list of the loaded translators and their highest loading levels')

	def _add_command_cli_arguments(self,  action_parser, command):
		'''
		Callback for creating the CLI arguments (positional and optional).
		:param action_parser: The argparse object
		:param command: The description of the command.
		'''
		level_group = action_parser.add_mutually_exclusive_group()

		level_group.add_argument('--level',
			action='store_true',
			default=True, 
			dest='showactivationtranslatorlevel', 
			help=_T('Show the activation level for each translator'))

		level_group.add_argument('--nolevel',
			action='store_false',
			dest='showactivationtranslatorlevel', 
			help=_T('Hide the activation level for each translator'))


	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		# Create the translator repository
		repository = TranslatorRepository(self.configuration)
		# Detect the translators
		repository.sync(False)
		# Get translator status
		inclusions = repository.getIncludedTranslatorsWithLevels()
		# Show the list
		if args.showactivationtranslatorlevel:
			self._show_inclusions(inclusions)
		else:
			self._show_inclusion_names_only(inclusions)
		return True

	def _show_inclusions(self,  all_inclusions : dict):
		sorted_dict = {k: all_inclusions[k] for k in sorted(all_inclusions)}
		for translator_name,  level in sorted_dict.items():
			eprint(_T("%s = %s") % (translator_name,  str(level)))

	def _show_inclusion_names_only(self,  all_inclusions : dict):
		sorted_dict = {k: all_inclusions[k] for k in sorted(all_inclusions)}
		for translator_name,  level in sorted_dict.items():
			eprint(translator_name)
