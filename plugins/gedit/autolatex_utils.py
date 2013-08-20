# autolatex - autolatex.py
# Copyright (C) 2013  Stephane Galland <galland@arakhne.org>
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

#---------------------------------
# IMPORTS
#---------------------------------

# Import standard python libs
import os
import subprocess
import ConfigParser
import StringIO

#---------------------------------
# CONSTANTS
#---------------------------------

# Level of verbosity of AutoLaTeX
DEFAULT_LOG_LEVEL = '--quiet'

# Binary file of AutoLaTeX
AUTOLATEX_BINARY = '/home/sgalland/git/autolatex/autolatex.pl'
AUTOLATEX_BACKEND_BINARY = '/home/sgalland/git/autolatex/autolatex-backend.pl'

# Path where the icons are installed
TOOLBAR_ICON_PATH = os.path.join(os.path.dirname(__file__), 'icons', '24')
NOTEBOOK_ICON_PATH = os.path.join(os.path.dirname(__file__), 'icons', '16')
TABLE_ICON_PATH = os.path.join(os.path.dirname(__file__), 'icons', '16')



def make_toolbar_icon_path(name):
	return os.path.join(TOOLBAR_ICON_PATH, name)

def make_notebook_icon_path(name):
	return os.path.join(NOTEBOOK_ICON_PATH, name)

def make_table_icon_path(name):
	return os.path.join(TABLE_ICON_PATH, name)



def backend_get_translators(directory):
	os.chdir(directory)
	process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'get', 'translators'], stdout=subprocess.PIPE )
	data = process.communicate()[0]
	string_in = StringIO.StringIO(data)
	config = ConfigParser.ConfigParser()
	config.readfp(string_in)
	string_in.close()
	return config

def backend_get_loads(directory):
	os.chdir(directory)
	process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'get', 'loads', ], stdout=subprocess.PIPE )
	data = process.communicate()[0]
	string_in = StringIO.StringIO(data)
	config = ConfigParser.ConfigParser()
	config.readfp(string_in)
	string_in.close()
	return config

def backend_set_loads(directory, load_config):
	os.chdir(directory)
	string_out = StringIO.StringIO()
	load_config.write(string_out)
	process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'set', 'loads', ], stdin=subprocess.PIPE)
	process.communicate(input=string_out.getvalue())
	string_out.close()

