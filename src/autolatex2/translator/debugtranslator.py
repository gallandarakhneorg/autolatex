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

	epsFile = genutils.basename2(_in,  _inexts) + '.eps'
	try:
		(sout, serr, sex, retcode) = Runner.runCommand( 'asy', '-o', epsFile, _in)
		Runner.checkRunnerStatus(serr, sex, retcode)
		if _global_configuration.generation.pdfMode:
			_runner.generateImage(infile = epsFile, outfile = _out, onlymorerecent = False,  ignoreDebugFeature = True)
	finally:
		genutils.unlink(epsFile)

	###############################################################
	###############################################################
	return _out

