#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-15  Stephane Galland <galland@arakhne.org>
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
Tools that is parsing a TeX file and detect if \documentclass is inside.
'''

import texparser

class DocumentDetector(texparser.Observer):
	'''
	Observer on TeX parsing for detecting the \documentclass macro inside a file.
	'''

	def __init__(self, filename : str=None, text : str=None, lineno : int =1):
		'''
		Constructor.
		:param filename: The name of the file.
		:type filename: str
		:param text: The text to parse. If None, the text is extracted from the file with the given name.
		:type text: str
		:param lineno: The number of the first line.
		:type lineno: int
		'''
		self.__filename = filename
		if text is None:
			with open(self.__filename, 'rb') as f:
				self.__content = f.read().decode('UTF-8')
		else:
			self.__content = text
		self.__lineno = lineno
		self.__latexDocument = False

	@property
	def latex(self) -> bool:
		'''
		Replies if the parsed document is a LaTeX document.
		:return: True if the document contains the \documentclass macro; False otherwise.
		:rtype: bool
		'''
		return self.__latexDocument

	@latex.setter
	def latex(self, l : bool):
		'''
		Set if the parsed document is a LaTeX document.
		:param l: True if the document contains the \documentclass macro; False otherwise.
		:type: bool
		'''
		self.__latexDocument = l

	@property
	def filename(self) -> str:
		'''
		Replies if filename that is parsed.
		:return: The filename.
		:rtype: str
		'''
		return self.__filename

	@filename.setter
	def filename(self, n : str):
		'''
		Replies if filename that is parsed.
		:param n: The filename.
		:type n: str
		'''
		self.__filename = n

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
		if name == '\\documentclass':
			self.latex = True
			parser.stop()
		return None

	def run(self):
		'''
		Determine if the given string is a LaTeX document, ie. it contains the \documentclass macro.
		'''
		self.latex = False
		if (self.__content):
			parser = texparser.TeXParser()
			parser.observer = self
			parser.filename = self.filename
			parser.add_text_mode_macro('documentclass', '![]!{}')
			parser.add_math_mode_macro('documentclass', '![]!{}')
			parser.parse(self.__content, self.__lineno)

