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

'''
Translation engine.
'''

import os
import re
import logging
import shlex
import subprocess
import importlib

import autolatex2.utils.utilfunctions as genutils
from autolatex2.config .configobj import Config
from autolatex2.config .translator import TranslatorLevel
from autolatex2.translator .transdefreader import YamlTransdefReader
from autolatex2.translator .transdefreader import PerlTransdefReader

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
class TranslatorError(Exception):

	def __init__(self, msg):
		super().__init__(msg)
		self.message = msg

	def __str__(self) -> str:
		return self.message


	

######################################################################
##
class Translator(object):
	'''
	Description of a translator.
	'''

	def __init__(self, name : str, configuration : Config):
		'''
		Parse a complete translator name to extract the components.
		:param name: The name must have the syntax:<ul>
				<li><code>source2target</code></li>
				<li><code>source2target+target2</code></li>
				<li><code>source2target_variante</code></li>
				<li><code>source2target+target2_variante</code></li>
				</li>
		:type: str
		:param configuration: The current AutoLaTeX configuration.
		:type configuration: Config
		'''
		self.configuration = configuration
		self.__name = None
		self.__basename = None
		self.__source = None
		self.__fullSource = None
		self.__target = None
		self.__variante = None
		self.__filename = None
		self.__level = None
		self.__fileContent = None
		self.decode(name)

	@classmethod
	def _label(clazz, fullSource : str, target : str, variante : str = None) -> str:
		'''
		Replies a human readable string that corresponds to the specified translator data.
		:param fullSource: The filename extension for the source file.
		:type fullSource: str
		:param target: The filename extension for the target file.
		:type target: str
		:param variante: The name of the transformation variante. Default is None.
		:type variante: str
		:rtype: str
		'''
		if variante:
			return _T("Translate %s to %s with %s alternative") % (fullSource, target, variante)
		else:
			return _T("Translate %s to %s") % (fullSource, target)

	def __str__(self):
		return Translator._label(self.fullSource, self.target, self.variante)

	def __repr__(self):
		return str(self)

	def decode(self, name: str):
		'''
		Decode the given translator name and change the properties
		of this object accordingly.
		:param name: The name must have the syntax:<ul>
				<li><code>source2target</code></li>
				<li><code>source2target+target2</code></li>
				<li><code>source2target_variante</code></li>
				<li><code>source2target+target2_variante</code></li>
				</li>
		:type: str
		'''
		m = re.match(r'^([a-zA-Z+-]+)2([a-zA-Z0-9-]+)(?:\+([a-zA-Z0-9+-]+))?(?:_(.*))?$', name)
		if m:
			source = m.group(1)
			target = m.group(2)
			target2 = m.group(3) or ''
			variante = m.group(4) or ''
			osource = source
			basename = "%s2%s%s" % (source, target, target2)
			if target2:
				if target2 == 'tex':
					source = "ltx.%s" % (source)
				elif target2 == 'layers':
					source = "layers.%s" % (source)
				elif target2 == 'layers+tex' or target2 == 'tex+layers':
					source = "layers.ltx.%s" % (source)
				else:
					target += "+%s" % (target2)
			self.__name = name
			self.__fullSource = source
			self.__source = osource
			self.__target = target
			self.__variante = variante
			self.__basename = basename
		else:
			raise RuntimeError[_T("Invalid translator name: %s") % (name)]


	@property
	def name(self) -> str:
		'''
		Name of the translator.
		:rtype: str
		'''
		return self.__name

	@property
	def source(self) -> str:
		'''
		Source type given to the constructor.
		:rtype: str
		'''
		return self.__source

	@property
	def fullSource(self) -> str:
		'''
		Source type.
		:rtype: str
		'''
		return self.__fullSource

	@property
	def target(self) -> str:
		'''
		Target type.
		:rtype: str
		'''
		return self.__target

	@property
	def variante(self) -> str:
		'''
		Variante of the translator.
		:rtype: str
		'''
		return self.__variante

	@property
	def basename(self) -> str:
		'''
		Basename of the translator.
		:rtype: str
		'''
		return self.__basename

	@property
	def filename(self) -> str:
		'''
		Replies the filename of the translator.
		:return: The filename or None.
		:rtype: str
		'''
		return self.__filename

	@filename.setter
	def filename(self, name : str):
		'''
		Set the filename of the translator.
		:param name: The filename of the translator.
		:type name: str
		'''
		self.__filename = name

	@property
	def level(self) -> TranslatorLevel:
		'''
		Replies the execution level at which this translator was defined.
		:return: The execution level of the translator.
		:rtype: TranslatorLevel
		'''
		return self.__level 

	@level.setter
	def level(self, l : TranslatorLevel):
		'''
		Set the execution level at which this translator was defined.
		:param l: The execution level of the translator.
		:type l: TranslatorLevel
		'''
		self.__level  = l

	def __readTranslatorFile(self, filename : str) -> dict:
		'''
		Replies the content of a translator definition file.
		:param filename: The filename to read.
		:type filename: str
		:return: The dictionary of the content.
		:rtype: dict
		'''
		exts = os.path.splitext(filename)
		ext = exts[-1]
		if ext == '.transdef':
			reader = PerlTransdefReader(self.configuration)
		else:
			reader = YamlTransdefReader(self.configuration)
		content = reader.readTranslatorFile(filename)
		return content

	def getInputExtensions(self) -> list:
		'''
		Replies the list of the filename extensions that are the sources for this translator.
		:rtype: list
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		if 'INPUT_EXTENSIONS' in self.__fileContent and self.__fileContent['INPUT_EXTENSIONS'] and self.__fileContent['INPUT_EXTENSIONS'].value_list:
			return list(self.__fileContent['INPUT_EXTENSIONS'].value_list)
		return list()

	def getOutputExtensions(self) -> list:
		'''
		Replies the list of the filename extensions that are the targets for this translator.
		:rtype: list
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		if 'OUTPUT_EXTENSIONS' in self.__fileContent and self.__fileContent['OUTPUT_EXTENSIONS'] and self.__fileContent['OUTPUT_EXTENSIONS'].value:
			return list(self.__fileContent['OUTPUT_EXTENSIONS'].value_list)
		return list()

	def getCommandLine(self) -> str:
		'''
		Replies the command line to run if specified in the translator definition file.
		:rtype: str
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		if 'COMMAND_LINE' in self.__fileContent and self.__fileContent['COMMAND_LINE'] and self.__fileContent['COMMAND_LINE'].value:
			return self.__fileContent['COMMAND_LINE'].value
		return None

	def getEmbeddedFunction(self) -> str:
		'''
		Replies the embedded function to run if specified in the translator definition file.
		:rtype: str
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		if 'TRANSLATOR_FUNCTION' in self.__fileContent and self.__fileContent['TRANSLATOR_FUNCTION'] and self.__fileContent['TRANSLATOR_FUNCTION'].value:
			return self.__fileContent['TRANSLATOR_FUNCTION'].value
		return None

	def getEmbeddedFunctionInterpreter(self) -> str:
		'''
		Replies the interpreter for the embedded function to run if specified in the translator definition file.
		:rtype: str
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		if 'TRANSLATOR_FUNCTION' in self.__fileContent and self.__fileContent['TRANSLATOR_FUNCTION'] and self.__fileContent['TRANSLATOR_FUNCTION'].interpreter:
			return self.__fileContent['TRANSLATOR_FUNCTION'].interpreter
		return None

	def getPythonDependencies(self) -> str:
		'''
		Replies the python dependencies that must be included in the executed script.
		:rtype: list
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		if 'TRANSLATOR_PYTHON_DEPENDENCIES' in self.__fileContent and self.__fileContent['TRANSLATOR_PYTHON_DEPENDENCIES'] and self.__fileContent['TRANSLATOR_PYTHON_DEPENDENCIES'].value_list:
			return self.__fileContent['TRANSLATOR_PYTHON_DEPENDENCIES'].value_list
		return None

	def getConstants(self) -> dict:
		'''
		Replies the constants that must be defined for the translator.
		The replied dictionary is a copy of the internal data structure.
		:return: the dictionary of the variable names and the values.
		:rtype: dict
		'''
		if self.__fileContent is None:
			self.__fileContent = self.__readTranslatorFile(self.filename)
		variables = dict()
		for k, v in self.__fileContent.items():
			if k not in [ 'INPUT_EXTENSIONS', 'OUTPUT_EXTENSIONS', 'FILES_TO_CLEAN', 'TRANSLATOR_PYTHON_DEPENDENCIES']:
				variables[k] = v.value_list
			if k not in [ 'TRANSLATOR_FUNCTION', 'COMMAND_LINE' ]:
				variables[k] = v.value
		return variables


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
						m = re.match(r'^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef[0-9]*$', filename, re.I)
						if m:
							scriptname = m.group(1)
							translator = Translator(scriptname, self.configuration)
							translator.filename = os.path.join(root, filename)
							loadedTranslators[scriptname] = translator
			else:
				for child in os.listdir(directory):
					absPath = os.path.join(directory, child)
					if not os.path.isdir(absPath):
						m = re.match(r'^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef[0-9]*$', child, re.I)
						if m:
							scriptname = m.group(1)
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

	def _getIncludedTranslators(self) -> dict:
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
		translators = self._getIncludedTranslators()
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

	def sync(self):
		'''
		Synchronize the repository with directories according to the given configuration.
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
		for translatorName in self._getIncludedTranslators():
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

######################################################################
##
class TranslatorRunner(object):
	'''
	Runner of translators.
	'''

	def __init__(self, repository : TranslatorRepository):
		'''
		Construct the runner of translators.
		:param repository: The repository of translators.
		:type repository: TranslatorRepository
		'''
		self._repository = repository
		self.configuration = repository.configuration
		self.__images = None

	def sync(self):
		'''
		Resynchronize the translator data.
		'''
		self._repository.sync()
		self.__images = None

	def addSourceImage(self, filename : str):
		'''
		Add a source image.
		:param filename: The filename of a source image.
		:type filename: str
		'''
		if self.__images is None:
			self.__images = set(filename)
		else:
			self.__images.add(filename)

	def getSourceImages(self) -> list:
		'''
		Replies the list of the images on which the translators could be applied.
		:return: The list of the image filenames.
		:rtype: list
		'''
		if self.__images is None:
			self.__images = set()
			# Add the images that were manually specified
			self.__images.update(self.configuration.translators.imagesToConvert)

			# Detect the image formats
			types = set()
			for translator in self._repository.includedTranslators.values():
				types.update(translator.getInputExtensions())
			types = tuple(types)

			# Detect the image from the file system
			for imageDirectory in self.configuration.translators.imagePaths:
				logging.debug(_T("Detecting images inside '%s'") % (imageDirectory))
				if self.configuration.translators.recursiveImagePath:
					for root, dirs, files in os.walk(imageDirectory):
						for filename in files:
							absPath = os.path.join(root, filename)
							if not genutils.isHiddenFile(absPath) and absPath.endswith(types):
								self.__images.add(absPath)
				else:
					for filename in os.listdir(imageDirectory):
						absPath = os.path.join(imageDirectory, filename)
						if not os.path.isdir(absPath) and not genutils.isHiddenFile(absPath):
							if absPath.endswith(types):
								self.__images.add(absPath)
		return self.__images

	def __compareExtensions(o):
		class K:
			def __init__(self, obj):
				self.obj = obj
			def __cmp(self, other):
				if self.obj is None:
					return 0 if other is None else -1
				if other is None:
					return 1
				c = len(other) - len(self.obj)
				if c != 0:
					return c
				return (self.obj > other) - (self.obj < other)
			def __lt__(self, other):
				return self.__cmp(other.obj) < 0
			def __gt__(self, other):
				return self.__cmp(other.obj) > 0
			def __eq__(self, other):
				return self.__cmp(other.obj) == 0
			def __le__(self, other):
				return self.__cmp(other.obj) <= 0
			def __ge__(self, other):
				return self.__cmp(other.obj) >= 0
			def __ne__(self, other):
				return self.__cmp(other.obj) != 0
		return K(o)

	def getTranslatorFor(self, filename : str) -> Translator:
		'''
		Replies the translator that could be used for the given filename.
		:return: The translator or None
		:rtype: Translator
		'''
		# NOTE : Cannot use os.path.splitex because several extensions have characters before the point, e.g. "+tex.svg"
		if os.name == 'nt':
			f0 = filename.lower()
			for translator in self._repository.includedTranslators.values():
				for extension in translator.getInputExtensions():
					if f0.endswith(extension.lower()):
						return translator
		else:
			for translator in self._repository.includedTranslators.values():
				for extension in translator.getInputExtensions():
					if filename.endswith(extension):
						return translator
		return None


	def generateImage(self, *, infile : str, translatorName : str = None, outfile : str = None, onlymorerecent : bool = True, failOnError : bool = True) -> bool:
		'''
		Generate the image from the given source file by running the appropriate translator.
		:param infile: The name of the source file.
		:type infile: str
		:param translatorName: Name of the translator to run. Default value: None.
		:type translatorName: str
		:param outfile: The name of the output file. Default value: None
		:type outfile: str
		:param onlymorerecent: Indicates if the translation is always run (False) or only if the source file is more recent than the target file. Default value: True
		:type onlymorerecent: bool
		:param failOnError: Indicates if the translator generates a Python exception on error during the run. Default value: True.
		:type failOnError: bool
		:return: The output filename on success; otherwise None on error or if the file is up-to-date
		:rtype: str
		'''
		if not infile:
			return None

		translator = None
		if translatorName:
			translator = self._repository._getObjectFor(translatorName)
		if translator is None:
			translator = self.getTranslatorFor(infile)
		if translator is None:
			raise TranslatorError(_T("Unable to find a translator for the source image %s") % (infile))

		if not os.access(infile, os.R_OK):
			errmsg = _T("%s: file not found or not readable.") % (infile)
			if failOnError:
				raise TranslatorError(errmsg)
			else:
				logging.error(errmsg)
				return None

		inexts = translator.getInputExtensions()
		inext = None
		for e in inexts:
			if infile.endswith(e):
				inext = e
				break
		if not inext:
			inext = translator.getInputExtensions()[0]
		outexts = translator.getOutputExtensions()
		if len(outexts) > 0 and outexts[0]:
			outext = outexts[0]
		else:
			outext = ''

		if not outfile:
			outfile = genutils.basename2(infile, inexts) + outext

		# Try to avoid the translation if the source file is no more recent than the target file.
		if onlymorerecent:
			inchange = genutils.getFileLastChange(infile)
			outchange = genutils.getFileLastChange(outfile)
			if outchange is None:
				# No out file, try to detect other types of generated files
				dirname = os.path.dirname(outfile)
				for filename in os.listdir(dirname):
					absPath = os.path.join(dirname, filename)
					if not os.path.isdir(absPath) and not genutils.isHiddenFile(absPath):
						bn = genutils.basename(filename, outexts)
						m = re.match('^('+re.escape(bn+'_')+'.*)'+re.escape(outext)+'$', filename, re.S)
						if m:
							t = genutils.getFileLastChange(absPath)
							if t is not None and (outchange is None or t < outchange):
								outchange = t
								break
			if outchange is not None and inchange <= outchange:
				# No need to translate again
				logging.fine_info(_T("%s is up-to-date") % (os.path.basename(outfile)))
				return None

		logging.info(_T("%s -> %s") % (os.path.basename(infile), os.path.basename(outfile)))
		logging.trace(_T("In: %s") % (infile))
		logging.trace(_T("Out: %s") % (outfile))

		commandLine = translator.getCommandLine()
		embeddedFunction = translator.getEmbeddedFunction()
		if commandLine:
			################################
			# Run an external command line #
			################################
			# Create the environment of variables for the CLI
			environment = translator.getConstants()
			environment['in'] = infile
			environment['inexts'] = inexts
			environment['inext'] = inext
			environment['out'] = outfile
			environment['outexts'] = outexts
			environment['outext'] = outext
			environment['ext'] = outext
			environment['outbasename'] = genutils.basename(outfile, outexts)
			environment['outwoext'] = os.path.join(os.path.dirname(outfile), environment['outbasename'])
			# Create the CLI to run
			cli = genutils.parseCLI(commandLine, environment)
			
			# Run the cli
			if logging.getLogger().isEnabledFor(logging.TRACE):
				shCmd = list()
				for e in cli:
					shCmd.append(shlex.quote(e))
				logging.trace(_T("Run: %s") % (' '.join(shCmd)))
			out = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(sout, serr) = out.communicate()
			if out.returncode != 0:
				errmsg = _T("%s\nReturn code: %d") % ((serr or ''), out.returncode)
				if failOnError:
					raise TranslatorError(errmsg)
				else:
					logging.error(errmsg)
					return None
			return outfile
		elif embeddedFunction:
			#########################
			# Run the embedded code #
			#########################
			interpreter = translator.getEmbeddedFunctionInterpreter()
			if not interpreter:
				interpreter = translator.configuration.pythonInterpreter
			else:
				interpreter = interpreter.lower()

			outbasename = genutils.basename(outfile, outexts)
			outwoext = os.path.join(os.path.dirname(outfile), outbasename)

			environment = translator.getConstants()
			if interpreter == translator.configuration.pythonInterpreter:
				environment['runner'] = self
			environment['in'] = infile
			environment['inexts'] = inexts
			environment['inext'] = inext
			environment['out'] = outfile
			environment['outexts'] = outexts
			environment['outext'] = outext
			environment['ext'] = outext
			environment['outbasename'] = outbasename
			environment['outwoext'] = outwoext
			environment['python_script_dependencies'] = translator.getPythonDependencies()
			environment['global_configuration'] = translator.configuration

			execEnv = {
				'interpreterObject': None, 
				'global_configuration': translator.configuration,
			}

			if translator.configuration is None:
				raise Exception('No configuration specification')
			
			package_name = "autolatex2.translator." + interpreter + "interpreter"
			if importlib.util.find_spec(package_name) is None:
				m = re.match('^(.*?)[0-9]+$',  interpreter)
				if m:
					package_name = "autolatex2.translator." + m.group(1) + "interpreter"
			exec("from " + package_name + " import TranslatorInterpreter\n"
					"interpreterObject = TranslatorInterpreter(global_configuration)",  None, execEnv)

			if not execEnv['interpreterObject'].runnable:
				errmsg = _T("Cannot execute the translator '%s'.") % (translatorName)
				if failOnError:
					raise TranslatorError(errmsg)
				else:
					logging.error(errmsg)
					return False
			
			execEnv['interpreterObject'].globalVariables.update(environment)
			(sout, serr, exception, retcode) = execEnv['interpreterObject'].run(embeddedFunction)
			if exception is not None or retcode != 0:
				errmsg = _T("%s\nReturn code: %s") % ((serr or ''), retcode)
				if failOnError:
					raise(TranslatorError(errmsg))
				else:
					logging.error(errmsg)
					return None

			return outfile
		else:
			errmsg = _T("Unable to find the method of translation for '%s'.") % (translatorName)
			if failOnError:
				raise TranslatorError(errmsg)
			else:
				logging.error(errmsg)
				return None
