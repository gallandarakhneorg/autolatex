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
Configuration of a AutoLaTeX instance.
'''

import os
import re
import autolatex2.tex.utils as texutils

import gettext
_T = gettext.gettext

from autolatex2.config.generation import GenerationConfig
from autolatex2.config.translator import TranslatorConfig

class Config(object):
	'''
	Configuration of a AutoLaTeX instance.
	'''

	def __init__(self):
		self.__pythonInterpreter = 'python3'
		self.__osName = None
		self.__homeDirectory = None
		self.__userDirectory = None
		self.__userFile = None
		self.__documentDirectory = None
		self.__installationDirectory = None
		self.__autolatexScriptName = None
		self.__autolatexLaunchName = None
		self.__autolatexVersion = None

		self.__generation = GenerationConfig()
		self.__translation = TranslatorConfig()

	@property
	def pythonInterpreter(self):
		'''
		Replies the name of the python interpreter.
		:rtype: str
		'''
		return self.__pythonInterpreter

	@pythonInterpreter.setter
	def pythonInterpreter(self, name : str):
		'''
		Change the name of the python interpreter.
		:param name: The name of the interpreter.
		:type name: str
		'''
		self.__pythonInterpreter = name
	
	@property
	def osname(self):
		'''
		Replies the name of the OS.
		This name is used by this configuration for building  the property values.
		:rtype: str
		'''
		if self.__osName is None:
			return os.name
		else:
			return self.__osName

	@osname.setter
	def osname(self, name : str):
		'''
		Set the name of the OS.
		This name is used by this configuration for building  the property values.
		:param name: The name of the OS. If None, the value of <code>os.name</code>
		             will be used.
		:type name: str
		'''
		self.__osName = name
	
	@property
	def homedir(self):
		'''
		Replies the home directory of the user.
		:rtype: str
		'''
		if self.__homeDirectory is None:
			return os.path.expanduser('~')
		else:
			return self.__homeDirectory

	@homedir.setter
	def homedir(self, name : str):
		'''
		Set the home directory.
		:param name: The home directory, or None.
		:type name: str
		'''
		self.__homeDirectory = name

	def makeDocumentConfigFilename(self, directory : str) -> str:
		'''
		Replies the filename of the AutoLateX 'project' configuration when
		it is located in the given directory.
		:param directory: The name of the directory in which the main document file is located.
		:type directory: str
		:return: The name of the file in which the document-level configuration is stored.
		:rtype: str
		'''
		if self.osname == 'posix':
			return os.path.join(directory, ".autolatex_project.cfg")
		else:
			return os.path.join(directory, "autolatex_project.cfg")

	@property
	def userConfigDirectory(self) -> str:
		'''
		Replies the name of folder where the AutoLateX 'user' configuration is.
		:return: The name of the user-level configuration folder.
		:rtype: str
		'''
		if self.__userDirectory is None:
			if self.osname == 'posix':
				self.__userDirectory = os.path.join(self.homedir, ".autolatex")
			elif self.osname == 'nt':
				self.__userDirectory = os.path.join(self.homedir, "Local Settings", "Application Data", "autolatex")
			else:
				self.__userDirectory = os.path.join(self.homedir, "autolatex")
		return self.__userDirectory

	def _isdir(self, directory : str) -> bool:
		'''
		Replies if the given directory exists in the operating system.
		:param directory: Name of the directory to test.
		:type directory: str
		:return: True if the directory exists; False otherwise.
		:rtype: bool
		'''
		return os.path.isdir(directory)

	@property
	def userConfigFile(self) -> str:
		'''
		Replies the name of file where the AutoLateX 'user' configuration is.
		:return: The name of the file in which the user-level configuration is stored.
		:rtype: str
		'''
		if self.__userFile is None:
			directory = self.userConfigDirectory
			if self._isdir(directory):
				self.__userFile = os.path.join(directory, 'autolatex.conf')
			elif self.osname == 'posix':
				self.__userFile = os.path.join(self.homedir, ".autolatex")
			elif self.osname == 'nt':
				self.__userFile = os.path.join(self.homedir, "Local Settings", "Application Data", "autolatex.conf")
			else:
				self.__userFile = os.path.join(self.homedir, "autolatex.conf")
		return self.__userFile

	@property
	def documentDirectory(self) -> str:
		'''
		Replies the directory of the document.
		:return: the name of the directory in which the current TeX document is located.
		:rtype: str
		'''
		return self.__documentDirectory

	@documentDirectory.setter
	def documentDirectory(self, currentDocument : str) -> str:
		'''
		Change the document directory.
		If the given path does not contain a document, try to find the directory where
		an AutoLaTeX configuration file is
		located. The search is traversing the parent directory from the current
		document.
		:param currentDocument: The path to the current LaTeX document.
		:type currentDocument: str
		:return: The path to the folder where the AutoLaTeX configuration was found.
		         It is 'current_document' or a parent directory of 'current_document'.
		:rtype: str
		'''
		adir = None
		if self._isdir(currentDocument):
			directory = currentDocument
		else:
			directory = os.path.dirname(currentDocument)
		directory = os.path.abspath(directory)
		document_dir = directory
		cfgFile = self.makeDocumentConfigFilename(directory)
		previousFile = ''
		while previousFile != cfgFile and not os.path.exists(cfgFile):
			directory = os.path.dirname(directory)
			previousFile = cfgFile
			cfgFile = self.makeDocumentConfigFilename(directory)
		
		if previousFile != cfgFile:
			adir = os.path.dirname(cfgFile)
		else:
			ext = os.path.splitext(currentDocument)[-1]
			if texutils.isTeXFileExtension(ext):
				adir = document_dir
		
		if adir is None:
			self.__documentDirectory = directory
		else:
			self.__documentDirectory = adir

		return adir

	def setRawDocumentDirectory(self, folder : str):
		'''
		Change the document directory.
		:param folder: The path to the folder in which the current LaTeX document is located.
		:type folder: str
		'''
		self.__documentDirectory = folder

	@property
	def installationDirectory(self) -> str:
		'''
		Replies the directory in which the AutoLaTeX is installed.
		:return: The installation directory of AutoLaTeX.
		:rtype: str
		'''
		if self.__installationDirectory is None:
			root = os.path.abspath(os.sep)
			path = os.path.dirname(__file__)
			while (path and path != root and os.path.isdir(path)):
				filename = os.path.join(path, 'VERSION')
				if os.path.isfile(filename):
					try:
						with open (filename, "r") as myfile:
							content = myfile.read().strip()
						if content.startswith('autolatex'):
							self.__installationDirectory = path
							return self.__installationDirectory
					except:
						pass			
				path = os.path.dirname(path)
		return self.__installationDirectory

	@property
	def name(self) -> str:
		'''
		Replies the base filename of the main AutoLaTeX script.
		:return: The AutoLaTeX main script filename.
		:rtype: str
		'''
		return self.__autolatexScriptName

	@name.setter
	def name(self, name : str) -> str:
		'''
		Change the base filename of the main AutoLaTeX script.
		:param name: The AutoLaTeX main script filename.
		:type: str
		'''
		self.__autolatexScriptName = name
		if self.__autolatexLaunchName is None:
			self.__autolatexLaunchName = name

	@property
	def launchName(self) -> str:
		'''
		Replies the base filename of the command which permits
		to launch AutoLaTeX. It could differ from the AutoLaTeX name
		due to several links.
		This value must be set with a call to setAutoLaTeXInfo().
		:return: The launchable AutoLaTeX script filename.
		:rtype: str
		'''
		return self.__autolatexLaunchName

	@launchName.setter
	def launchName(self, name : str) -> str:
		'''
		Change the base filename of the command which permits
		to launch AutoLaTeX. It could differ from the AutoLaTeX name
		due to several links.
		This value must be set with a call to setAutoLaTeXInfo().
		:param name: The launchable AutoLaTeX script filename.
		:type: str
		'''
		self.__autolatexLaunchName = name
		if self.__autolatexScriptName is None:
			self.__autolatexScriptName = name

	@property
	def version(self) -> str:
		'''
		Replies the current version of AutoLaTeX.
		This number is extracted from the VERSION filename if
		it exists.
		This value must be set with a call to setAutoLaTeXInfo().
		:return: The AutoLaTeX version number.
		:rtype: str
		'''
		if (self.__autolatexVersion is None):
			directory =  self.installationDirectory
			if directory is not None:
				with open (os.path.join(directory, 'VERSION'), "r") as myfile:
					line = myfile.read().strip()
				m = re.match(r'^autolatex\s+([0-9]+\.[0-9]+(\-[^\s]+)?)', line)
				if m:
					self.__autolatexVersion = m.group(1)
					if not self.__autolatexVersion:
						raise [_T("invalid line in the VERSION file: %s") % (line)]
			else:
				raise IOError[_T("installation directory cannot be detected")]
		return self.__autolatexVersion

	@property
	def generation(self) -> GenerationConfig:
		'''
		Replies the configuration dedicated to the generation process.
		:return: the generation configuration.
		:rtype: GenerationConfig
		'''
		return self.__generation

	@generation.setter
	def generation(self, config : GenerationConfig):
		'''
		Set the configuration dedicated to the generation process.
		:param config: the generation configuration.
		:type config: GenerationConfig
		'''
		self.__generation = config

	@property
	def translators(self) -> GenerationConfig:
		'''
		Replies the configuration dedicated to the translators.
		:return: the translator configuration.
		:rtype: TranslatorConfig
		'''
		return self.__translation

	@translators.setter
	def translators(self, config : GenerationConfig):
		'''
		Set the configuration dedicated to the translators.
		:param config: the translator configuration.
		:type config: TranslatorConfig
		'''
		self.__translation = config

