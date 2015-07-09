#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-14  Stephane Galland <galland@arakhne.org>
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
Provides tools for debugging autolatex.
'''

import os
import pprint

def dbg(*variables1 : object, **variables2 : object):
	'''
	Raw display the values of the given variables on the console.
	This function never returns.
	:param variables1: The list of variables to display.
	:type variables1: object
	:param variables2: The dictionary of variables to display.
	:type variables2: object
	'''
	dbg_print(*variables1, **variables2)
	exit(255)

def dbg_print(*variables1 : object, **variables2 : object):
	'''
	Raw display the values of the given variables on the console.
	:param variables1: The list of variables to display.
	:type variables1: object
	:param variables2: The dictionary of variables to display.
	:type variables2: object
	'''
	pp = pprint.PrettyPrinter(indent=2)
	if variables1: pp.pprint(variables1)
	if variables2: pp.pprint(variables2)

def dbg_struct(var : object):
	'''
	Raw display the value structure of the given variable on the console.
	This function never returns.
	:param var: The variable to display.
	:type var: object
	'''
	print (var.__class__)
	print (dir(var))
	exit(255)

def dbg_showfolder(folder : str, recursive : bool = False):
	'''
	Print the content of a folder.
	The output is similar to the 'ls -lR' command line on Unix systems.
	:param folder: The name of the folder to display.
	:type folder: str
	:param recursive: Indicates if the subfolders are also displayed (default: False).
	:type recursive: bool
	'''
	print()
	for dirname, dirnames, filenames in os.walk(folder):
		print("%s:" % dirname)

		# print path to all subdirectories first.
		for subdirname in dirnames:
			print("%s/" % subdirname)

		# print path to all filenames.
		for filename in filenames:
			print(filename)

		if recursive:
			for subdirname in dirnames:
				fullPath = os.path.join(dirname, subdirname)
				print()
				dbg_showfolder(fullPath, recursive)

