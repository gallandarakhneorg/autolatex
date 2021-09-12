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
Tools for extracting the list of the included figures in a TeX document.
'''

import os
import re
import textwrap
import logging

import gettext
_T = gettext.gettext

from autolatex2.tex import texparser
import autolatex2.utils.utilfunctions as genutils

class ImageInclusions(texparser.Observer):
	'''
	Observer on TeX parsing for extracting included images in a TeX document.
	'''

	__MACROS = {
		'input'											: '!{}',
		'include'										: '!{}',
		'includeanimatedfigure'			: '![]!{}',
		'includeanimatedfigurewtex'		: '![]!{}',
		'includefigurewtex'					: '![]!{}',
		'includegraphics'						: '![]!{}',
		'includegraphicswtex'				: '![]!{}',
		'graphicspath'								: '![]!{}',
		'mfigure'										: '![]!{}!{}!{}!{}',
		'mfigure*'										: '![]!{}!{}!{}!{}',
		'msubfigure'									: '![]!{}!{}!{}',
		'msubfigure*'								: '![]!{}!{}!{}',
		'mfiguretex'									: '![]!{}!{}!{}!{}',
		'mfiguretex*'								: '![]!{}!{}!{}!{}',
		'pgfdeclareimage'						: '![]!{}!{}', 
	}

	def __init__(self, filename : str):
		'''
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		'''
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__dirname = os.path.dirname(filename)
		self.__init()

	def __init(self) :
		# Inclusion paths for pictures.
		self.__includePaths = []
		if self.__dirname:
			self.__includePaths.append(self.__dirname)
		# Content of the TeX file to generate
		self.__filesToCopy = set()
		# Mapping betwwen the files of the source TeX and the target TeX.
		self.__source2target = dict()
		self.__target2source = dict()

	@property
	def includePaths(self) -> list:
		'''
		Replies the paths in which included files are search for.
		:return: The list of the inclusion path.
		:rtype: list
		'''
		return self.__includePaths

	def get_included_figures(self) -> set:
		'''
		Replies the list of included figures.
		:rtype: list
		'''
		return self.__filesToCopy

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
	def dirname(self) -> str:
		'''
		Replies the dirname of the parsed file.
		:return: The dirname  of the parsed file.
		:rtype: str
		'''
		return self.__dirname

	@dirname.setter
	def dirname(self, n : str):
		'''
		Set the dirname of the parsed file.
		:param d: The dirname of the parsed file.
		:type n: str
		'''
		self.__dirname = n

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

	def openBlock(self, parser : texparser.Parser, text : str) -> str:
		'''
		Invoked when a block is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return '{'

	def closeBlock(self, parser : texparser.Parser, text : str) -> str:
		'''
		Invoked when a block is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return '}'

	def openMath(self, parser : texparser.Parser, inline : bool) -> str:
		'''
		Invoked when a math environment is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return '$' if inline else '\\['

	def closeMath(self, parser : texparser.Parser, inline : bool) -> str:
		'''
		Invoked when a math environment is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return '$' if inline else '\\]'

	def text(self, parser : texparser.Parser, text : str):
		'''
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		'''
		return None

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
		if	name == "\\includegraphics" or name == "\\includeanimatedfigure" or name == "\\includeanimatedfigurewtex" or name == "\\includefigurewtex" or name == "\\includegraphicswtex":
			self.__findPicture(parameter[1]['text'])
		elif name == "\\graphicspath":
			t = parameter[1]['text']
			if t:
				r = re.match('^\\s*(?:(?:\\{([^\\}]+)\\})|([^,]+))\\s*[,;]?\\s*(.*)$', t)
				while r:					
					path = r.group(1) or r.group(2)
					if not os.path.isabs(path):
						path = os.path.join(self.__dirname, path)
					t = r.group(3)
					self.__includePaths.insert(0, path)
					r = re.match('^\\s*(?:(?:\\{([^\\}]+)\\})|([^,]+))\\s*[,;]?\\s*(.*)$', t) if t else None
		elif	name == "\\mfigure" or name == "\\mfigure*" or name == "\\mfiguretex" or name == "\\mfiguretex*":
			self.__findPicture(parameter[2]['text'])
		elif name == "\\msubfigure" or name == "\\msubfigure*":
			self.__findPicture(parameter[2]['text'])
		elif name == "\\pgfdeclareimage":
			self.__findPicture(parameter[2]['text'])
		elif name == "\\include" or name == "\\input":
			filename = self.__makeFilename(parameter[0]['text'], '.tex')
			with open(filename) as f:
				subcontent = f.read()
			subcontent += textwrap.dedent("""
							%%=======================================================
							%%== END FILE: %s
							%%=======================================================
							""") % (os.path.basename(filename))

			parser.putBack(subcontent)
			return textwrap.dedent("""
					%%=======================================================
					%%== BEGIN FILE: %s
					%%=======================================================
					""") % (os.path.basename(filename))
		# Reply the raw text back to the generated TeX document.
		return rawtext

	def __makeFilename(self, basename : str, ext : str = None) -> str:
		'''
		Create a valid filename for the flattening process.
		:param basename: The basename.
		:param basename: str
		:param ext: The filename extension (default: None).
		:param ext: str
		'''
		if ext and not basename.endswith(ext):
			name = basename + ext
		else:
			name = basename
		if not os.path.isabs(name):
			return os.path.join(self.dirname, name)
		return name

	def __createMapping(self, filename : str, ext : str) -> str:
		'''
		Compute an unique filename, and map it to the source file.
		:param filename: The filename to translate.
		:type filename: str
		:param ext: The filename extension to remove.
		:type ext: str
		:return: The unique basename.
		:rtype: str
		'''
		name = os.path.basename(filename)
		if ext and name.endswith(ext):
			name = name[0:(-len(ext))]
		bn = name
		i = 0
		while (name + ext) in self.__target2source:
			name = "%s_%d" % (bn, i)
			i += 1
		self.__target2source[name + ext] = filename
		self.__source2target[filename] = name + ext
		return name

	def __findPicture(self, texname : str):
		'''
		Find a picture.
		:param texname: The name of the picture in the TeX document.
		:type texname: str
		:return: the tuple (target filename, the prefix to add before the macro)
		:rtype:
		'''
		# Search in the registered/found bitmaps
		if self.__source2target:
			for src in self.__source2target:
				if src == texname:
					return (os.path.basename(self.__source2target), '')

		prefix = ''
		filename = self.__makeFilename(texname)
		if not os.path.isfile(filename):
			texexts = ('.pdftex_t', '.pstex_t', '.pdf_tex', '.ps_tex', '.tex')
			figexts = (	'.pdf', '.eps', '.ps', '.png', '.jpeg', '.jpg', '.gif', '.bmp')
			exts = figexts + texexts
			ofilename = filename
			obasename = genutils.basename(texname, *exts)
			filenames = {}

			# Search in the registered paths
			template = obasename
			for path in self.includePaths:
				for ext in figexts:
					fullname = os.path.join(path, template + ext)
					fullname = self.__makeFilename(fullname)
					if os.path.isfile(fullname):
						filenames[fullname] = False
				for ext in texexts:
					fullname = os.path.join(path, template + ext)
					fullname = self.__makeFilename(fullname, '')
					if os.path.isfile(fullname):
						filenames[fullname] = True

			# Search in the folder, i.e. the document directory.
			if not filenames:
				template = os.path.join(os.path.dirname(ofilename), genutils.basename(ofilename, exts))
				for ext in figexts:
					fn = template + ext
					if os.path.isfile(fn):
						filenames[fn] = False
				for ext in texexts:
					fn = template + ext
					if os.path.isfile(fn):
						filenames[fn] = True

			if not filenames:
				logging.error(_T('Picture not found: %s'), texname)
			else:
				selectedName1 = None
				selectedName2 = None
				for filename in filenames:
					ext = os.path.splitext(filename)[1] or ''
					texname = self.__createMapping(filename, ext) + ext
					if filenames[filename]:
						if not selectedName1:
							selectedName1 = (texname, filename)
					else:
						self.__filesToCopy.add(os.path.normpath(filename))
						selectedName2 = texname
				if selectedName1:
					texname, filename = selectedName1
					logging.trace(_T('Embedding %s'), filename)
					with open(filename) as f:
						filecontent = f.read()
					# Replacing the filename in the newly embedded TeX file
					if self.__source2target:
						for source in self.__source2target:
							filecontent = filecontent.replace('{' + source + '}',
											'{' + self.__source2target[source] + '}')
					prefix +=	textwrap.dedent("""
								%%=======================================================
								%%== BEGIN FILE: %s
								%%=======================================================
								\\begin{filecontents*}{%s}
								%s
								\\end{filecontents*}
								%%=======================================================
								""") % (os.path.basename(texname), os.path.basename(texname), filecontent)
					self.__dynamicPreamble.append(r'\usepackage{filecontents}')
				elif selectedName2:
					texname = selectedName2
		else:
			ext = os.path.splitext(texname)[1] or ''
			texname = self.__createMapping(filename, ext) + ext
			self.__filesToCopy.add(os.path.normpath(filename))

		return (texname, prefix)

	def _analyze_document(self):
		'''
		Analyze the tex document for extracting information.
		:return: The content of the file.
		'''
		with open(self.filename) as f:
			content = f.read()

		parser = texparser.TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

	def run(self) -> bool:
		'''
		Make the input file standalone.
		:return: True if the execution is a success, otherwise False.
		'''
		self.__init()
		self._analyze_document()
		return True


