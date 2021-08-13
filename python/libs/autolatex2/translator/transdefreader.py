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
Readers of "transdef" files.
'''

import re
import abc
import logging
import yaml

from dataclasses import dataclass

from autolatex2.config.configobj import Config

import gettext
_T = gettext.gettext

######################################################################
##
@dataclass
class TransdefLine(object):
	name : str
	lineno : int
	interpreter : str
	value : str
	value_list : list
	
	def __init__(self,  name : str,  lineno : int,  value : str,  interpreter : str):
		'''
		Constructor.
		:param name: The name of transdef entry.
		:type name: str
		:param lineno: The line number into the transdef file.
		:type lineno: int
		:param value: The value extracted from the transdef file.
		:type value: str
		:param interpreter: The interpreter to use for the value (if the value is code).
		:type interpreter: str
		'''
		self.name = name
		self.lineno = lineno
		self.value = value
		self.value_list = list([value])
		self.interpreter = interpreter



######################################################################
##
class AbstractTransdefReader(object):
	'''
	Abstract implementation of a "transdef" reader.
	'''

	def __init__(self, configuration : Config):
		'''
		Contructor.
		:param configuration: the global configuration.
		:type configuration: Config
		'''
		self.__configuration = configuration

	@property
	def configuration(self):
		'''
		Replies the configuration.
		:return: the configuration.
		:rtype: Config
		'''
		return self.__configuration

	@configuration.setter
	def configuration(self,  c : Config):
		'''
		Change the configuration.
		:param c: the configuration.
		:type c: Config
		'''
		self.__configuration = c

	@abc.abstractmethod
	def readTranslatorFile(self, filename : str) -> dict:
		'''
		Read the translator file. The replied value is the set of keys read from the transdef file. Each value is a TransdefLine.
		:param filename: the name of the file to read.
		:type filename: str
		:rtype: dict
		'''
		pass


######################################################################
##
class PerlTransdefReader(AbstractTransdefReader):
	'''
	Reader for the version 1 (original) transdef format (for the Perl version of AutoLaTeX).
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
		content = dict()
		with open(filename) as f:
			lineno = 0
			eol = False
			curvar = None
			for line in f.readlines():
				lineno = lineno + 1
				if eol:
					if line.startswith(eol):
						eol = None
						curvar = None
					elif curvar:
						# Append to current entry
						content[curvar].value += line
				elif not re.match(r'^\s*[#;]', line):
					m = re.match(r'^\s*([azA-Z0-9_]+)(?:\s+with\s+(.*?))?(?:\s+for\s+((?:pdf)|(?:eps)))?\s*=\<\<([a-zA-Z0-9_]+)\s*(.*?)\s*$', line, re.I)
					if m:
						curvar = m.group(1)
						interpreter = m.group(2)
						mode = m.group(3)
						eol = m.group(4)
						value = m.group(5)
						if (not mode) or (self.configuration.generator.pdfMode and mode.lower() == 'pdf') or (not self.configuration.generator.pdfMode and mode.lower() == 'eps'):
							curvar = curvar.upper()
							content[curvar] = TransdefLine(curvar,  lineno,  value,  (interpreter.lower() if interpreter else None))
						else:
							curvar = None
					else:
						m = re.match(r'^\s*([azA-Z0-9_]+)(?:\s+with\s+(.*?))?(?:\s+for\s+((?:pdf)|(?:eps)))?\s*=\s*(.*?)\s*$', line, re.I)
						if m:
							var = m.group(1)
							interpreter = m.group(2)
							mode = m.group(3)
							value = m.group(4)
							if (not mode) or (self.configuration.generation.pdfMode and mode.lower() == 'pdf') or (not self.configuration.generation.pdfMode and mode.lower() == 'eps'):
								curvar = None
								eol = None
								content[var.upper()] = TransdefLine(var.upper(),  lineno,  value,  (interpreter.lower() if interpreter else None))
						elif not re.match(r'^\s*$', line):
							logging.error(_T("Line outside a definition (%s:%d).") % (filename, lineno))

		if eol:
			logging.error(_T("The block for the variable '%s' is not closed. Keyword '%s' was not found (%s:%s).")
				% (curvar, eol, filename, lineno))

		# Translate the values into suitable Python objects
		if 'INPUT_EXTENSIONS' in content and content['INPUT_EXTENSIONS'] and content['INPUT_EXTENSIONS'].value:
			exts = re.split(r'\s+', content['INPUT_EXTENSIONS'].value or '')
			content['INPUT_EXTENSIONS'].value_list = list()
			for e in exts:
				if not re.match(r'^\s*$', e):
					if not re.match(r'^[\.+]', e):
						e = "." + e
					content['INPUT_EXTENSIONS'].value_list.append(e)

		if 'OUTPUT_EXTENSIONS' in content and content['OUTPUT_EXTENSIONS'] and content['OUTPUT_EXTENSIONS'].value:
			exts = re.split(r'\s+', content['OUTPUT_EXTENSIONS'].value or '')
			content['OUTPUT_EXTENSIONS'].value_list = list()
			for e in exts:
				if not re.match(r'^\s*$', e):
					if not re.match(r'^\.', e):
						e = "." + e
					content['OUTPUT_EXTENSIONS'].value_list.append(e)

		if 'TRANSLATOR_PERL_DEPENDENCIES' in content and content['TRANSLATOR_PERL_DEPENDENCIES'] and content['TRANSLATOR_PERL_DEPENDENCIES'].value:
			logging.warning(_T("The key 'TRANSLATOR_PERL_DEPENDENCIES' is no more supported in the translator files. Please use 'TRANSLATOR_PYTHON_DEPENDENCIES'"))

		if 'TRANSLATOR_PYTHON_DEPENDENCIES' in content and content['TRANSLATOR_PYTHON_DEPENDENCIES'] and content['TRANSLATOR_PYTHON_DEPENDENCIES'].value:
			content['TRANSLATOR_PYTHON_DEPENDENCIES'].value_list = re.split(r'\s+', content['TRANSLATOR_PYTHON_DEPENDENCIES']['value'] or '')

		if 'FILES_TO_CLEAN' in content and content['FILES_TO_CLEAN'] and content['FILES_TO_CLEAN'].value:
			patterns = re.split(r'\s+', content['FILES_TO_CLEAN'].value or '')
			content['FILES_TO_CLEAN'].value_list = list()
			for p in patterns:
				if not re.match(r'^\s*$', p):
					content['FILES_TO_CLEAN'].value_list.append(p)

		return content

######################################################################
##
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
				if (not mode) or (self.configuration.generator.pdfMode and mode.lower() == 'pdf') or (not self.configuration.generator.pdfMode and mode.lower() == 'eps'):
					curvar = curvar.upper()
					if isinstance(value,  list):
						content[curvar] = TransdefLine(curvar,  int(0),  None,  (interpreter.lower() if interpreter else None))
						content[curvar].value_list = value
					else:
						content[curvar] = TransdefLine(curvar,  0,  value,  (interpreter.lower() if interpreter else None))
		
		# Translate the values into suitable Python objects
		if 'TRANSLATOR_PERL_DEPENDENCIES' in content and content['TRANSLATOR_PERL_DEPENDENCIES'] and content['TRANSLATOR_PERL_DEPENDENCIES'].value:
			logging.warning(_T("The key 'TRANSLATOR_PERL_DEPENDENCIES' is no more supported in the translator files. Please use 'TRANSLATOR_PYTHON_DEPENDENCIES'"))

		if 'INPUT_EXTENSIONS' in content and content['INPUT_EXTENSIONS'] and content['INPUT_EXTENSIONS'].value_list:
			for i in range(len(content['INPUT_EXTENSIONS'].value_list)):
				e = content['INPUT_EXTENSIONS'].value_list[i]
				if e:
					if not re.match(r'^\.', e):
						e = "." + e
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
					if not re.match(r'^\.', e):
						e = "." + e
					content['OUTPUT_EXTENSIONS'].value_list[i] = e
			if content['OUTPUT_EXTENSIONS'] and content['OUTPUT_EXTENSIONS'].value_list and len(content['OUTPUT_EXTENSIONS'].value_list) > 0:
				try:
					content['OUTPUT_EXTENSIONS'].value = ' '.join(content['OUTPUT_EXTENSIONS'].value_list)
				except:
					content['OUTPUT_EXTENSIONS'].value = ''
			else:
				content['OUTPUT_EXTENSIONS'].value = ''

		return content
