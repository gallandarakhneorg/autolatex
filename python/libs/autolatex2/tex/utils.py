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
	return ['.idx']

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
	re_fatal_error = "==>\\s*f\\s*a\\s*t\\s*a\\s*l\\s+e\\s*r\\s*r\\s*o\\s*r"
	logBlocks = list()
	fatalError = ''
	currentLogBlock = ''
	with open(logFilename, "r") as f:
		line = f.readline()
		while line is not None and line != '' and not fatalError:
			line = line.strip()
			if line is None or line == '':
				# Empty line => break the block
				if currentLogBlock != '':
					if re.search('^.+:[0-9]+:', currentLogBlock, re.M):
						if re.search('^\\!\\s*'+re_fatal_error, currentLogBlock, re.S | re.I):
							fatalError = "\\![^!]"
						else:
							m = re.search('^(.+:[0-9]+:)\\s*'+re_fatal_error, currentLogBlock, re.S | re.I)
							if m:
								fatalError = re.group(1)
							else:
								logBlocks.append(currentLogBlock)
					elif re.search('^\!', currentLogBlock, re.M):
						logBlocks.append(currentLogBlock)
				currentLogBlock = ''
			else:
				currentLogBlock = currentLogBlock + line
			line = f.readline()
	if currentLogBlock != '':
		if re.search('^.+:[0-9]+:', currentLogBlock, re.M):
			if re.search('^\\!\\s*'+re_fatal_error, currentLogBlock, re.S | re.I):
				fatalError = "\\![^!]"
			else:
				m = re.search('^(.+:[0-9]+:)\\s*'+re_fatal_error, currentLogBlock, re.S | re.I)
				if m:
					fatalError = m.group(1)
				else:
					logBlocks.append(currentLogBlock)
		elif currentLogBlock.startswith('!'):
			if re.search('^\\!\\s*'+re_fatal_error, currentLogBlock, re.S | re.I):
				fatalError = "\\![^!]"
			else:
				logBlocks.append(currentLogBlock)
	return (fatalError, logBlocks)


def extractErrorMessageFromTeXLogs(filename : str, fatalError : str, logBlocks : list, isExtendedWarningEnable : bool, latexWarningCode : str) -> str:
	'''
	Parse the given fatal error description and the given log blocks in order to
	extract the complete error message.
	:param filename: The filename of the log file that is used for detecting the error message.
	:type filename: str
	:param fatalError: The definition of the fatal error location, according to the function parseTeXLogFile.
	:type fatalError: str
	:param logBlocks: The blocks of text into the logs, according to the function parseTeXLogFile.
	:type logBlocks: list
	:param isExtendedWarningEnable: Indicates if the AutoLaTeX extension mechanism for warnings is enable.
	:type isExrendedWarningEnable: bool
	:param latexWarningCode: The TeX code that is used for enabling the extension mechanism of the warnings.
	:type latexWarningCode: str
	:rtype: str
	'''
	extractedMessage = ''
	if fatalError is not None and fatalError != '':
		# Parse the fatal error block to extract the filename
		# where the error occured
		m = re.search('^(.+?)\\:([0-9]+)\\:$', fatalError, re.S)
		if m is not None:
			candidate = m.group(1)
			pos = m.group(2)
			candidates = re.split('[\n\r]+', candidate)
			candidate = candidates.pop(0)
			candidate_pattern = re.escape(candidate)
			while candidate is not None and candidate != '' and len(candidates) > 0 and not os.path.isfile(candidate):
				l = candidates.pop(0)
				candidate_pattern = re.escape(l) + '[\n\r]+' + candidate_pattern
				candidate = l + candidate
			if candidate is not None and candidate != '':
				linenumber = int(pos)
				# Search the error message in the log.
				candidate_pattern += re.escape(":"+pos+":")
				# Filtering the 'autogenerated' file
				if isExtendedWarningEnable and os.path.basename(candidate) == 'autolatex_autogenerated.tex':
					code = latexWarningCode
					candidate = filename
					linenumber = linenumber - (code.count('\n') + 1)
				i = 0
				while (extractedMessage is None or extractedMessage == '') and i < len(logBlocks):
					block = logBlocks[i]
					m = re.search(candidate_pattern+'(.*)$', block, re.S)
					if m is not None and m != "":
						messageText = m.group(1)
						extractedMessage = ("%s:%d:%s" % (candidate, linenumber, messageText)).strip()
					i = i + 1
				if extractedMessage is not None and extractedMessage != '':
					if int(pos) != linenumber:
						extractedMessage = re.sub('^'+re.escape(l+pos), l + linenumber, extractedMessage, re.M)
					# Do not cut the words with carriage returns
					extractedMessage = re.sub('([a-z])[\n\r\f]([a-z])', '\\1\\2', extractedMessage, re.S | re.I)
					extractedMessage = re.sub('([a-z]) [\n\r\f]([a-z])', '\\1 \\2', extractedMessage, re.S | re.I)
					extractedMessage = re.sub('([a-z])[\n\r\f] ([a-z])', '\\1 \\2', extractedMessage, re.S | re.I)
		else:
			# Search the error message in the log.
			candidate_pattern += re.escape(fatalError)
			i = 0
			while extractedMessage is None and i < len(logBlocks):
				block = logBlocks[i]
				m = re.search('(?:^|\n|\r)'+candidate_pattern+'\\s*(.*)$', block, re.S)
				if m is not None and m != '':
					message = m.group(1)
					linenumber = 0
					m = re.search('line\\s+([0-9]+)', message, re.I)
					if m is not None and m != '':
						linenumber = int(m.group(1))
					extractedMessage = "%s:%d: %s" % (filename, linenumber, message)
				i = i + 1
	return extractedMessage

