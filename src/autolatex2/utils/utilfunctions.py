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
General utilities.
'''

import os
import sys
import re

if os.name == 'nt':
	import win32api
	import win32con

def findFileInPath(filename : str,  useEnvironmentVariable : bool = False) -> str:
	'''
	Search a file into the "sys.path" (filled with PYTHONPATH) variable.
	:param filename: The relative filename.
	:type filenamename: str
	:param useEnvironmentVariable: Indicates if the PYTHONPATH environment variable should be preferred to sys.path.
	:type useEnvironmentVariable: bool
	:return: The absolute path of the file, or None if the file was not found.
	:rtype: str
	'''
	if useEnvironmentVariable:
		path = os.getenv("PYTHONPATH")
		elements = path.split(os.pathsep)
	else:
		elements = sys.path
	for root in elements:
		if root is None or root == '':
			fn = os.path.join(os.curdir, filename)
		else:
			fn = os.path.join(root, filename)
		fn = os.path.abspath(fn)
		if os.path.exists(fn):
			return fn
	return None

def unlink(name : str):
	'''
	Remove the file. Do not fail if the file does not exist.
	:param name: The filename.
	:type name: str
	'''
	try:
		os.unlink(name)
	except:
		pass

def basename(name : str, *ext : str) -> str:
	'''
	Replies the basename, with the given extensions.
	This function remove the directory name.
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

def basename2(name : str, *ext : str) -> str:
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
	bn = basename(name,  *ext)
	dn = os.path.dirname(name)
	if dn:
		return os.path.join(dn,  bn)
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

def getFileLastChange(filename : str) -> int:
	'''
	Replies the time of the last change on the given file.
	'''
	try:
		t1 = os.path.getmtime(filename)
		t2 = os.path.getctime(filename)
		return t1 if t1 >= t2 else t2
	except:
		return None

def parseCLI(commandLine : str, environment : dict = {}, exceptions : set = {}) -> list:
	'''
	Parse the given strings as command lines and extract each component.
	The components are separated by space characters. If you want a
	space character inside a component, you must enclose the component
	with quotes. To have quotes in components, you must protect them
	with the backslash character.
	This function expand the environment variables.</p>
	<p><i>Note:</i> Every parameter that is an associative array is assumed to be an
	environment of variables that should be used prior to <code>os.environ</code> to expand the
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

def abspath(path : str, root : str) -> str:
	'''
	Make the path absolute if not yet.
	:param abspath: The path to make absolute.
	:type abspath: str
	:param root: The root folder to use if the path is not absolute.
	:type root: str
	:return: The absolute path.
	:rtype: str
	'''
	if os.path.isabs(path):
		return path
	return os.path.normpath(os.path.join(root, path))

def to_path_list(value : str,  root : str) -> list:
	'''
	Convert a string to list of paths. According to the operating system, the path separator may be ':' or ';'
	:param value: the value to convert.
	:type value: str
	:param root: the root directory to use for making absolute the paths.
	:type root: str
	:return: the list value.
	:rtype: list
	'''
	if value:
		sep = os.pathsep
		paths = list()
		for p in value.split(sep):
			if os.path.isabs(p):
				paths.append(p)
			else:
				if root:
					pp = os.path.normpath(os.path.join(root,  p))
				else:
					pp = os.path.abspath(p)
				paths.append(pp)
		return paths
	return list()
