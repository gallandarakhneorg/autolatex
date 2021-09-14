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

import re
import os
import sys
import subprocess
import shutil
import gzip
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

# Read the program information
with open(os.path.join('src', 'autolatex2', 'VERSION'), 'r', encoding='utf-8') as fh:
    line = fh.read()
    m = re.match('^([^ ]+)\\s+(.*?)\\s*$', line)
    if m:
    	name = m.group(1)
    	version = m.group(2)
    else:
    	raise Exception("Cannot read VERSION file")

class PostBuildCommand(build_py):
	def run(self):
		super().run()
		print("Building manual page")
		self.pod2man()

	def pod2man(self, in_pod : str = None, out_man : str = None, out_gz : str = None):
		if not in_pod:
			in_pod = os.path.join('.', 'doc', 'autolatex.pod')
		if not out_man:
			out_man = os.path.join('.', 'build', 'man', 'autolatex.1')
		if not out_gz:
			out_gz = out_man + '.gz' #usr/share/man/man1
		os.makedirs(os.path.dirname(out_man), exist_ok=True)
		rc = subprocess.call(['pod2man', '--center=AutoLaTeX', '--name=' + name, '--release=' + version, in_pod, out_man])
		if rc == 0:
			with open(out_man, 'rb') as f_in:
				with gzip.open(out_gz, 'wb') as f_out:
					shutil.copyfileobj(f_in, f_out)
		else:
			sys.exit(rc)

# Setup
setup(
	cmdclass={
		'build_py': PostBuildCommand,
		#'install': PostInstallCommand,
	},
	name=name,
	version=version,
	author="Stephane Galland",
	author_email="galland@arakhne.org",
	description="AutoLaTeX is a tool for managing LaTeX documents",
	url="https://github.com/gallandarakhneorg/autolatex",
	license='GPL',
	project_urls={
		"Bug Tracker": "https://github.com/gallandarakhneorg/autolatex/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GPL License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.7",
	install_requires=[
		"abc",
		"argparse",
		"base64",
		"configparser",
		"Crypto",
		"dataclasses",
		"enum",
		"fnmatch",
		"gettext",
		"importlib",
		"inspect",
		"io",
		"json",
		"logging",
		"os",
		"platform",
		"pprint",
		"re",
		"setuptools>=42",
		"shlex",
		"shutil",
		"subprocess",
		"sys",
		"textwrap",
		"yaml",
	],
	package_dir={"":"src"},
	packages=find_packages(where='src', exclude=("tests")),
	entry_points=dict(
		console_scripts=['autolatex=autolatex2.cli.autolatex:main']
	),
	include_package_data = True,
	package_data={
		"": ["VERSION", "*.ist", "*.cfg", "translators/*.transdef2"],
	},
)
