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
Abstract implementation of a command and script runner.
'''

import sys
import io
import os
import subprocess

import gettext
_T = gettext.gettext

######################################################################
##
class CommandExecutionError(Exception):

	def __init__(self, returncode : int,  msg : str =  None):
		'''
		Construct the exception with the given return code.
		:param returncode: The return code of the executed command.
		:type returncode: int
		:param msg: Error message.
		:type msg: str
		'''
		self.__errno = returncode
		if msg:
			self.__strerror = _T('Error during the execution of the command: %s') % (msg)
		else:
			self.__strerror = _T('Error during the execution of the command; return code is %d') % (returncode)

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
class Runner(object):
	'''
	Definition of an abstract implementation of a command and script runner.
	'''

	@staticmethod
	def checkRunnerStatus(serr, sex, retcode : int = 0):
		'''
		Helper function that generate the correct running behavior regarding the status of a command.
		:param serr: Standard error output.
		:param sex: Exception during script execution.
		:param retcode: The return code.
		'''
		if sex:
			raise sex
		elif retcode != 0:
			if serr:
				raise Exception(serr)
			else:
				raise Exception(_T("Error when running the command. Return code is %d") % (retcode))

	@staticmethod
	def checkRunnerExitCode(code):
		'''
		Helper function that generate the correct running behavior regarding the exit code of a command.
		:param code: exit code of a command.
		'''
		if code != 0:
			raise Exception(_T("Errorneous command with exit code %d") % (code))

	@staticmethod
	def runPython(script : str, interceptError : bool = False, localVariables : dict = None,  showScriptOnError : bool = True):
		'''
		Run a Python script in the current process.
		:param script: The Python script to run.
		:type script: str
		:param interceptError: Indicates if all the exception are intercepted
		                       and put inside the returned value. If False,
		                       the exceptions are not intercepted and they are
		                       raised by this function. Default value is: False.
		:type interceptError: bool
		:param localVariables: Dictionnary of the predefined elmeents (imports or local variables)
		:type localVariables: dict
		:param showScriptOnError: Indicates if the script must be output on the standard error output in case of an error. Default is True.
		:type showScriptOnError: bool
		:return: A triplet containing the standard output, the
				 error output, and the error.
		:rtype: (str,str,exception)
		'''
		script = script + "\n"
		codeOut = io.StringIO()
		codeErr = io.StringIO()
		savedStdout = sys.stdout
		savedStderr = sys.stderr
		sys.stdout = codeOut
		sys.stderr = codeErr
		exception = None
		try:
			if interceptError:
				try:
					exec(script, None,  localVariables)
				except BaseException as e:
					exception = e
			else:
				try:
					exec(script, None,  localVariables)
				except BaseException as err:
					if showScriptOnError:
						savedStderr.write(str(err))
						savedStderr.write(Runner.__formatScript(script))
					raise err
		finally:
			sys.stdout = savedStdout
			sys.stderr = savedStderr
		sout = codeOut.getvalue()
		serr = codeErr.getvalue()
		codeOut.close()
		codeErr.close()
		return (sout, serr, exception, (0 if exception is None else 255))

	@staticmethod
	def __formatScript(script : str) -> str:
		lines = script.split("\n")
		nlines = len(lines)
		pattern = "%d" % (nlines)
		s = len(pattern)
		pattern = "%" + str(s) + "d %s"
		for i in range(nlines):
			nl = str(pattern) % ((i+1),  lines[i])
			lines[i] = nl
		return "\n" + ("\n".join(lines))


	@staticmethod
	def runCommand(*cmd : str) -> tuple:
		'''
		Run an external command in a subprocess.
		:param cmd: The command line to run.
		:type cmd: list
		:return: A triplet containing the standard output, the
				 error output, and the exception with the return code if different of 0.
		:rtype: (str,str,exception,retcode)
		'''
		return Runner.runCommandTo(None,  *cmd)

	@staticmethod
	def runCommandTo(redirectStdoutTo : str,  *cmd : str) -> tuple:
		'''
		Run an external command in a subprocess.
		:param redirectStdoutTo: Specify the path of the file that must receive the standard output.
		:type redirectStdoutTo: str
		:param cmd: The command line to run.
		:type cmd: list
		:return: A triplet containing the standard output, the
				 error output, and the exception with the return code if different of 0.
		:rtype: (str,str,exception,retcode)
		'''
		if redirectStdoutTo is not None:
			with open(redirectStdoutTo, "w") as stdout_file:
				out = subprocess.Popen(cmd, shell=False, stdout=stdout_file, stderr=subprocess.PIPE)
				(sout, serr) = out.communicate()
				retcode = out.returncode
		else:
			out = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(sout, serr) = out.communicate()
			retcode = out.returncode
		if retcode != 0:
			sex = CommandExecutionError(retcode,  serr)
		else:
			sex = None
		if sout is not None and isinstance(sout, bytes):
			sout = sout.decode()
		if serr is not None and isinstance(serr, bytes):
			serr = serr.decode()
		return (sout or '', serr or '', sex, retcode)

	@staticmethod
	def runCommandWithoutRedirect(*cmd : str) -> int:
		'''
		Run an external command in a subprocess without redirecting the input and outputs, and wait for the termination of the subprocess.
		:param cmd: The command line to run.
		:type cmd: list
		:return: exit code
		:rtype: int
		'''
		completed_process = subprocess.run(cmd)
		if completed_process:
			return completed_process.returncode
		return 255

	@staticmethod
	def startCommandWithoutRedirect(*cmd : str) -> bool:
		'''
		Run an external command in a subprocess without redirecting the input and outputs, and do not wait for the termination of the subprocess.
		:param cmd: The command line to run.
		:type cmd: list
		:return: True if the command was launched, False otherwise
		:rtype: bool
		'''
		proc = subprocess.Popen(cmd, shell=False)
		return proc is not None
	
	@staticmethod
	def normalizeCommand(cmd : tuple) -> tuple:
		'''
		Ensure that the command (the first element of the list) is a command with an absolute path.
		:param cmd: The command line to run.
		:type cmd: list
		:rtype: tuple
		'''
		c = cmd[0]
		if not os.path.isabs(c):
			for p in os.getenv("PATH").split(os.pathsep):
				fn = os.path.join(p, c)
				if os.path.exists(fn):
					cmd = list(cmd[1:])
					cmd.insert(0, fn)
					return tuple(cmd)
		return cmd

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
			sex = CommandExecutionError(out.returncode,  serr)
		else:
			sex = None
		if sout is not None and isinstance(sout, bytes):
			sout = sout.decode()
		if serr is not None and isinstance(serr, bytes):
			serr = serr.decode()
		return (sout or '', serr or '', sex, out.returncode)


