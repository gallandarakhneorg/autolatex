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
Tools for extracting the bibliography citations from a AUX file or a BSF file.
'''

import os
import re
import base64
from Crypto.Hash import MD5

from autolatex2.tex import texparser

class AuxiliaryCitationAnalyzer(texparser.Observer):
	'''
	Observer on TeX parsing extracting the bibliography citations from a AUX file.
	'''

	__MACROS = {
		'citation'			: '[]!{}',
		'bibcite'			: '[]!{}',
		'bibdata'			: '[]!{}',
		'bibstyle'			: '[]!{}',
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
		self.__styles = set()
		self.__citations = None
		self.__md5 = None

	@property
	def databases(self) -> set:
		'''
		Replies the databases that were specified in the AUX file.
		:return: the set of databases.
		:rtype: set
		'''
		return self.__databases

	@property
	def styles(self) -> set:
		'''
		Replies the bibliography styles that were specified in the AUX file.
		:return: the set of styls.
		:rtype: set
		'''
		return self.__styles

	@property
	def citations(self) -> set:
		'''
		Replies the bibliography citations that were specified in the AUX file.
		:return: the set of citations.
		:rtype: set
		'''
		if self.__citations is None:
			return set()
		return self.__citations

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
		Parse the aux file, extract the bibliography citations, and build a MD5.
		:return: the MD5 of the citations.
		'''
		if self.__md5 is None:
			if self.__citations is None:
				self.run()
			h = MD5.new()
			h.update(bytes('\\'.join(self.citations), 'UTF-8'))
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
		if name == '\\bibdata':
			if parameter and len(parameter) > 1 and 'text' in parameter[1] and parameter[1]['text']:
				for bibdb in re.split(r'\s*,\s*', parameter[1]['text']):
					if bibdb:
						self.__databases.add(bibdb)
		elif name == '\\bibstyle':
			if parameter and len(parameter) > 1 and 'text' in parameter[1] and parameter[1]['text']:
				for bibdb in re.split(r'\s*,\s*', parameter[1]['text']):
					if bibdb:
						self.__styles.add(bibdb)
		elif parameter and len(parameter) > 1 and 'text' in parameter[1] and parameter[1]['text']:
			for bibdb in re.split(r'\s*,\s*', parameter[1]['text']):
				if bibdb:
					self.__citations.add(bibdb)
		return ''

	def run(self):
		'''
		Extract the data from the AUX file.
		'''
		with open(self.filename) as f:
			content = f.read()

		self.__citations = set()

		parser = texparser.TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

		self.__citations = sorted(self.__citations)





class BiblatexCitationAnalyzer(texparser.Observer):
	'''
	Observer on TeX parsing extracting the bibliography citations from a BCF (biblatex) file.
	'''

	def __init__(self, filename : str):
		'''
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		'''
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__citations = None
		self.__md5 = None

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
	def citations(self) -> set:
		'''
		Replies the bibliography citations that were specified in the BCF file.
		:return: the set of citations.
		:rtype: set
		'''
		if self.__citations is None:
			return set()
		return self.__citations

	@property
	def md5(self) -> str:
		'''
		Parse the bcf file, extract the bibliography citations, and build a MD5.
		:return: the MD5 of the citations.
		'''
		if self.__md5 is None:
			if self.__citations is None:
				self.run()
			h = MD5.new()
			h.update(bytes('\\'.join(self.citations), 'UTF-8'))
			value = h.digest()
			self.__md5 = base64.encodebytes(value).decode('UTF-8').strip()
		return self.__md5

	def run(self):
		'''
		Extract the data from the BCF file.
		'''
		with open(self.filename) as f:
			content = f.read()

		citations = set()

		for citation in re.findall(re.escape('<bcf:citekey>') + '(.+?)' + re.escape('</bcf:citekey>'), content, re.DOTALL):
			citations.add(citation)

		self.__citations = sorted(citations)

