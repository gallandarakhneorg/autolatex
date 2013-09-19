#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/utils/latex_log_parser.py
# Copyright (C) 2013  Stephane Galland <galland@arakhne.org>
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

#---------------------------------
# IMPORTS
#---------------------------------

# Import standard python libs
import os
import re
# Import AutoLaTeX libraries
import utils

#---------------------------------
# INTERNATIONALIZATION
#---------------------------------

import gettext
_T = gettext.gettext



class TeXWarning:
	def __init__(self, filename, extension, line, message):
		self._data = {}
		if extension:
			self._filename = filename.strip()+extension
		else:
			self._filename = filename.strip()
		self._linenumber = line
		expr = re.compile("[\n\r\f\t ]+")
		self._message = re.sub(expr, ' ', message)

	def append(self, message):
		self._message = self._message + message

	def set_data(self, key, value):
		self._data[key] = value

	def get_data(self, key):
		return self._data[key]

	def get_all_data(self):
		return self._data

	def get_filename(self):
		return self._filename

	def get_line_number(self):
		return self._linenumber

	def get_message(self):
		return self._message

	def set_message(self, message):
		self._message = message

	def __str__(self):
		s = str(self._filename)+":"+str(self._linenumber)+":"+str(self._message)+"\n"
		if self._data:
			s = s + self._data
		return s

class Parser:

	def __init__(self, log_file):
		self._directory = os.path.dirname(log_file)
		#
		self._warnings = []
		# Parsing the log file
		regex_start = re.compile("^\\!\\!\\!\\!\\[BeginWarning\\](.*)$")
		regex_end = re.compile("^\\!\\!\\!\\!\\[EndWarning\\]")
		regex_warn = re.compile("^(.*?):([^:]*):([0-9]+):\\s*(.*?)\\s*$")
		f = open(log_file, 'r')
		current_log_block = ''
		warning = False
		line = f.readline()
		while line:
			if warning:
				mo = re.match(regex_end, line)
				if mo:
					mo = re.match(regex_warn, current_log_block)
					if mo:
						w = TeXWarning(
							mo.group(1),
							mo.group(2),
							mo.group(3),
							mo.group(4))
						self._warnings.append(w)
					warning = False
					current_log_block = ''
				else:
					l = line
					if not l.endswith(".\n"):
						l = l.rstrip()
					current_log_block = current_log_block + l
			else:
				mo = re.match(regex_start, line)
				if mo:
					l = mo.group(1)
					if not l.endswith(".\n"):
						l = l.rstrip()
					current_log_block = l
					warning = True
			line = f.readline()

		if warning and current_log_block:
			mo = re.match(regex_warn, current_log_block)
			if mo:
				w = TeXWarning(
					mo.group(1),
					mo.group(2),
					mo.group(3),
					mo.group(4))
				self._warnings.append(w)

	def __str__(self):
		text = ""
		for w in self._warnings:
			text = text + str(w) + "\n"
		return text

	def get_undefined_citation_warnings(self):
		regex = re.compile(
				"^.*citation\\s*\\`([^']+)\\'.+undefined.*$",
				re.I|re.S)
		warnings = []
		for warning in self._warnings:
			message = warning.get_message()
			mo = re.match(regex, message)
			if mo:
				warning.set_message(
					warning.get_filename()+":"+
					str(warning.get_line_number())+": "+
					(_T("Citation '%s' undefined") % mo.group(1)))
				warnings.append(warning)
		return warnings

	def get_undefined_reference_warnings(self):
		regex = re.compile(
				"^.*reference\\s*\\`([^']+)\\'.+undefined.*$",
				re.I|re.S)
		warnings = []
		for warning in self._warnings:
			message = warning.get_message()
			mo = re.match(regex, message)
			if mo:
				warning.set_message(
					warning.get_filename()+":"+
					str(warning.get_line_number())+": "+
					(_T("Reference '%s' undefined") % mo.group(1)))
				warnings.append(warning)
		return warnings

	def get_multidefined_label_warnings(self):
		regex = re.compile(
				"^.*label\\s*\\`([^']+)\\'.+multiply\\s+defined.*$",
				re.I|re.S)
		warnings = []
		for warning in self._warnings:
			message = warning.get_message()
			mo = re.match(regex, message)
			if mo:
				warning.set_message(
					warning.get_filename()+":"+
					str(warning.get_line_number())+": "+
					(_T("Label '%s' multiply defined") % mo.group(1)))
				warnings.append(warning)
		return warnings

