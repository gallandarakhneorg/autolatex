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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of tnghe GNU General Public License
# along with this program; see the file COPYING.	If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

'''
General utilities for TeX.
'''

import os
import re
from enum import IntEnum, unique

import gettext
_T = gettext.gettext

######################################################################
##
@unique
class TeXWarnings(IntEnum):
	'''
	List of LaTeX warnings supported by TeX maker
	'''
	done = 0
	undefined_reference = 1
	undefined_citation = 2
	multiple_definition = 3
	other_warning = 4

######################################################################
##

def getTeXFileExtensions() -> list:
	'''
	Replies the supported filename extensions for TeX files.
	:return: The list of the filename extensions.
	:rtype: list
	'''
	return ['.tex', '.latex', '.ltx']

def getIndexFileExtensions() -> list:
	'''
	Replies the supported filename extensions for Index files.
	:return: The list of the filename extensions.
	:rtype: list
	'''
	return ['.idx',  '.ind']

def getGlossaryFileExtensions() -> list:
	'''
	Replies the supported filename extensions for glossary files.
	:return: The list of the filename extensions.
	:rtype: list
	'''
	return ['.glo',  '.gls',  '.acr',  '.not']

def isTeXFileExtension(ext : str) -> bool:
	'''
	Test if a given string is a standard extension for TeX document.
	The test is case-insensitive.
	:param ext: The extension to test.
	:type ext: str
	:return: True if the extension is for a TeX/LaTeX file; otherwise False.
	:rtype: bool
	'''
	ext = ext.lower()
	return ext in getTeXFileExtensions()

def isTeXDocument(filename : str) -> bool:
	'''
	Replies if the given filname is a TeX document.
	The test is case-insensitive.
	:param filename: The filename to test.
	:type filename: str
	:return: True if the extension is for a TeX/LaTeX file; otherwise False.
	:rtype: bool
	'''
	if filename:
		ext = os.path.splitext(filename)[-1]
		return isTeXFileExtension(ext)
	return False

def extractTeXWarningFromLine(line : str, warnings : set) -> bool:
	'''
	Test if the given line contains a typical TeX warning message.
	This function stores the discovered warning into this maker.
	True is replied if a new run of the TeX compiler is requested
	within the warning message. False is replied if the TeX compiler
	should not be re-run.
	:param line: The line of text to parse.
	:type line: str
	:param warnings: The list of warnings to fill.
	:type warnings: list
	:rtype: bool
	'''
	line = re.sub('[^a-zA-Z:\\-]+', '', line)
	if re.search('Warning.*re\\-?run', line, re.I):
		return True
	elif re.search('Warning:Therewereundefinedreferences', line, re.I):
		warnings.add(TeXWarnings.undefined_reference)
	elif re.search('Warning:Citation.+undefined', line, re.I):
		warnings.add(TeXWarnings.undefined_citation)
	elif re.search('Warning:Thereweremultiply\\-definedlabels', line, re.I):
		warnings.add(TeXWarnings.multiple_definition)
	elif re.search('(?:\\s|^)Warning', line, re.I | re.M):
		warnings.add(TeXWarnings.other_warning)
	return False


def __parseTeXFatalErrorMessage(error : str) -> str:
	err0 = re.sub('\\!\\!\\!\\!\\[BeginWarning\\].*?\\!\\!\\!\\!\\[EndWarning\\].*',  '',  error,  re.S | re.I)
	m = re.match('^.*?:[0-9]+:\\s*(.*?)\\s*$',  err0,  re.S)
	if m:
		return m.group(1).strip()
	return ''


def parseTeXLogFile(logFilename : str) -> tuple:
	'''
	Parse the given file as a TeX log file and extract any relevant information.
	All the block of warnings or errors are detected until a fatal error or the
	end of the file is reached.
	This function replies a tuple in which the first member is the fatal error,
	if one, and the second member is the list of log blocks.
	:param logFilename: The filename of the log file.
	:type logFilename: str
	:rtype: tuple
	'''
	blocks = list()
	fatal_error = ''
	with open(logFilename, "r") as f:
		line = f.readline()
		currentBlock = ''
		while line is not None and line != '':
			line = line.strip()
			if line is None or line == '':
				if currentBlock:
					blocks.append(currentBlock)
					if not fatal_error:
						fatal_error = __parseTeXFatalErrorMessage(currentBlock)
				currentBlock = ''
			else:
				currentBlock = currentBlock + line
			line = f.readline()
	if currentBlock:
		blocks.append(currentBlock)
		if not fatal_error:
			fatal_error = __parseTeXFatalErrorMessage(currentBlock)
	return (fatal_error, blocks)
