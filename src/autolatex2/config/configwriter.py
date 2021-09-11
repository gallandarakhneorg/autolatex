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
Writer of AutoLaTeX Configuration.
'''

import configparser
import os

from autolatex2.config.configobj import Config

class OldStyleConfigWriter(object):
	'''
	Writer of AutoLaTeX Configuration that is written with the old-style format (ini file).
	'''
	
	def to_bool(self,  value : bool) -> str:
		if value is None:
			return None
		return 'true' if value else 'false'

	def to_cli(self,  value) -> str:
		if value:
			if isinstance(value,  list):
				return ' '.join(value)
			else:
				return str(value)
		return None

	def to_path(self,  value,  cdir : str) -> str:
		if value:
			return os.path.relpath(str(value),  cdir)
		return None

	def to_paths(self,  value,  cdir : str) -> str:
		if value:
			if isinstance(value,  list):
				return os.pathsep.join({os.path.relpath(str(f),  cdir) for f in value})
			else:
				return os.path.relpath(str(value),  cdir)
		return None

	def set(self,  config_out,  section : str,  key : str,  value):
		if value:
			config_out.set(section,  key,  value)

	def write(self, filename : str,  config : Config):
		'''
		Write the configuration file.
		:param filename: the name of the file to read.
		:type filename: str
		:param config: the configuration object to fill up.
		:type config: Config
		'''
		dout = os.path.dirname(filename)
		
		config_out = configparser.ConfigParser()

		config_out.add_section('generation')

		self.set(config_out, 'generation', 'main file', self.to_path(os.path.normpath(os.path.join(config.documentDirectory,  config.documentFilename)),  dout))

		self.set(config_out, 'generation', 'image directory', self.to_paths(config.translators.imagePaths,  dout))
		
		self.set(config_out, 'generation', 'generate images', self.to_bool(config.translators.is_translator_enable))
		
		self.set(config_out, 'generation', 'generation type', 'pdf' if config.generation.pdfMode else 'ps')

		self.set(config_out, 'generation', 'tex compiler', config.generation.latexCompiler)

		self.set(config_out, 'generation', 'synctex', self.to_bool(config.generation.synctex))

		self.set(config_out, 'generation', 'translator include path', self.to_paths(config.translators.includePaths,  dout) )

		self.set(config_out, 'generation', 'latex_cmd', self.to_cli(config.generation.latexCLI))
		self.set(config_out, 'generation', 'latex_flags', self.to_cli(config.generation.latexFlags))

		self.set(config_out, 'generation', 'bibtex_cmd', self.to_cli(config.generation.bibtexCLI))
		self.set(config_out, 'generation', 'bibtex_flags', self.to_cli(config.generation.bibtexFlags))

		self.set(config_out, 'generation', 'biber_cmd', self.to_cli(config.generation.biberCLI))
		self.set(config_out, 'generation', 'biber_flags', self.to_cli(config.generation.biberFlags))
	
		self.set(config_out, 'generation', 'makeglossaries_cmd', self.to_cli(config.generation.makeglossaryCLI))
		self.set(config_out, 'generation', 'makeglossaries_flags', self.to_cli(config.generation.makeglossaryFlags))
	
		self.set(config_out, 'generation', 'makeindex_cmd', self.to_cli(config.generation.makeindexCLI))
		self.set(config_out, 'generation', 'makeindex_flags', self.to_cli(config.generation.makeindexFlags))

		self.set(config_out, 'generation', 'dvi2ps_cmd', self.to_cli(config.generation.dvipsCLI))
		self.set(config_out, 'generation', 'dvi2ps_flags', self.to_cli(config.generation.dvipsFlags))

		if config.generation.makeindexStyleFilename:
			if config.generation.makeindexStyleFilename == config.get_system_ist_file():
				self.set(config_out, 'generation', 'makeindex style', '@system')
			elif os.path.dirname(config.generation.makeindexStyleFilename) == config.documentDirectory:
				self.set(config_out, 'generation', 'makeindex style', '@detect@system')
			else:
				self.set(config_out, 'generation', 'makeindex style', config.generation.makeindexStyleFilename)

		config_out.add_section('viewer')

		self.set(config_out, 'viewer', 'view', self.to_bool(config.view.view))

		self.set(config_out, 'viewer', 'viewer', self.to_cli(config.view.viewerCLI))

		clean_files = config.clean.cleanFiles
		cleanall_files = config.clean.cleanallFiles
		if clean_files or cleanall_files:
			config_out.add_section('clean')
			self.set(config_out, 'clean', 'files to clean', self.to_paths(clean_files,  dout))
			self.set(config_out, 'clean', 'files to desintegrate', self.to_paths(cleanall_files,  dout))

		for translator,  included in config.translators.translators().items():
			config_out.add_section(translator)
			self.set(config_out, translator, 'include module', self.to_bool(included))


		with open(filename, 'w') as configfile:
			config_out.write(configfile)
