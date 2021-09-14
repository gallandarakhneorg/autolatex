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
Translation engine.
'''

import logging
import os
import shlex
import subprocess
import re
import importlib
import glob

from autolatex2.translator.translatorobj import Translator
from autolatex2.translator.translatorrepository import TranslatorRepository
import autolatex2.utils.utilfunctions as genutils
import autolatex2.translator.debugtranslator as debugtranslator

import gettext
_T = gettext.gettext



######################################################################
##
class TranslatorError(Exception):

	def __init__(self, msg):
		super().__init__(msg)
		self.message = msg

	def __str__(self) -> str:
		return self.message



######################################################################
##
class TranslatorRunner(object):
	'''
	Runner of translators.
	'''

	def __init__(self, repository : TranslatorRepository):
		'''
		Construct the runner of translators.
		:param repository: The repository of translators.
		:type repository: TranslatorRepository
		'''
		self._repository = repository
		self.configuration = repository.configuration
		self.__images = None

	def sync(self, detect_conflicts : bool = True):
		'''
		Resynchronize the translator data.
		:param detect_conflicts: Indicates if the conflicts in translator loading is run. Default is True.
		:type detect_conflicts: bool
		'''
		self._repository.sync(detect_conflicts = detect_conflicts)
		self.__images = None

	def addSourceImage(self, filename : str):
		'''
		Add a source image.
		:param filename: The filename of a source image.
		:type filename: str
		'''
		if self.__images is None:
			self.__images = set(filename)
		else:
			self.__images.add(filename)

	def getSourceImages(self) -> set:
		'''
		Replies the list of the images on which the translators could be applied.
		:return: The list of the image filenames.
		:rtype: set
		'''
		if self.__images is None:
			self.__images = set()
			# Add the images that were manually specified
			self.__images.update(self.configuration.translators.imagesToConvert)

			# Detect the image formats
			types = set()
			for translator in self._repository.includedTranslators.values():
				types.update(translator.getInputExtensions())
			types = tuple(types)

			# Detect the image from the file system
			for imageDirectory in self.configuration.translators.imagePaths:
				logging.debug(_T("Detecting images inside '%s'") % (imageDirectory))
				if self.configuration.translators.recursiveImagePath:
					for root, dirs, files in os.walk(imageDirectory):
						for filename in files:
							absPath = os.path.join(root, filename)
							if not genutils.isHiddenFile(absPath) and absPath.endswith(types):
								self.__images.add(absPath)
				else:
					for filename in os.listdir(imageDirectory):
						absPath = os.path.join(imageDirectory, filename)
						if not os.path.isdir(absPath) and not genutils.isHiddenFile(absPath):
							if absPath.endswith(types):
								self.__images.add(absPath)
		return self.__images

	def __compareExtensions(o):
		class K:
			def __init__(self, obj):
				self.obj = obj
			def __cmp(self, other):
				if self.obj is None:
					return 0 if other is None else -1
				if other is None:
					return 1
				c = len(other) - len(self.obj)
				if c != 0:
					return c
				return (self.obj > other) - (self.obj < other)
			def __lt__(self, other):
				return self.__cmp(other.obj) < 0
			def __gt__(self, other):
				return self.__cmp(other.obj) > 0
			def __eq__(self, other):
				return self.__cmp(other.obj) == 0
			def __le__(self, other):
				return self.__cmp(other.obj) <= 0
			def __ge__(self, other):
				return self.__cmp(other.obj) >= 0
			def __ne__(self, other):
				return self.__cmp(other.obj) != 0
		return K(o)

	def getTranslatorFor(self, input_filename : str, output_filename : str = None) -> Translator:
		'''
		Replies the translator that could be used for the given filename.
		:param input_filename: The name of the file to the translated.
		:type input_filename: str
		:param output_filename: The name of the file to be generated.
		:type output_filename: str
		:return: The translator or None
		:rtype: Translator
		'''
		# NOTE : Cannot use os.path.splitex because several extensions have characters before the point, e.g. "+tex.svg"
		if os.name == 'nt':
			f0 = input_filename.lower()
		else:
			f0 = input_filename
		candidate_extension = 0
		candidates = list()
		incl = self._repository.includedTranslators
		for translator in incl.values():
			exts = translator.getInputExtensions()
			for extension in exts:
				if f0.endswith(extension):
					ln = len(extension)
					if not candidates or ln > candidate_extension:
						candidate_extension = ln
						candidates = list([translator])
					elif candidate_extension == ln:
						candidates.append(translator)
		ln = len(candidates)
		selected = None
		if ln == 0:
			return None
		elif ln == 1:
			selected = candidates[0]
		else:
			if output_filename is not None:
				if os.name == 'nt':
					f1 = output_filename.lower()
				else:
					f1 = output_filename
				out_candidate_extension = 0
				out_candidates = list()
				for candidate in candidates:
					exts = candidate.getOutputExtensions()
					for extension in exts:
						if f1.endswith(extension):
							ln = len(extension)
							if not candidates or ln > out_candidate_extension:
								out_candidate_extension = ln
								out_candidates = list([candidate])
							elif out_candidate_extension == ln:
								out_candidates.append(candidate)
				if len(out_candidates) == 1:
					selected = out_candidates[0]
				else:
					selected = out_candidates[0]
					logging.warning(_T("Too much translators for file '%s': %s") % (os.path.basename(input_filename), '; '.join(out_candidates)))
					logging.warning(_T("Selecting translator: %s") % (str(selected)))
			else:
				selected = candidates[0]
				logging.warning(_T("Too much translators for file '%s': %s") % (os.path.basename(input_filename), '; '.join(candidates)))
				logging.warning(_T("Selecting translator: %s") % (str(selected)))
		return selected

	def getTemporaryFiles(self,  *, infile : str, translatorName : str = None, outfile : str = None, failOnError : bool = True) -> list:
		'''
		Replies the list of the temporary files that could be generated by the translator.
		:param infile: The name of the source file.
		:type infile: str
		:param translatorName: Name of the translator to run. Default value: None.
		:type translatorName: str
		:param outfile: The name of the output file. Default value: None
		:type outfile: str
		:param failOnError: Indicates if the translator generates a Python exception on error during the run. Default value: True.
		:type failOnError: bool
		:return: The list of the temporary files.
		:rtype: list
		'''
		if not infile:
			return list()

		translator = None
		if translatorName:
			translator = self._repository._getObjectFor(translatorName)
		if translator is None:
			translator = self.getTranslatorFor(infile)
		if translator is None:
			raise TranslatorError(_T("Unable to find a translator for the source image %s") % (infile))

		inexts = translator.getInputExtensions()
		inext = None
		for e in inexts:
			if infile.endswith(e):
				inext = e
				break
		if not inext:
			inext = translator.getInputExtensions()[0]
		outexts = translator.getOutputExtensions()
		if len(outexts) > 0 and outexts[0]:
			outext = outexts[0]
		else:
			outext = ''

		if not outfile:
			outfile = genutils.basename2(infile, inexts) + outext

		environment = translator.getConstants()
		environment['in'] = infile
		indir = os.path.dirname(infile)
		environment['indir'] = indir
		environment['inexts'] = inexts
		environment['inext'] = inext
		environment['out'] = outfile
		outdir = os.path.dirname(outfile)
		environment['outdir'] = outdir
		environment['outexts'] = outexts
		environment['outext'] = outext
		environment['ext'] = outext
		environment['outbasename'] = genutils.basename(outfile, outexts)
		environment['outwoext'] = os.path.join(outdir, environment['outbasename'])
		environment['outmode'] = 'pdf' if translator.configuration.generation.pdfMode else 'eps'

		fixed_patterns = genutils.expandenv(translator.getTemporaryFilePatterns(), environment)
		temp_files = list()
		for pattern in fixed_patterns:
			if os.path.isabs(pattern):
				pt0 = pattern
				pt1 = pattern
			else:
				pt0 = os.path.join(indir,  pattern)
				pt1 = os.path.join(outdir,  pattern)
			temp_files.extend(glob.glob(pathname = pt0,  recursive = False))
			if indir != outdir:
				temp_files.extend(glob.glob(pathname = pt1,  recursive = False))
		return temp_files

	def getTargetFiles(self,  *, infile : str, translatorName : str = None, outfile : str = None, failOnError : bool = True) -> list:
		'''
		Replies the list of the generated files that are by the translator.
		:param infile: The name of the source file.
		:type infile: str
		:param translatorName: Name of the translator to run. Default value: None.
		:type translatorName: str
		:param outfile: The name of the output file. Default value: None
		:type outfile: str
		:param failOnError: Indicates if the translator generates a Python exception on error during the run. Default value: True.
		:type failOnError: bool
		:return: The list of the target files.
		:rtype: list
		'''
		if not infile:
			return list()

		translator = None
		if translatorName:
			translator = self._repository._getObjectFor(translatorName)
		if translator is None:
			translator = self.getTranslatorFor(infile)
		if translator is None:
			raise TranslatorError(_T("Unable to find a translator for the source image %s") % (infile))

		inexts = translator.getInputExtensions()
		inext = None
		len_inext = 0
		for e in inexts:
			if infile.endswith(e) and len(e) > len_inext:
				inext = e
				len_inext = len(e)
		if not inext:
			inext = translator.getInputExtensions()[0]
		outexts = translator.getOutputExtensions()
		if len(outexts) > 0 and outexts[0]:
			outext = outexts[0]
		else:
			outext = ''

		if not outfile:
			outfile = genutils.basename2(infile, inexts) + outext

		environment = translator.getConstants()
		environment['in'] = infile
		indir = os.path.dirname(infile)
		environment['indir'] = indir
		environment['inexts'] = inexts
		environment['inext'] = inext
		environment['out'] = outfile
		outdir = os.path.dirname(outfile)
		environment['outdir'] = outdir
		environment['outexts'] = outexts
		environment['outext'] = outext
		environment['ext'] = outext
		environment['outbasename'] = genutils.basename(outfile, outexts)
		environment['outwoext'] = os.path.join(outdir, environment['outbasename'])
		environment['outmode'] = 'pdf' if translator.configuration.generation.pdfMode else 'eps'

		fixed_patterns = genutils.expandenv(translator.getTargetFilePatterns(), environment)
		target_files = list()
		for pattern in fixed_patterns:
			if os.path.isabs(pattern):
				pt0 = pattern
				pt1 = pattern
			else:
				pt0 = os.path.join(indir,  pattern)
				pt1 = os.path.join(outdir,  pattern)
			target_files.extend(glob.glob(pathname = pt0,  recursive = False))
			if indir != outdir:
				target_files.extend(glob.glob(pathname = pt1,  recursive = False))
		return target_files

	def generateImage(self, *, infile : str, translatorName : str = None, outfile : str = None, onlymorerecent : bool = True, failOnError : bool = True,  ignoreDebugFeature : bool = False) -> str:
		'''
		Generate the image from the given source file by running the appropriate translator.
		:param infile: The name of the source file.
		:type infile: str
		:param translatorName: Name of the translator to run. Default value: None.
		:type translatorName: str
		:param outfile: The name of the output file. Default value: None
		:type outfile: str
		:param onlymorerecent: Indicates if the translation is always run (False) or only if the source file is more recent than the target file. Default value: True
		:type onlymorerecent: bool
		:param failOnError: Indicates if the translator generates a Python exception on error during the run. Default value: True.
		:type failOnError: bool
		:return: The output filename on success; otherwise None on error or if the file is up-to-date
		:rtype: str
		'''
		if not infile:
			return None

		translator = None
		if translatorName:
			translator = self._repository._getObjectFor(translatorName)
		if translator is None:
			translator = self.getTranslatorFor(infile,  outfile)
		if translator is None:
			raise TranslatorError(_T("Unable to find a translator for the source image %s") % (infile))

		if not os.access(infile, os.R_OK):
			errmsg = _T("%s: file not found or not readable.") % (infile)
			if failOnError:
				raise TranslatorError(errmsg)
			else:
				logging.error(errmsg)
				return None

		inexts = translator.getInputExtensions()
		inext = None
		for e in inexts:
			if infile.endswith(e):
				inext = e
				break
		if not inext:
			inext = translator.getInputExtensions()[0]
		outexts = translator.getOutputExtensions()
		if len(outexts) > 0 and outexts[0]:
			outext = outexts[0]
		else:
			outext = ''

		if not outfile:
			outfile = genutils.basename2(infile, inexts) + outext

		# Try to avoid the translation if the source file is no more recent than the target file.
		if onlymorerecent:
			inchange = genutils.getFileLastChange(infile)
			outchange = genutils.getFileLastChange(outfile)
			if outchange is None:
				# No out file, try to detect other types of generated files
				dirname = os.path.dirname(outfile)
				for filename in os.listdir(dirname):
					absPath = os.path.join(dirname, filename)
					if not os.path.isdir(absPath) and not genutils.isHiddenFile(absPath):
						bn = genutils.basename(filename, outexts)
						m = re.match('^('+re.escape(bn+'_')+'.*)'+re.escape(outext)+'$', filename, re.S)
						if m:
							t = genutils.getFileLastChange(absPath)
							if t is not None and (outchange is None or t < outchange):
								outchange = t
								break
			if outchange is not None and inchange <= outchange:
				# No need to translate again
				logging.fine_info(_T("%s is up-to-date") % (os.path.basename(outfile)))
				return None

		logging.info(_T("%s -> %s") % (os.path.basename(infile), os.path.basename(outfile)))
		logging.debug(_T("In: %s") % (infile))
		logging.debug(_T("Out: %s") % (outfile))

		commandLine = translator.getCommandLine()
		embeddedFunction = translator.getEmbeddedFunction()

		environment = translator.getConstants()
		environment['in'] = infile
		environment['indir'] = os.path.dirname(infile)
		environment['inexts'] = inexts
		environment['inext'] = inext
		environment['out'] = outfile
		environment['outdir'] = os.path.dirname(outfile)
		environment['outexts'] = outexts
		environment['outext'] = outext
		environment['ext'] = outext
		environment['outbasename'] = genutils.basename(outfile, outexts)
		environment['outwoext'] = os.path.join(os.path.dirname(outfile), environment['outbasename'])
		environment['outmode'] = 'pdf' if translator.configuration.generation.pdfMode else 'eps'

		if not ignoreDebugFeature and debugtranslator.python_translator_debugger_enable():
			environment['runner'] = self
			environment['python_script_dependencies'] = translator.getPythonDependencies()
			environment['global_configuration'] = translator.configuration
			return debugtranslator.python_translator_debugger_code(self,  environment)
		elif commandLine:
			################################
			# Run an external command line #
			################################
			# Create the environment of variables for the CLI
			# Create the CLI to run
			cli = genutils.expandenv(commandLine, environment)
			
			# Run the cli
			if logging.getLogger().isEnabledFor(logging.DEBUG):
				shCmd = list()
				for e in cli:
					shCmd.append(shlex.quote(e))
				logging.debug(_T("Run: %s") % (' '.join(shCmd)))
			out = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(sout, serr) = out.communicate()
			if out.returncode != 0:
				errmsg = _T("%s\nReturn code: %d") % ((serr or ''), out.returncode)
				if failOnError:
					raise TranslatorError(errmsg)
				else:
					logging.error(errmsg)
					return None
			return outfile
		elif embeddedFunction:
			#########################
			# Run the embedded code #
			#########################
			interpreter = translator.getEmbeddedFunctionInterpreter()
			if not interpreter:
				interpreter = translator.configuration.pythonInterpreter
			else:
				interpreter = interpreter.lower()
			if interpreter == translator.configuration.pythonInterpreter:
				environment['runner'] = self
			environment['python_script_dependencies'] = translator.getPythonDependencies()
			environment['global_configuration'] = translator.configuration

			execEnv = {
				'interpreterObject': None, 
				'global_configuration': translator.configuration,
			}

			if translator.configuration is None:
				raise Exception('No configuration specification')
			
			package_name = "autolatex2.translator.interpreters." + interpreter + "interpreter"
			if importlib.util.find_spec(package_name) is None:
				m = re.match('^(.*?)[0-9]+$',  interpreter)
				if m:
					package_name = "autolatex2.translator.interpreters." + m.group(1) + "interpreter"
			exec("from " + package_name + " import TranslatorInterpreter\n"
					"interpreterObject = TranslatorInterpreter(global_configuration)",  None, execEnv)

			if not execEnv['interpreterObject'].runnable:
				errmsg = _T("Cannot execute the translator '%s'.") % (translatorName)
				if failOnError:
					raise TranslatorError(errmsg)
				else:
					logging.error(errmsg)
					return None
			
			execEnv['interpreterObject'].globalVariables.update(environment)
			(sout, serr, exception, retcode) = execEnv['interpreterObject'].run(embeddedFunction)
			if exception is not None or retcode != 0:
				errmsg = _T("%s\nReturn code: %s") % ((serr or ''), retcode)
				if failOnError:
					raise(TranslatorError(errmsg))
				else:
					logging.error(errmsg)
					return None

			return outfile
		else:
			errmsg = _T("Unable to find the method of translation for '%s'.") % (translatorName)
			if failOnError:
				raise TranslatorError(errmsg)
			else:
				logging.error(errmsg)
				return None
