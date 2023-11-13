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
Tools for that is extracting the definitions of glossaries from a GLS file.
'''

import os
import base64
from hashlib import md5

from autolatex2.tex import texparser

class GlossaryAnalyzer(texparser.Observer):
	'''
	Observer on TeX parsing that is extracting the definitions of glossaries from a GLS file.
	'''

	__MACROS = {
		'glossentry' : '[]!{}!{}',
	}

	def __init__(self, filename : str):
		'''
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		'''
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__databases = set()
		self.__glossaryEntries = None
		self.__md5 = None

	@property
	def glossaryEntries(self) -> set:
		'''
		Replies the glossary entries that were specified in the GLS file.
		:return: the set of glossary entries.
		:rtype: set
		'''
		return self.__glossaryEntries

	@property
	def basename(self) -> str:
		'''
		Replies the basename of the parsed file.
		:return: The basename  of the parsed file.
		:rtype: str
		'''
		return self.__basename

	@basename.setter
	def basename(self, n : str):
		'''
		Set the basename of the parsed file.
		:param d: The basename of the parsed file.
		:type n: str
		'''
		self.__basename = n

	@property
	def filename(self) -> str:
		'''
		Replies the filename of the parsed file.
		:return: The filename of the parsed file.
		:rtype: str
		'''
		return self.__filename

	@filename.setter
	def filename(self, n : str):
		'''
		Set the filename of the parsed file.
		:param d: The filename of the parsed file.
		:type n: str
		'''
		self.__filename = n

	@property
	def md5(self) -> str:
		'''
		Parse the idx file, extract the indexes, and build a MD5.
		:return: the MD5 of the indexes.
		'''
		if self.__md5 is None:
			if self.__glossaryEntries is None:
				self.run()
			h = md5(bytes('\\'.join(self.glossaryEntries), 'UTF-8'))
			value = h.digest()
			self.__md5 = base64.encodebytes(value).decode('UTF-8').strip()
		return self.__md5

	def expand(self, parser : texparser.Parser, rawtext : str, name : str, *parameter : texparser.Parameter) -> str:
		'''
		Expand the given macro on the given parameters.
		:param parser: reference to the parser.
		:type parser: Parser
		:param rawtext: The raw text that is the source of the expansion.
		:type rawtext: str
		:param name: Name of the macro.
		:type name: str
		:param parameter: Descriptions of the values passed to the TeX macro.
		:type parameter: Parameter
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		'''
		value = []
		if len(parameter) > 2 and parameter[2]['text']:
			value.append(parameter[2]['text'])
		if len(parameter) > 1 and parameter[1]['text']:
			value.append(parameter[1]['text'])
		if len(value) > 0:
			self.__glossaryEntries.add('|'.join(value))
		return ''

	def run(self):
		'''
		Extract the data from the GLS file.
		'''
		with open(self.filename) as f:
			content = f.read()

		self.__glossaryEntries = set()

		parser = texparser.TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

		self.__glossaryEntries = sorted(self.__glossaryEntries)


