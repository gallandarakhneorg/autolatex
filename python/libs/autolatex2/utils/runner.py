#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-15  Stephane Galland <galland@arakhne.org>
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
Abstract implementation of a command and script runner.
'''

import sys
import io
import subprocess
import pprint
import abc

import gettext
_T = gettext.gettext

######################################################################
##
class CommandExecutionError(Exception):

	def __init__(self, returncode : int):
		'''
		Construct the exception with the given return code.
		:param returncode: The return code of the executed command.
		:type returncode: int
		'''
		self.__errno = returncode
		self.__strerror = _T('Error during the execution of the command: %d') % (returncode)

	@property
	def errno(self) -> int:
		'''
		Replies the number of the error, usually, the return code of executed command.
		:return: The number of the error.
		:rtype: int
		'''
		return self.__errno

	@property
	def strerror(self) -> str:
		'''
		Replies the error message.
		:return: The error message.
		:rtype: str
		'''
		return self.__strerror

	def __str__(self) -> str:
		return self.strerror


######################################################################
##
class AbstractRunner(object):
	'''
	Definition of an abstract implementation of a command and script runner.
	'''
	__metaclass__ = abc.ABCMeta

	@staticmethod
	def runPython(script : str, interceptError : bool = False, localVariables : dict = None):
		'''
		Run a Python script in the current process.
		:param script: The Python script to run.
		:type script: str
		:param interceptError: Indicates if all the exception are intercepted
		                       and put inside the returned value. If False,
		                       the exceptions are not intercepted and they are
		                       raised by this function. Default value is: False.
		:return: A triplet containing the standard output, the
				 error output, and the error.
		:rtype: (str,str,exception)
		'''
		codeOut = io.StringIO()
		codeErr = io.StringIO()
		sys.stdout = codeOut
		sys.stderr = codeErr
		exception = None
		if interceptError:
			try:
				exec(script, None, localVariables)
			except BaseException as e:
				exception = e
		else:
			exec(script, None, localVariables)
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__
		sout = codeOut.getvalue()
		serr = codeErr.getvalue()
		codeOut.close()
		codeErr.close()
		return (sout, serr, exception, (0 if exception is None else 255))

	@staticmethod
	def runCommand(*cmd : str):
		'''
		Run an external command in a subprocess.
		:param cmd: The command line to run.
		:type cmd: list
		:return: A triplet containing the standard output, the
				 error output, and the exception with the return code if different of 0.
		:rtype: (str,str,exception)
		'''
		out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(sout, serr) = out.communicate()
		retcode = out.returncode
		if retcode != 0:
			sex = CommandExecutionError(retcode)
		else:
			sex = None
		if sout is not None and isinstance(sout, bytes):
			sout = sout.decode("ascii")
		if serr is not None and isinstance(serr, bytes):
			serr = serr.decode("ascii")
		return (sout or '', serr or '', sex, retcode)

	@staticmethod
	def runScript(script : str, *interpreter : str):
		'''
		Run a script with the given interpreter.
		The script is passed to the interpreter on the standard input.
		The command line of the interpreter must be specified in order to
		run the interpreter and read the script from the standard input.
		:param script: The script to run.
		:type script: str
		:param interpreter: The command line of the interpreter to use.
		:type interpreter: str
		:return: A triplet containing the standard output, the
				 error output, and the exception with the return code if different of 0.
		:rtype: (str,str,exception)
		'''
		out = subprocess.Popen(interpreter, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		sin = script.encode("ascii")
		(sout, serr) = out.communicate(input=sin)
		if out.returncode != 0:
			sex = CommandExecutionError(out.returncode)
		else:
			sex = None
		if sout is not None and isinstance(sout, bytes):
			sout = sout.decode("ascii")
		if serr is not None and isinstance(serr, bytes):
			serr = serr.decode("ascii")
		return (sout or '', serr or '', sex, out.returncode)


