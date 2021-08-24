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
Configuration for the logging system.
'''

from autolatex2.utils.extlogging import LogLevel

import gettext
_T = gettext.gettext

class LoggingConfig(object):
	'''
	Configuration of a AutoLaTeX instance.
	'''

	default_level = LogLevel.ERROR
	default_message = _T('%(levelname)s: %(message)s')

	def __init__(self):
		self.__message = LoggingConfig.default_message
		self.__level = LoggingConfig.default_level

	@property
	def message(self) -> bool:
		'''
		Replies the template for the logging message.
		:return: the template.
		:rtype: str
		'''
		return self.__message

	@message.setter
	def message(self,  template : str):
		'''
		Change the template for the logging message.
		:param template: the template.
		:type template: str
		'''
		if template:
			self.__message = template
		else:
			self.__message = LoggingConfig.default_message

	@property
	def level(self) -> int :
		'''
		Replies the logging level.
		:return: the level.
		:rtype: int
		'''
		return self.__level

	@level.setter
	def level(self,  level : int):
		'''
		Change the logging level.
		:param level: the level.
		:type level: int
		'''
		if level:
			self.__level = level
		else:
			self.__level = LoggingConfig.default_level
