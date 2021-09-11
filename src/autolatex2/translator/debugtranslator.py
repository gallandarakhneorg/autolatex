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
Utility tools for debugging the Python translator scripts.
'''

from autolatex2.utils.runner import Runner

import os
import re
import shutil
from pathlib import Path
import autolatex2.utils.utilfunctions as genutils

def python_translator_debugger_enable():
	'''
	Replies if the feature for debugging a Python translator is active.
	If this function replies True, the function 'python_translator_debugger_code' must contains the code of the translator to test.
	'''
	return False

def python_translator_debugger_code(runner : object,  environment : dict):
	'''
	The code to debug.
	'''
	# Initialization of the script
	_in = environment['in']
	_indir = environment['indir']
	_inexts = environment['inexts']
	_inext = environment['inext']
	_out = environment['out']
	_outdir = environment['outdir']
	_outmode = environment['outmode']
	_outexts = environment['outexts']
	_outext = environment['outext']
	_ext = environment['ext']
	_outbasename = environment['outbasename']
	_outwoext = environment['outwoext']
	_runner = runner
	_python_script_dependencies = environment['python_script_dependencies']
	_global_configuration = environment['global_configuration']
	
	###############################################################
	###############################################################
	## Code to debug
	###############################################################
	###############################################################

	umbrello_cmd = shutil.which('umbrello')
	if not umbrello_cmd:
		umbrello_cmd = shutil.which('umbrello5')
	if not umbrello_cmd:
		umbrello_cmd = shutil.which('umbrello6')
	if not umbrello_cmd:
		raise Exception('Cannot find the umbrello binary file')
	outdir = genutils.basename2(_out,  _outexts)
	if os.path.isdir(outdir):
		shutil.rmtree(outdir)
	os.makedirs(outdir,  exist_ok=True)
	try:
		(sout, serr, sex, retcode) = Runner.runCommand(umbrello_cmd, '--export', 'eps', '--directory', outdir, _in)
		Runner.checkRunnerStatus(serr, sex, retcode)
		generatedFiles = list()
		with os.scandir(outdir) as fdir:
			for fn in fdir:
				if fn.is_file():
					nm = fn.name
					if nm != '..' and nm != '.' and nm.lower().endswith('.eps'):
						ffn = os.path.join(outdir, nm)
						if os.path.isfile(ffn):
							generatedFiles.append(ffn)
		if _global_configuration.generation.pdfMode:
			if len(generatedFiles) > 1:
				template = genutils.basename2(_out,  _outexts) + '_'
				for file in generatedFiles:
					bn = genutils.basename(file, ['.eps'])
					bn = re.sub('\\s+',  '_',  bn)
					outfile = template + bn + '.pdf'
					_runner.generateImage(infile = file, outfile = outfile, onlymorerecent = False,  ignoreDebugFeature = True)
				Path(_out).touch()
			elif len(generatedFiles) > 0:
				file = generatedFiles[0]
				_runner.generateImage(infile = file, outfile = _out, onlymorerecent = False,  ignoreDebugFeature = True)
			else:
				raise Exception("No file generated")
		else:
			if len(generatedFiles) > 1:
				template = genutils.basename2(_out,  _outexts) + '_'
				for file in generatedFiles:
					bn = os.path.basename(file)
					bn = re.sub('\\s+',  '_',  bn)
					outfile = template + bn
					shutil.move(file,  outfile)
				Path(_out).touch()
			elif len(generatedFiles) > 0:
				file = generatedFiles[0]
				shutil.move(file,  _out)
			else:
				raise Exception("No file generated")
	finally:
		if os.path.isdir(outdir):
			shutil.rmtree(outdir)

	###############################################################
	###############################################################
	return _out

