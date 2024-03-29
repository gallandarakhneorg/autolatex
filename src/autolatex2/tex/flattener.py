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
Tools for creating a flattened version of a TeX document.
A flattened document contains a single TeX file, and all the
other related files are put inside the same directory of
the TeX file.
'''

import os
import shutil
import re
import textwrap
import logging

import gettext
_T = gettext.gettext

from autolatex2.tex import texparser
import autolatex2.utils.utilfunctions as genutils

class Flattener(texparser.Observer):
	'''
	Observer on TeX parsing for creating a flattened version of a TeX document.
	'''

	__MACROS = {
		'input'											: '!{}',
		'include'										: '!{}',
		'usepackage'									: '![]!{}',
		'RequirePackage'							: '![]!{}',
		'documentclass'							: '![]!{}',
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
		'addbibresource'							: '![]!{}',
		'begin'											: '![]!{}', 
		'end'												: '![]!{}', 
	}

	def __init__(self, filename : str, outputDirectory : str):
		'''
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param outputDirectory: The name of the directory in which the document must be generated.
		:type outputDirectory: ste
		'''
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__dirname = os.path.dirname(filename)
		self.__output = outputDirectory
		self.__useBiblio = False
		self.__init()
		self.__included_sty = dict()

	def __init(self) :
		# Inclusion paths for pictures.
		self.__includePaths = []
		if self.__dirname:
			self.__includePaths.append(self.__dirname)
		# Premable entries added by this tool
		self.__dynamicPreamble = []
		# Content of the TeX file to generate
		self.__texFileContent = ''
		# Mapping betwwen the files of the source TeX and the target TeX.
		self.__source2target = dict()
		self.__target2source = dict()
		# Files to copy
		self.__filesToCopy = set()
		# Embedded files
		self.__embedded_files_added = set()
		self.__embedded_files = dict()
		self.__file_content_counter = 0

	@property
	def includePaths(self) -> list:
		'''
		Replies the paths in which included files are search for.
		:return: The list of the inclusion path.
		:rtype: list
		'''
		return self.__includePaths

	@property
	def use_biblio(self) -> bool:
		'''
		Replies if the biblio database.
		:return: True if the biblio database may be use. False for inline biliography entries.
		:rtype: bool
		'''
		return self.__useBiblio

	@use_biblio.setter
	def use_biblio(self, b : bool):
		'''
		Set if the biblio database.
		:param b: True if the biblio database may be use. False for inline biliography entries.
		:type b: bool
		'''
		self.__useBiblio = b

	@property
	def output_directory(self) -> str:
		'''
		Replies the output directory.
		:return: The name  of the output directory.
		:rtype: str
		'''
		return self.__output

	@output_directory.setter
	def output_directory(self, n : str):
		'''
		Set the output directory.
		:param d: The name of output directory.
		:type n: str
		'''
		self.__output = n

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

	def findMacro(self, parser : texparser.Parser, name : str, special : bool, math : bool) -> str:
		'''
		Invoked each time a macro definition is not found in the parser data.
		:param parser: reference to the parser.
		:type parser: Parser
		:param name: Name of the macro.
		:type name: str
		:param special: Indicates if the macro is a special macro or not.
		:type special: bool
		:param math: Indicates if the math mode is active.
		:type math: bool
		:return: the definition of the macro, ie. the macro prototype. See the class documentation for an explanation about the format of the macro prototype.
		:rtype: str
		'''
		if not special:
			if name.startswith('bibliographystyle'):
				return '!{}'
			elif name.startswith('bibliography'):
				return '!{}'
		return None

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
		if text:
			self.__texFileContent += text
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
		if name == "\\begin":
			texname = parameter[1]['text']
			if texname == 'filecontents*':
				self.__file_content_counter = self.__file_content_counter + 1
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}" % (texname)
			return ret
		elif name == "\\end":
			texname = parameter[1]['text']
			if texname == 'filecontents*':
				self.__file_content_counter = self.__file_content_counter - 1
				if self.__file_content_counter <= 0:
					for key,  value in self.__embedded_files.items():
						parser.putBack(value)
					self.__embedded_files = dict()
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}" % (texname)
			return ret
		elif name == "\\usepackage" or name == "\\RequirePackage":
			texname = parameter[1]['text']
			filename = self.__makeFilename(texname, '.sty')
			added_file = ''
			if texname == 'biblatex':
				if not self.use_biblio:
					filename = self.__makeFilename(self.basename, '.bbl', '.tex')
					if os.path.isfile(filename) and filename not in self.__embedded_files_added:
						logging.trace(_T('Embedding %s'), filename)
						if not self.__embedded_files_added:
							self.__dynamicPreamble.append("\\usepackage{filecontents}")
						self.__embedded_files_added.add(filename)
						with open(filename) as f:
							content = f.read()
						basename = os.path.basename(filename)
						added_file = textwrap.dedent("""
								%%=======================================================
								%%== BEGIN FILE: %s
								%%=======================================================
								\\begin{filecontents*}{%s}
								%s
								\\end{filecontents*}
								%%=======================================================
								""") % (basename, basename, content)
					else:
						logging.error(_T('File not found: %s'), filename)
			elif self.__isDocumentFile(filename) and filename not in self.__embedded_files_added:
				logging.trace(_T('Embedding %s'), filename)
				if not self.__embedded_files_added:
					self.__dynamicPreamble.append("\\usepackage{filecontents}")
				self.__embedded_files_added.add(filename)
				with open(filename) as f:
					content = f.read()
				basename = os.path.basename(filename)
				added_file = textwrap.dedent("""
						%%=======================================================
						%%== BEGIN FILE: %s
						%%=======================================================
						\\begin{filecontents*}{%s}
						%s
						\\end{filecontents*}
						%%=======================================================
						""") % (basename, basename, content)
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}" % (texname)
			if added_file:
				if 	self.__file_content_counter <= 0:
					parser.putBack(added_file + ret)
					return ''
				else:
					self.__embedded_files[filename] = added_file
					return ret
			else:
				return ret
		if name == "\\documentclass":
			texname = parameter[1]['text']
			filename = self.__makeFilename(texname, '.cls')
			if self.__isDocumentFile(filename):
				texname = self.__createMapping(filename, '.cls')
				self.__filesToCopy.add(filename)
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}\n\n%%========= AUTOLATEX PREAMBLE\n\n" % (texname)
			return ret
		elif	name == "\\includegraphics" or \
				name == "\\includeanimatedfigure" or \
				name == "\\includeanimatedfigurewtex" or \
				name == "\\includefigurewtex" or \
				name == "\\includegraphicswtex":
			texname, prefix = self.__findPicture(parameter[1]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}" % (texname)
			return ret
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
			return "\\graphicspath{{./}}"
		elif	name == "\\mfigure" or \
				name == "\\mfigure*" or \
				name == "\\mfiguretex" or \
				name == "\\mfiguretex*":
			texname, prefix = self.__findPicture(parameter[2]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}{%s}{%s}{%s}" % (parameter[1]['text'], texname, parameter[3]['text'], parameter[4]['text'])
			return ret
		elif name == "\\msubfigure" or name == "\\msubfigure*":
			texname, prefix = self.__findPicture(parameter[2]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}{%s}{%s}" % (parameter[1]['text'], texname, parameter[3]['text'])
			return ret
		elif name == "\\pgfdeclareimage":
			texname, prefix = self.__findPicture(parameter[2]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % (parameter[0]['text'])
			ret += "{%s}{%s}" % (parameter[1]['text'], texname)
			return ret
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
		elif name.startswith("\\bibliographystyle"):
			if self.use_biblio:
				texname = parameter[0]['text']
				filename = self.__makeFilename(texname, '.bst')
				if self.__isDocumentFile(filename):
					texname = self.__createMapping(filename, '.bst')
					self.__filesToCopy.add(filename)
				return "%s{%s}" % (name, texname)
			return None
		elif name.startswith("\\bibliography"):
			if self.use_biblio:
				texname = parameter[0]['text']
				filename = self.__makeFilename(texname, '.bib')
				if self.__isDocumentFile(filename):
					texname = self.__createMapping(filename, '.bib')
					self.__filesToCopy.add(filename)
				return "%s{%s}" % (name, texname)
			else:
				if len(name) > 13:
					bibdb = name[13:]
				else:
					bibdb = self.basename
				bblFile = bibdb + ".bbl"
				if not os.path.isabs(bblFile):
					bblFile = os.path.join(self.dirname, bblFile)
				if os.path.isfile(bblFile):
					with open(bblFile) as f:
						content = f.read()
					return textwrap.dedent("""
							%%=======================================================
							%%== BEGIN FILE: %s
							%%=======================================================
							%s
							%%=======================================================
							""") % (os.path.basename(bblFile), content)
				else:
					logging.error(_T('File not found: %s'), bblFile)
		elif name == "\\addbibresource":
			if self.use_biblio:
				texname = parameter[1]['text']
				filename = self.__makeFilename(texname, '.bib')
				if self.__isDocumentFile(filename):
					texname = self.__createMapping(filename, '.bib')
					self.__filesToCopy.add(filename)
				return "%s{%s}" % (name, texname)
			else:
				return None
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

	def __isDocumentFile(self, filename : str) -> bool:
		'''
		Replies if the given file is a part of the document.
		:param filename: The filename to test.
		:type filename: str
		:return: True if the file is a part of the document; otherwise False.
		:rtype: bool
		'''
		if not os.path.isabs(filename):
			filename = os.path.join(self.dirname, filename)
		if os.path.isfile(filename):
			return filename.startswith(self.dirname)
		return False;

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
						self.__filesToCopy.add(filename)
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
			self.__filesToCopy.add(filename)

		return (texname, prefix)

	def _analyze_document(self) -> str:
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

		# Replace PREAMBLE content
		if self.__texFileContent:
			preamble = '\n'.join(self.__dynamicPreamble)
			if not preamble:
				preamble = ''
			content = self.__texFileContent.replace('%========= AUTOLATEX PREAMBLE', preamble, 1)

		# Clean the content by removing empty lines
		content = content.replace('\t', ' ').strip()
		content = re.sub("\n+[ \t]*", "\n", content, re.S)

		return content

	def _generate_flat_document(self,  content : str) -> bool:
		'''
		Generate the flat document.
		:param content: The content of the file.
		:type content: str
		:return: The success status of the generation.
		:rtype: bool
		'''
		# Create the output directory
		os.makedirs(self.output_directory)

		# Create the main TeX file
		outputFile = os.path.join(self.output_directory, self.basename) + '.tex';

		logging.debug(_T('Writing %s') % (outputFile))
		with open(outputFile, 'w') as f:
			f.write(content)

		# Copy the resources
		for source in self.__filesToCopy:
			target = self.__source2target[source]
			target = os.path.join(self.output_directory, target)
			logging.debug(_T('Copying resource %s to %s') % (source, target))
			targetDir = os.path.dirname(target)
			if not os.path.isdir(targetDir):
				os.makedirs(targetDir)
			shutil.copy(source, target)
		return True

	def run(self) -> bool:
		'''
		Make the input file standalone.
		:return: True if the execution is a success, otherwise False.
		'''
		self.__init()
		content = self._analyze_document()
		logging.trace(_T("File content: %s") % (content))
		return self._generate_flat_document(content)


