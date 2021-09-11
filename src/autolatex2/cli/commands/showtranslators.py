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

from autolatex2.cli.main import AbstractMakerAction
from autolatex2.config.translator import TranslatorLevel
from autolatex2.translator.translatorobj import TranslatorRepository
from autolatex2.utils.extprint import eprint

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id = 'showtranslators'

	alias = 'translators'

	help = _T('Display the list of the installed translators and their individual loading flags')

	def run(self,  args) -> bool:
		'''
		Callback for running the command.
		:param args: the arguments.
		:return: True to continue process. False to stop the process.
		'''
		# Create the translator repository
		repository = TranslatorRepository(self.configuration)
		# Detect the translators
		repository.sync()
		# Get translator status
		installed_translators = repository.installedTranslators
		inclusions = repository.getIncludedTranslatorsWithLevels()
		# Add the implicit inclusions
		all_inclusions = dict(inclusions)
		self._add_implicit_inclusions(all_inclusions,  installed_translators,  TranslatorLevel.SYSTEM)
		self._add_implicit_inclusions(all_inclusions,  installed_translators,  TranslatorLevel.USER)
		self._add_implicit_inclusions(all_inclusions,  installed_translators,  TranslatorLevel.DOCUMENT)
		# Show the status
		self._show_inclusions(all_inclusions)
		return True

	def _show_inclusions(self,  all_inclusions : dict):
		for translator_name,  level in all_inclusions.items():
			eprint(_T("%s = %s") % (translator_name,  str(level)))

	def _add_implicit_inclusions(self,  all_inclusions : dict,  installed_translators : dict,  level : TranslatorLevel,  default_inclusion_level : TranslatorLevel = TranslatorLevel.SYSTEM):
		if level >=0 and level < len(installed_translators):
			decls = installed_translators[level]
			if decls and isinstance(decls,  dict):
				for translator_name,  translator in decls.items():
					if translator_name not in all_inclusions:
						all_inclusions[translator_name] = default_inclusion_level
