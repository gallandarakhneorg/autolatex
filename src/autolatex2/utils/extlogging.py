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
Extension of the logging library.
'''

import logging
import re
from enum import IntEnum, unique

import gettext
_T = gettext.gettext

@unique
class LogLevel(IntEnum):
	'''
	Logging levels for AutoLaTeX.
	'''
	OFF = logging.CRITICAL + 10
	CRITICAL = logging.CRITICAL
	ERROR= logging.ERROR
	WARNING = logging.WARNING
	FINE_WARNING = logging.WARNING - 5
	INFO = logging.INFO
	FINE_INFO = logging.INFO- 5
	DEBUG = logging.DEBUG
	TRACE = logging.DEBUG - 5

	@staticmethod
	def to_lower_level(level : int) -> int:
		'''
		Replies the lower level.
		:param level: the base level.
		:type level: int
		:return: the lower level.
		:rtype: int
		'''
		if (level > LogLevel.CRITICAL):
			return LogLevel.CRITICAL
		elif (level > LogLevel.ERROR):
			return LogLevel.ERROR
		elif (level > LogLevel.WARNING):
			return LogLevel.WARNING
		elif (level > LogLevel.FINE_WARNING):
			return LogLevel.FINE_WARNING
		elif (level > LogLevel.INFO):
			return LogLevel.INFO
		elif (level > LogLevel.FINE_INFO):
			return LogLevel.FINE_INFO
		elif (level > LogLevel.DEBUG):
			return LogLevel.DEBUG
		elif (level > LogLevel.TRACE):
			return LogLevel.TRACE
		else:
			return logging.NOT_SET


def addLoggingLevel(level_name : str, level_num : int, method_name : str = None):
	"""
	Comprehensively adds a new logging level to the `logging` module and the
	currently configured logging class.

	To avoid accidental clobberings of existing attributes, this method will
	raise an "AttributeError" if the level name is already an attribute of the
	"logging" module or if the method name is already present.
	
	Copied from: https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility

	:param level_name: Name of the level.
	:type level_name: str
	:param level_num: The number associated to the level.
	:type level_num: int
	:param method_name: The name of the method to display the logging message for the given level.
	:type method_name: str
	"""
	level_name = level_name.upper()
	if not method_name:
		method_name = level_name.lower()
	if hasattr(logging, level_name):
		raise AttributeError('{} already defined in logging module'.format(level_name))
	if hasattr(logging, method_name):
		raise AttributeError('{} already defined in logging module'.format(method_name))
	if hasattr(logging.getLoggerClass(), method_name):
		raise AttributeError('{} already defined in logger class'.format(method_name))
	# This method was inspired by the answers to Stack Overflow post
	# http://stackoverflow.com/q/2183233/2988730, especially
	# http://stackoverflow.com/a/13638084/2988730
	def logForLevel(self, message, *args, **kwargs):
		if self.isEnabledFor(level_num):
			self._log(level_num, message, args, **kwargs)
	def logToRoot(message, *args, **kwargs):
		logging.log(level_num, message, *args, **kwargs)
	#
	logging.addLevelName(level_num, level_name)
	setattr(logging, level_name, level_num)
	setattr(logging.getLoggerClass(), method_name, logForLevel)
	setattr(logging, method_name, logToRoot)



def provideLoggingLevel(level_name : str, level_num : int, method_name : str = None):
	"""
	Add logging level if not already defined.

	:param level_name: Name of the level.
	:type level_name: str
	:param level_num: The number associated to the level.
	:type level_num: int
	:param method_name: The name of the method to display the logging message for the given level.
	:type method_name: str
	"""
	if not hasattr(logging, level_name):
		addLoggingLevel(level_name = level_name, level_num = level_num, method_name = method_name)



def ensureAutoLaTeXLoggingLevels():
	"""
	Ensure the loggig levels that are suitable fir AutoLaTeX.
	"""
	provideLoggingLevel('FINE_WARNING',  LogLevel.FINE_WARNING)
	provideLoggingLevel('FINE_INFO',  LogLevel.FINE_INFO)
	provideLoggingLevel('TRACE',  LogLevel.TRACE)

def multiline_debug(message):
	"""
	Show up a debug message that may be split on multiple logging's lines.
	:param message: The multiline message.
	:type message: str or list
	"""
	if logging.getLogger().isEnabledFor(logging.DEBUG) and message:
		message = message.strip()
		if message:
			if isinstance(message,  list):
				msg = message
			else:
				msg = re.split('[\n\r]',  message)
			for line in msg:
				logging.debug(line)

def multiline_info(message):
	"""
	Show up an info message that may be split on multiple logging's lines.
	:param message: The multiline message.
	:type message: str or list
	"""
	if logging.getLogger().isEnabledFor(logging.INFO) and message:
		message = message.strip()
		if message:
			if isinstance(message,  list):
				msg = message
			else:
				msg = re.split('[\n\r]',  message)
			for line in msg:
				logging.info(line)

def multiline_warning(message):
	"""
	Show up a warning message that may be split on multiple logging's lines.
	:param message: The multiline message.
	:type message: str or list
	"""
	if logging.getLogger().isEnabledFor(logging.WARNING) and message:
		message = message.strip()
		if message:
			if isinstance(message,  list):
				msg = message
			else:
				msg = re.split('[\n\r]',  message)
			for line in msg:
				logging.warning(line)

def multiline_error(message):
	"""
	Show up an error message that may be split on multiple logging's lines.
	:param message: The multiline message.
	:type message: str or list
	"""
	if logging.getLogger().isEnabledFor(logging.ERROR) and message:
		message = message.strip()
		if message:
			if isinstance(message,  list):
				msg = message
			else:
				msg = re.split('[\n\r]',  message)
			for line in msg:
				logging.error(line)
