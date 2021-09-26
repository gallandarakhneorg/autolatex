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
from autolatex2.config.translator import TranslatorLevel
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.utils.extprint import eprint

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'showinstalledtranslators'

	alias = 'installedtranslators'

	help = _T('Display the list of the installed translators and their highest loading levels')

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
			dest='showinstalledtranslatorlevel', 
			help=_T('Show the installation level for each translator'))

		level_group.add_argument('--nolevel',
			action='store_false',
			dest='showinstalledtranslatorlevel', 
			help=_T('Hide the installation level for each translator'))


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
		installed_translators = repository.installedTranslators
		inclusions = repository.getIncludedTranslatorsWithLevels()
		# Add the implicit inclusions
		all_inclusions = dict(inclusions)
		self._add_implicit_inclusions(all_inclusions,  installed_translators,  TranslatorLevel.SYSTEM)
		self._add_implicit_inclusions(all_inclusions,  installed_translators,  TranslatorLevel.USER)
		self._add_implicit_inclusions(all_inclusions,  installed_translators,  TranslatorLevel.DOCUMENT)
		if args.showinstalledtranslatorlevel:
			# Show the level
			self._show_inclusions(all_inclusions)
		else:
			# Hide the level
			self._show_inclusion_names_only(all_inclusions)
		return True

	def _show_inclusions(self,  all_inclusions : dict):
		sorted_dict = {k: all_inclusions[k] for k in sorted(all_inclusions)}
		for translator_name,  level in sorted_dict.items():
			eprint(_T("%s = %s") % (translator_name,  str(level)))

	def _show_inclusion_names_only(self,  all_inclusions : dict):
		sorted_dict = {k: all_inclusions[k] for k in sorted(all_inclusions)}
		for translator_name,  level in sorted_dict.items():
			eprint(translator_name)

	def _add_implicit_inclusions(self,  all_inclusions : dict,  installed_translators : dict,  level : TranslatorLevel,  default_inclusion_level : TranslatorLevel=TranslatorLevel.SYSTEM):
		if level >=0 and level < len(installed_translators):
			decls = installed_translators[level]
			if decls and isinstance(decls,  dict):
				for translator_name,  translator in decls.items():
					if translator_name not in all_inclusions:
						all_inclusions[translator_name] = default_inclusion_level
