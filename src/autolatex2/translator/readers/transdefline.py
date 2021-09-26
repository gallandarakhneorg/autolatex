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
Readers of "transdef" files.
'''

from dataclasses import dataclass


@dataclass
class TransdefLine(object):
	name : str
	lineno : int
	interpreter : str
	value : str
	value_list : list
	
	def __init__(self,  name : str,  lineno : int,  value : str,  interpreter : str):
		'''
		Constructor.
		:param name: The name of transdef entry.
		:type name: str
		:param lineno: The line number into the transdef file.
		:type lineno: int
		:param value: The value extracted from the transdef file.
		:type value: str
		:param interpreter: The interpreter to use for the value (if the value is code).
		:type interpreter: str
		'''
		self.name = name
		self.lineno = lineno
		self.value = value
		self.value_list = list([value])
		self.interpreter = interpreter
