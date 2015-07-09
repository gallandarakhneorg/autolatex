#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-15	Stephane Galland <galland@arakhne.org>
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
General utilities.
'''

import os
import sys
import re

if os.name == 'nt':
	import win32api
	import win32con

import autolatex2.utils.debug as debug

def basename(name : str, *ext : str) -> str:
	'''
	Replies the basename, with the given extensions.
	This function mimics the 'basename' command on Unix systems.
	:param name: The filename.
	:type name: str
	:param ext: The extensions to remove.
	:type ext: str
	:return: The absolute path of the command, or None.
	:rtype: str
	'''
	bn = os.path.basename(name)
	for e in ext:
		if isinstance(e, list) or isinstance(e, tuple) or isinstance(e, set):
			for e2 in e:
				if bn.endswith(e2):
					i = len(e2)
					n = bn[0:-i]
					return n
		elif bn.endswith(e):
			i = len(e)
			n = bn[0:-i]
			return n
	return bn

def firstOf(*values : list) -> object:
	'''
	Replies the first non-null value in the given values.
	:param values: The array of values.
	:type values: list
	:return: the first non-null value, or None.
	:rtype: object
	'''
	for value in values:
		if value is not None:
			return value
	return None

def isHiddenFile(filename : str) -> bool:
	'''
	Replies if the file with the given name is hidden.
	:param filename: The name of the file.
	:type filename: str
	:return: True if the file is hidden.
	:rtype: bool
	'''
	if os.name == 'nt':
		attribute = win32api.GetFileAttributes(filename)
		return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
	else:
		return filename.startswith('.')

def fileLastChange(filename : str) -> int:
	'''
	Replies the time of the last change on the given file.
	'''
	try:
		t1 = os.path.getmtime(filename)
		t2 = os.path.getctime(filename)
		return t1 if t1 >= t2 else t2
	except:
		return None

def parseCLI(commandLine : str, environment : dict, exceptions : set = {}) -> list:
	'''
	<p>Parse the given strings as command lines and extract each component.
	The components are separated by space characters. If you want a
	space character inside a component, you muse enclose the component
	with quotes. To have quotes in components, you must protect them
	with the backslash character.
	This function expand the environment variables.</p>
	<p><i>Note:</i> Every paramerter that is an associative array is assumed to be an
	environment of variables that should be used prior to <code>@ENV</code> to expand the
	environment variables. The elements in the parameter are treated from the
	first to the last. Each time an environment was found, it is replacing any
	previous additional environment.</p>
	:param exceptions: The names of the environment variables to not expand.
	:type exceptions: set
	:return: The CLI elements.
	:rtype: list
	'''
	r = list()
	commandLine = commandLine.strip()
	if commandLine:
		protect = ''
		value = ''
		m = re.match('^(.*?)(["\']|(?:\\s+)|(?:\\.)|(?:\\$[a-zA-Z0-9_]+)|(?:\\$\\{[a-zA-Z0-9_]+\\}))(.*)$', commandLine, re.S)
		while m:
			prefix = m.group(1)
			sep = m.group(2)
			commandLine = m.group(3)
			value += prefix
			if sep.startswith('\\'):
				value += sep[1:]
			else:
				varname = None
				if sep.startswith('${'):
					varname = sep[2:-1]
				elif sep.startswith('$'):
					varname = sep[1:]
				if varname:
					if protect == '\'' or varname in exceptions:
						value += sep
					elif environment and varname in environment:
						value += environment[varname] or ''
					else:
						value += os.environ.get(varname) or ''
				elif sep == '"' or sep == '\'':
					if not protect:
						protect = sep
					elif protect == sep:
						protect = ''
					else:
						value += sep
				elif protect:
					value += sep
				elif value:
					r.append(value)
					value = ''
			m = re.match('^(.*?)(["\']|(?:\\s+)|(?:\\.)|(?:\\$[a-zA-Z0-9_]+)|(?:\\$\\{[a-zA-Z0-9_]+\\}))(.*)$', commandLine, re.S)
		if commandLine:
			    value += commandLine
		if value:
			    r.append(value)
	return r

