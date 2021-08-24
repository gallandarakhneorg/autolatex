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
Reader of AutoLaTeX Configuration.
'''

import logging
import configparser
import os
import re

import autolatex2.utils.utilfunctions as genutils
from autolatex2.config.configobj import Config
from autolatex2.config.translator import TranslatorLevel
from autolatex2.utils.extlogging import ensureAutoLaTeXLoggingLevels

import gettext
_T = gettext.gettext

class OldStyleConfigReader(object):
	'''
	Reader of AutoLaTeX Configuration that is written with the old-style format (ini file).
	'''
	
	def __init__(self):
		self._base_dir = os.getcwd()
		ensureAutoLaTeXLoggingLevels()

	def _read_viewer(self,  content : object,  config : Config):
		'''
		Read the configuration section [viewer].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		config.view.view = OldStyleConfigReader.to_bool(self._ensureAscendentCompatibility(content.get('view')),  config.view.view)
		config.view.viewerCLI = self._ensureAscendentCompatibility(content.get('viewer')) or config.view.viewerCLI

	def _read_scm(self,  content : object,  config : Config):
		'''
		Read the configuration section [scm].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		config.scm.commitCLI = self._ensureAscendentCompatibility(content.get('scm commit')) or config.scm.commitCLI
		config.scm.updateCLI = self._ensureAscendentCompatibility(content.get('scm update')) or config.scm.commitCLI

	def _read_clean(self,  content : object,  config : Config):
		'''
		Read the configuration section [clean].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		for p in OldStyleConfigReader.to_path_list(self._ensureAscendentCompatibility(content.get('files to clean'))):
			config.clean.addCleanFile(p)
		for p in OldStyleConfigReader.to_path_list(self._ensureAscendentCompatibility(content.get('files to desintegrate'))):
			config.clean.addCleanAllFile(p)

	def _read_generation_prefix(self,  content : object,  filename : str, config : Config):
		'''
		Read the path definition in the configuration section [generation].
		:param content: the configuration file content.
		:type content: dict
		:param filename: the name of the configuration file.
		:type filename: str
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		main_name = self._ensureAscendentCompatibility(content.get('main file'))
		if main_name:
			main_name = genutils.abspath(main_name,  self._base_dir)
			config.documentDirectory = os.path.dirname(main_name)
			config.documentFilename = os.path.basename(main_name)

	def _read_generation(self,  content : object,  config : Config):
		'''
		Read the configuration section [generation], except the ones "_read_generation_prefix".
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		for p in OldStyleConfigReader.to_path_list(self._ensureAscendentCompatibility(content.get('image directory'))):
			config.translators.addImagePath(self.to_path(p))

		config.translators.is_translator_enable = OldStyleConfigReader.to_bool(self._ensureAscendentCompatibility(content.get('generate images')),  config.translators.is_translator_enable)
		
		generation_type = OldStyleConfigReader.to_kw(self._ensureAscendentCompatibility(content.get('generation type')),  'pdf' if config.generation.pdfMode else 'ps')
		if generation_type == 'dvi' or generation_type == 'ps':
			config.generation.pdfMode = False
		else:
			config.generation.pdfMode = True

		tex_compiler = OldStyleConfigReader.to_kw(self._ensureAscendentCompatibility(content.get('tex compiler')),  config.generation.latexCompiler)
		if tex_compiler != 'latex' and tex_compiler != 'xelatex' and tex_compiler != 'lualatex':
			tex_compiler = 'pdflatex'
		config.generation.latexCompiler = tex_compiler

		config.generation.synctex = OldStyleConfigReader.to_bool(self._ensureAscendentCompatibility(content.get('synctex')),  config.generation.synctex)

		for p in OldStyleConfigReader.to_path_list(self._ensureAscendentCompatibility(content.get('translator include path'))):
			config.translators.addIncludePath(self.to_path(p))
	
		cmd = self._ensureAscendentCompatibility(content.get('latex_cmd'))
		if cmd:
			config.generation.latexCLI = cmd

		cmd = self._ensureAscendentCompatibility(content.get('bibtex_cmd'))
		if cmd:
			config.generation.bibtexCLI = cmd
	
		cmd = self._ensureAscendentCompatibility(content.get('biber_cmd'))
		if cmd:
			config.generation.biberCLI = cmd
	
		cmd = self._ensureAscendentCompatibility(content.get('makeglossaries_cmd'))
		if cmd:
			config.generation.makeglossaryCLI = cmd

		cmd = self._ensureAscendentCompatibility(content.get('makeindex_cmd'))
		if cmd:
			config.generation.makeindexCLI = cmd

		cmd = self._ensureAscendentCompatibility(content.get('dvi2ps_cmd'))
		if cmd:
			config.generation.dvipsCLI = cmd

		flags = self._ensureAscendentCompatibility(content.get('latex_flags'))
		if flags:
			config.generation.latexFlags = flags

		flags = self._ensureAscendentCompatibility(content.get('bibtex_flags'))
		if flags:
			config.generation.bibtexFlags = flags

		flags = self._ensureAscendentCompatibility(content.get('biber_flags'))
		if flags:
			config.generation.biberFlags = flags

		flags = self._ensureAscendentCompatibility(content.get('makeglossaries_flags'))
		if flags:
			config.generation.makeglossaryFlags = flags

		flags = self._ensureAscendentCompatibility(content.get('makeindex_flags'))
		if flags:
			config.generation.makeindexFlags = flags

		flags = self._ensureAscendentCompatibility(content.get('dvi2ps_flags'))
		if flags:
			config.generation.dvipsFlags = flags

		make_index_style = self.to_list(self._ensureAscendentCompatibility(content.get('makeindex style')))
		config.generation.makeindexStyleFilename = None
		if not make_index_style:
			make_index_style = ['@detect@system']
		for key in make_index_style:
			kw = OldStyleConfigReader.to_kw(key,  '@detect@system')
			result = None
			if kw == '@detect':
				result = self.to_path(self.__detect_ist_file(config))
			elif kw == '@system':
				result = self.to_path(config.get_system_ist_file())
			elif kw == '@none':
				config.generation.makeindexStyleFilename = None
				break
			elif kw == '@detect@system':
				ist_file = self.__detect_ist_file(config)
				if ist_file:
					result = self.to_path(ist_file)
				else:
					result = self.to_path(config.get_system_ist_file())
			else:
				result = self.to_path(make_index_style)
			if result:
				config.generation.makeindexStyleFilename = result
				break

	def _read_translator(self,  translator_name : str,  translator_level : TranslatorLevel,  content : object,  config : Config):
		'''
		Read the configuration section [<translator>].
		:param translator_name: The name of the translator.
		:type translator_name: str
		:param translator_level: The level for the translator.
		:type translator_level: int
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		config.translators.setIncluded(translator_name,  translator_level,  OldStyleConfigReader.to_bool(self._ensureAscendentCompatibility(content.get('include module')),  config.translators.included(translator_name,  translator_level)))
		for p in OldStyleConfigReader.to_path_list(self._ensureAscendentCompatibility(content.get('files to convert'))):
			config.translators.addImageToConvert(self.to_path(p))

	def read(self, filename : str,  translator_level : TranslatorLevel,  config : Config = None) -> Config:
		'''
		Read the configuration file.
		:param filename: the name of the file to read.
		:type filename: str
		:param translator_level: the level at which the configuration is located. See TranslatorLevel enumeration.
		:type translator_level: TranslatorLevel
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		'''
		if config is None:
			config = Config()

		filename = os.path.abspath(filename)
		self._base_dir = os.path.dirname(filename)

		try:
			config_file = configparser.SafeConfigParser()
			config_file.read(filename)
			
			for section in config_file.sections():
				nsection = section.lower()
				if nsection == 'generation':
					content = dict(config_file.items(section))
					self._read_generation_prefix(content,  filename,  config)

			for section in config_file.sections():
				nsection = section.lower()
				content = dict(config_file.items(section))
				if nsection == 'generation':
					self._read_generation(content,  config)
				elif nsection == 'viewer':
					self._read_viewer(content,  config)
				elif nsection == 'clean':
					self._read_clean(content,  config)
				elif nsection == 'scm':
					self._read_scm(content,  config)
				else:
					self._read_translator(section,  translator_level,  content,  config)
		finally:
			self._base_dir = os.getcwd()
		return config

	def __detect_ist_file(self,  config : Config) -> str:
		'''
		Detect an IST file into the current document.
		:param config: the configuration.
		:type config: Config
		:return: the IST filename or None
		:rtype: str
		'''
		ddir = config.documentDirectory
		if not ddir:
			ddir = os.getcwd()
		if os.path.isdir(ddir):
			onlyfiles = [f for f in os.listdir(ddir) if os.path.isfile(os.path.join(ddir, f))]
			ist_files = list()
			for file in onlyfiles:
				if re.match('.ist$',  file,  re.I):
					ist_files.append(file)
			if len(ist_files) > 0:
				filename = ist_files[0]
				if len(ist_files) > 1:
					logging.warn(_T('Multiple IST files were found into the document directory. Use: %s') % (filename))
				return filename
		return None

	def _ensureAscendentCompatibility(self,  value : str) -> str:
		if value:
			m = re.match('^(.*?)\\s*\\#.*$',  value)
			if m:
				return m.group(1)
		return value

	def to_path(self,  value : str) -> str:
		if value:
			return genutils.abspath(value,  self._base_dir)
		return value

	@staticmethod
	def to_bool(value : str,  default : bool) -> bool:
		'''
		Convert a string to a bool. This function takes care of strings as "True", "False", "Yes", "No", "t", "f", "y", "n", "1", "0".
		:param value: the value to convert.
		:type value: str
		:param default: the default value.
		:type: bool
		:return: the boolean value.
		:rtype: bool
		'''
		if value:
			v = value.lower()
			return v == 'true' or v == 'yes' or v == 't' or v =='y' or v =='1'
		return default

	@staticmethod
	def to_path_list(value : str) -> list:
		'''
		Convert a string to list of paths. According to the operating system, the path separator may be ':' or ';'
		:param value: the value to convert.
		:type value: str
		:return: the list value.
		:rtype: list
		'''
		if value:
			sep = os.pathsep
			paths = value.split(sep)
			return paths
		return list()

	@staticmethod
	def to_list(value : str) -> list:
		'''
		Convert a string to list of strings. The considered separators are: ',' and ';'
		:param value: the value to convert.
		:type value: str
		:return: the list value.
		:rtype: list
		'''
		if value:
			return re.split('\s*[,;]\s*',  value)
		return value

	@staticmethod
	def to_kw(value : str,  default : str) -> str:
		'''
		Convert a string to string-based keyword.
		:param value: the value to convert.
		:type value: str
		:param default: the default value.
		:type: str
		:return: the keyword.
		:rtype: str
		'''
		if value:
			return value.lower()
		return default

	def readSystemConfigSafely(self, config : Config = None) -> Config:
		'''
		Read the configuration file at the system level without failing if the file does not exist.
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		'''
		if config is None:
			config = Config()
		filename = config.systemConfigFile
		if filename and os.path.isfile(filename) and os.access(filename, os.R_OK):
			try:
				self.read(filename,  TranslatorLevel.SYSTEM,  config)
			except:
				pass
		return config

	def readUserConfigSafely(self, config : Config = None) -> Config:
		'''
		Read the configuration file at the user level without failing if the file does not exist.
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		'''
		if config is None:
			config = Config()
		filename = config.userConfigFile
		if filename and os.path.isfile(filename) and os.access(filename, os.R_OK):
			try:
				self.read(filename,  TranslatorLevel.USER,  config)
			except:
				pass
		return config

	def readDocumentConfigSafely(self, filename : str,  config : Config = None) -> Config:
		'''
		Read the configuration file at the document level without failing if the file does not exist.
		:param filename: the name of the file to read.
		:type filename: str
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		'''
		if config is None:
			config = Config()
		if filename and os.path.isfile(filename) and os.access(filename, os.R_OK):
			try:
				self.read(filename,  TranslatorLevel.DOCUMENT,  config)
			except:
				pass
		return config
