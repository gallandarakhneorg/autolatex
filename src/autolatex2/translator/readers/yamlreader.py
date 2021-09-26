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
Readers of "transdef" files.
'''

import re
import logging
import yaml

from autolatex2.config.configobj import Config
from autolatex2.translator.readers.abstractreader import AbstractTransdefReader
from autolatex2.translator.readers.transdefline import TransdefLine
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext



class YamlTransdefReader(AbstractTransdefReader):
	'''
	Reader for the version 2 (Yaml-based) transdef format (for the Python version of AutoLaTeX).
	'''

	def __init__(self, configuration : Config):
		'''
		Contructor.
		:param configuration: the global configuration.
		:type configuration: Config
		'''
		super().__init__(configuration)

	def readTranslatorFile(self, filename : str) -> dict:
		'''
		Read the translator file. The replied value is the set of keys read from the transdef file.
		:param filename: the name of the file to read.
		:type filename: str
		:rtype: dict
		'''
		# Read the YAML content
		with open(filename, 'r') as stream:
			yaml_content = yaml.safe_load(stream)
		# Analyze the content
		content = dict()
		for (key,  value) in yaml_content.items():
			m = re.match('^\\s*([azA-Z0-9_]+)(?:\\s+with\\s+(.*?))?(?:\\s+for\\s+((?:pdf)|(?:eps)))?\\s*$', key, re.I | re.S)
			if m:
				curvar = m.group(1)
				interpreter = m.group(2)
				mode = m.group(3) 
				if (not mode) or (self.configuration.generation.pdfMode and mode.lower() == 'pdf') or (not self.configuration.generation.pdfMode and mode.lower() == 'eps'):
					curvar = curvar.upper()
					if isinstance(value,  list):
						content[curvar] = TransdefLine(curvar,  int(0),  None,  (interpreter.lower() if interpreter else None))
						content[curvar].value_list = value
					else:
						content[curvar] = TransdefLine(curvar,  0,  value,  (interpreter.lower() if interpreter else None))
		
		# Translate the values into suitable Python objects
		if 'TRANSLATOR_PERL_DEPENDENCIES' in content and content['TRANSLATOR_PERL_DEPENDENCIES'] and content['TRANSLATOR_PERL_DEPENDENCIES'].value:
			logging.warning(_T("The key 'TRANSLATOR_PERL_DEPENDENCIES' is no more supported in the translator files. Please use 'TRANSLATOR_PYTHON_DEPENDENCIES'"))

		# Ensure that the command line is a list
		if 'COMMAND_LINE' in content and content['COMMAND_LINE'] and content['COMMAND_LINE'].value:
			cli = genutils.parseCLI(commandLine = str(content['COMMAND_LINE'].value), all_protect = True)
			content['COMMAND_LINE'].value = None
			content['COMMAND_LINE'].value_list = cli

		if 'INPUT_EXTENSIONS' in content and content['INPUT_EXTENSIONS'] and content['INPUT_EXTENSIONS'].value_list:
			for i in range(len(content['INPUT_EXTENSIONS'].value_list)):
				e = content['INPUT_EXTENSIONS'].value_list[i]
				if e:
					e = self._normalize_extension(e)
					content['INPUT_EXTENSIONS'].value_list[i] = e
			if content['INPUT_EXTENSIONS'] and content['INPUT_EXTENSIONS'].value_list and len(content['INPUT_EXTENSIONS'].value_list) > 0:
				try:
					content['INPUT_EXTENSIONS'].value = ' '.join(content['INPUT_EXTENSIONS'].value_list)
				except:
					content['INPUT_EXTENSIONS'].value = ''
			else:
				content['INPUT_EXTENSIONS'].value = ''
		
		if 'OUTPUT_EXTENSIONS' in content and content['OUTPUT_EXTENSIONS'] and content['OUTPUT_EXTENSIONS'].value_list:
			for i in range(len(content['OUTPUT_EXTENSIONS'].value_list)):
				e = content['OUTPUT_EXTENSIONS'].value_list[i]
				if e:
					e = self._normalize_extension(e)
					content['OUTPUT_EXTENSIONS'].value_list[i] = e
			if content['OUTPUT_EXTENSIONS'] and content['OUTPUT_EXTENSIONS'].value_list and len(content['OUTPUT_EXTENSIONS'].value_list) > 0:
				try:
					content['OUTPUT_EXTENSIONS'].value = ' '.join(content['OUTPUT_EXTENSIONS'].value_list)
				except:
					content['OUTPUT_EXTENSIONS'].value = ''
			else:
				content['OUTPUT_EXTENSIONS'].value = ''

		return content

	def _normalize_extension(self,  extension : str) -> str:
		if not extension:
			return extension
		if extension.startswith('.'):
			return extension
		if re.match('[+._]', extension):
			return extension
		return '.' + extension
