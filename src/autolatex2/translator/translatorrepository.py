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

'''
Translation engine.
'''

import os
import re
import logging

from autolatex2.config .configobj import Config
from autolatex2.config .translator import TranslatorLevel
from autolatex2.translator.translatorobj import Translator

import gettext
_T = gettext.gettext


######################################################################
##
class TranslatorConflictError(Exception):

	def __init__(self, msg):
		super().__init__(msg)
		self.message = msg

	def __str__(self) -> str:
		return self.message



######################################################################
##
class TranslatorRepository(object):
	'''
	Repository of translators.
	'''

	def __init__(self, configuration : Config):
		'''
		Construct the repository of translators.
		:param configuration: The current configuration.
		:type configuration: Config
		'''
		self.configuration = configuration
		self._installedTranslators = list((None, None, None))
		self._installedTranslators[TranslatorLevel.SYSTEM] = dict()
		self._installedTranslators[TranslatorLevel.USER] = dict()
		self._installedTranslators[TranslatorLevel.DOCUMENT] = dict()
		self._installedTranslatorNames = set()
		self._includedTranslators = dict()

	@property
	def installedTranslators(self) -> list:
		'''
		Replies the installed translators.
		The function sync() must be call for updating the list of the installed translators.
		:return: The lists of the dictionary of the installed translators in which the keys are the names and the values are the filename of the translators.
		:rtype: list
		'''
		return self._installedTranslators

	@property
	def installedTranslatorNames(self) -> set:
		'''
		Replies the names of the installed translators.
		:return: The set of the names.
		:rtype: set
		'''
		return self._installedTranslatorNames

	@property
	def includedTranslators(self) -> dict:
		'''
		Replies the included translators.
		The function sync() must be call for updating the list of the included translators.
		:return: The dictionary of the included translators in which the keys are the source types and the values are the translators.
		:rtype: dict
		'''
		return self._includedTranslators

	def _readDirectory(self, *, directory : str, recursive : bool = False, warn : bool = False):
		'''
		Detect translators from from the translator files installed in the directory.
		:param directory: The path to the directory to explore.
		:type directory: str
		:param recursive: Indicates if the function must recurse in the directories. Default value: False.
		:type recursive: bool
		:param warn: Indicates if the warning may be output or not. Default value: False.
		:type warn: bool
		:return: The loaded translators.
		:rtype: dict
		'''
		loadedTranslators = dict()

		if os.path.isdir(directory):
			if not os.path.isabs(directory):
				directory = os.path.abspath(directory)
			if recursive:
				for root, dirs, files in os.walk(directory):
					for filename in files:
						m = re.match(r'^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef([0-9]*)$', filename, re.I)
						if m:
							scriptname = m.group(1)
							version = m.group(2)
							if (version and int(version) > 1) or self.configuration.translators.is_translator_fileformat_1_enable:
								translator = Translator(scriptname, self.configuration)
								translator.filename = os.path.join(root, filename)
								loadedTranslators[scriptname] = translator
			else:
				for child in os.listdir(directory):
					absPath = os.path.join(directory, child)
					if not os.path.isdir(absPath):
						m = re.match(r'^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef([0-9]*)$', child, re.I)
						if m:
							scriptname = m.group(1)
							version = m.group(2)
							if (version and int(version) > 1) or self.configuration.translators.is_translator_fileformat_1_enable:
								translator = Translator(scriptname, self.configuration)
								translator.filename = absPath
								loadedTranslators[scriptname] = translator
		elif warn:
			logging.fine_warning(_T("%s is not a directory") % (directory))

		return loadedTranslators

	def _getInstallLevelFor(self, translatorName : str) -> TranslatorLevel:
		'''
		Search for the translator in the installed translators, and reply its level.
		:param translatorName: The name of the translator.
		:type translatorName: str
		:return: The level, or None if not found
		:rtype: TranslatorLevel
		'''
		lvls = list(TranslatorLevel)[1:]
		for level in reversed(lvls):
			if translatorName in self._installedTranslators[level.value]:
				return level
		return None

	def _getObjectFor(self, translatorName : str) -> Translator:
		'''
		Search for the translator in the installed translators.
		:param translatorName: The name of the translator.
		:type translatorName: str
		:return: The translator, or None if not found
		:rtype: Translator
		'''
		lvls = list(TranslatorLevel)
		for level in reversed(lvls):
			if translatorName in self._installedTranslators[level.value]:
				return self._installedTranslators[level.value][translatorName]
		return None

	def getIncludedTranslatorsWithLevels(self) -> dict:
		'''
		Replies the included translators according to the given configuration.
		All the translators are included, except if the configuration specify something different.
		:return: The dictionary with translator names as keys and inclusion levels as values.
		:rtype: dict
		'''
		included = dict()
		for translatorName in self._installedTranslatorNames:
			installLevel = self._getInstallLevelFor(translatorName)
			if installLevel is not None:
				inc = self.configuration.translators.inclusionLevel(translatorName)
				if inc is None:
					included[translatorName] = installLevel
				elif  inc != TranslatorLevel.NEVER:
					if inc >= installLevel:
						included[translatorName] = TranslatorLevel(inc)
					else:
						included[translatorName] = installLevel
		return included

	def _detectConflicts(self) -> list:
		'''
		Replies the translators under conflict per level and source according to the given configuration.
		:return: The data structure described by list[level] = dict(source, set(translator))).
		:rtype: list
		'''
		conflicts = list((dict(), dict(), dict()))
		# Build the list of the included translators per level
		translators = self.getIncludedTranslatorsWithLevels()
		for (translatorName, activationLevel) in translators.items():
			translator = self._getObjectFor(translatorName)
			source = translator.fullSource
			for aLevel in (range(activationLevel,len(conflicts))):
				if source not in conflicts[aLevel]:
					conflicts[aLevel][source] = set()
				conflicts[aLevel][source].add(translator)
		# Remove any entry that are not indicating a translator conflict.
		for levelDict in conflicts:
			toDelete = list()
			for k, v in levelDict.items():
				if v and len(v) <= 1:
					toDelete.append(k)
			for k in toDelete:
				del levelDict[k]
		return conflicts

	def sync(self, detect_conflicts : bool = True):
		'''
		Synchronize the repository with directories according to the given configuration.
		:param detect_conflicts: Indicates if the conflicts in translator loading is run. Default is True.
		:type detect_conflicts: bool
		'''
		self._installedTranslators = list((None, None, None))
		self._installedTranslators[TranslatorLevel.SYSTEM] = dict()
		self._installedTranslators[TranslatorLevel.USER] = dict()
		self._installedTranslators[TranslatorLevel.DOCUMENT] = dict()
		self._installedTranslatorNames = set()
		self._includedTranslators = dict()

		# Load distribution/system modules
		if not self.configuration.translators.ignoreSystemTranslators:
			dirname = os.path.join(self.configuration.installationDirectory, 'translators')
			logging.debug(_T("Get loadable translators from %s") % (dirname))
			v0 = self._readDirectory(directory=dirname, recursive=True, warn=True)
			self._installedTranslators[TranslatorLevel.SYSTEM].update(v0)

		# Load user modules recursively from ~/.autolatex/translators
		if not self.configuration.translators.ignoreUserTranslators:
			dirname = os.path.join(self.configuration.userConfigDirectory, 'translators')
			logging.debug(_T("Get loadable translators from %s") % (dirname))
			v1 = self._readDirectory(directory=dirname, recursive=True, warn=True)
			self._installedTranslators[TranslatorLevel.USER].update(v1)

		# Load user modules non-recursively the paths specified inside the configurations
		for path in self.configuration.translators.includePaths:
			logging.debug(_T("Get loadable translators from %s") % (path))
			v2 = self._readDirectory(directory=path, recursive=True, warn=True)
			self._installedTranslators[TranslatorLevel.DOCUMENT].update(v2)

		# Load document modules
		directory = self.configuration.documentDirectory
		if not self.configuration.translators.ignoreDocumentTranslators:
			if directory is not None:
				logging.debug(_T("Get loadable translators from %s") % (directory))
				v3 = self._readDirectory(directory=directory, recursive=False, warn=True)
				self._installedTranslators[TranslatorLevel.DOCUMENT].update(v3)

		# Finalize initialization of the loadable translators.
		for translator in self._installedTranslators[TranslatorLevel.SYSTEM].values():
			translator.level = TranslatorLevel.SYSTEM
			self._installedTranslatorNames.add(translator.name)
		for translator in self._installedTranslators[TranslatorLevel.USER].values():
			translator.level = TranslatorLevel.USER
			self._installedTranslatorNames.add(translator.name)
		for translator in self._installedTranslators[TranslatorLevel.DOCUMENT].values():
			translator.level = TranslatorLevel.DOCUMENT
			self._installedTranslatorNames.add(translator.name)

		# Determine the included translators
		if detect_conflicts:
			conflicts = self._detectConflicts()
			if directory:
				specificConflicts = conflicts[TranslatorLevel.DOCUMENT]
				filename = self.configuration.makeDocumentConfigFilename(directory)
			else:
				specificConflicts = conflicts[TranslatorLevel.USER]
				filename = self.configuration.userConfigFile

			self._failOnConflict(specificConflicts, filename)

		# Save the included translators
		self._includedTranslators = self._buildIncludedTranslatorDict()

	def _buildIncludedTranslatorDict(self) -> dict:
		'''
		Build the dictionary of the included translators.
		:return: The dictionary with source types as keys, and translators as values.
		:type configFilename: dict
		'''
		included = dict()
		for translatorName in self.getIncludedTranslatorsWithLevels():
			translator = self._getObjectFor(translatorName)
			source = translator.fullSource
			included[source] = translator
		return included
		

	def _failOnConflict(self, conflicts : dict, configFilename : str):
		'''
		Fail if a conflict exists between translators.
		:param conflicts: The list of conflicts, replied by the function _detectConflicts().
		:type conflicts: dict
		:param configFilename: The filename of the configuration file to put in the error message.
		:type configFilename: str
		'''
		for source, translators in conflicts.items():
			msg = ''
			excludemsg = ''
			firstTranslator = None
			for translator in translators:
				if msg:
					msg += ",\n"
				msg += str(translator)
				if firstTranslator is None:
					excludemsg += "[%s]\ninclude module = yes\n" % (translator.name)
					firstTranslator = translator
				else:
					excludemsg += "[%s]\ninclude module = no\n" % (translator.name)
			raise TranslatorConflictError(_T("Several possibilities exist for generating a figure from a %s file:\n%s\n\nYou must specify which to include (resp. exclude) with --include (resp. --exclude).\n\nIt is recommended to update your %s file with the following configuration for each translator to exclude (example on the translator %s):\n\n%s\n" %
							(	source,
								msg,
								configFilename,
								firstTranslator.name,
								excludemsg )))
