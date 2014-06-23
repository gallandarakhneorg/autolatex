#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-14  Stephane Galland <galland@arakhne.org>
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
import sys
import subprocess
import io
import gettext
import configparser

#---------------------------------
# UTILITY FUNCTION
#---------------------------------

# Search an executable in the PATH.
def which(cmd):
  # can't search the path if a directory is specified
  assert not os.path.dirname(cmd)
  extensions = os.environ.get("PATHEXT", "").split(os.pathsep)
  for directory in os.environ.get("PATH", "").split(os.pathsep):
    base = os.path.join(directory, cmd)
    options = [base] + [(base + ext) for ext in extensions]
    for filename in options:
      if os.path.exists(filename):
        return filename
  return None

# Search a module in the sys.path or in search_part.
def resolve_module_path(path, search_path=[]):
  if not os.path.isabs(path):
    for p in search_path:
      full_name = os.path.join(p, path)
      if os.path.exists(full_name):
        return full_name
    for p in sys.path:
      full_name = os.path.join(p, path)
      if os.path.exists(full_name):
        return full_name
  return path

#---------------------------------
# CONSTANTS
#---------------------------------

# Level of verbosity of AutoLaTeX
DEFAULT_LOG_LEVEL = '--quiet'

# String that is representing an empty string for the AutoLaTeX backend.
CONFIG_EMPTY_VALUE = '<<<<empty>>>>'

# Paths
AUTOLATEX_APP_PATH = None
AUTOLATEX_DEV_PATH = None
AUTOLATEX_INSTALL_PATH = None
AUTOLATEX_PO_PATH = None # Default locale path
AUTOLATEX_PM_PATH = None

# Binary files
AUTOLATEX_BINARY = None
DEFAULT_AUTOLATEX_BINARY = None
AUTOLATEX_BACKEND_BINARY = None
DEFAULT_AUTOLATEX_BACKEND_BINARY = None
AUTOLATEX_CONFIG_BINARY = None
DEFAULT_AUTOLATEX_CONFIG_BINARY = None

# Initialize the global values related to AutoLaTeX for an Application.
# @param application_file - filename of the application using this module.
# @param po_name - name of the application for the internalization mechanisms.
# @param search_pat - list of paths in which other modules may be found.
def init_application_configuration(application_file, po_name, search_path=[]):
  init_plugin_configuration(application_file, po_name, search_path)

# Initialize the global values related to AutoLaTeX for a Plugin.
# @param plugin_file - filename of the plugin using this module.
# @param po_name - name of the plugin for the internalization mechanisms.
# @param search_pat - list of paths in which other modules may be found.
def init_plugin_configuration(plugin_file, po_name, search_path=[]):
  global AUTOLATEX_APP_PATH
  global AUTOLATEX_DEV_PATH
  global AUTOLATEX_INSTALL_PATH
  global AUTOLATEX_PO_PATH
  global AUTOLATEX_PM_PATH
  global AUTOLATEX_BINARY
  global AUTOLATEX_BACKEND_BINARY
  global AUTOLATEX_CONFIG_BINARY
  global DEFAULT_AUTOLATEX_BINARY
  global DEFAULT_AUTOLATEX_BACKEND_BINARY
  global DEFAULT_AUTOLATEX_CONFIG_BINARY

  bin_autolatex = which('autolatex')

  # Build the plugin's filename
  plugin_file = resolve_module_path(plugin_file, search_path)

  # Path of the plugin
  AUTOLATEX_APP_PATH = os.path.dirname(plugin_file)

  # Path to the development directory
  pdev_path = os.path.realpath(os.path.join(AUTOLATEX_APP_PATH, 
      os.path.basename(os.path.splitext(plugin_file)[0])+'.py'))
  dev_path = os.path.dirname(pdev_path)
  while dev_path and pdev_path and pdev_path!=dev_path and not os.path.exists(
        os.path.join(dev_path, 'autolatex.pl')):
    pdev_path = dev_path
    dev_path = os.path.dirname(dev_path)
  if dev_path and os.path.isfile(os.path.join(dev_path, 'autolatex.pl')):
    AUTOLATEX_DEV_PATH = dev_path
  else:    
    dev_path = os.path.realpath(bin_autolatex)
    if dev_path:
      AUTOLATEX_DEV_PATH = os.path.dirname(dev_path)
    else:
      AUTOLATEX_DEV_PATH = None


  # Path to the install directory
  if AUTOLATEX_DEV_PATH:
    AUTOLATEX_INSTALL_PATH = AUTOLATEX_DEV_PATH
  else:
    path = os.path.realpath(bin_autolatex)
    AUTOLATEX_INSTALL_PATH = os.path.dirname(path)

  # Path to PO files
  AUTOLATEX_PO_PATH = None
  if AUTOLATEX_DEV_PATH:
    path = os.path.join(AUTOLATEX_DEV_PATH, 'po')
    if os.path.exists(os.path.join(path, 'fr', 'LC_MESSAGES', po_name+'.mo')):
      AUTOLATEX_PO_PATH = path

  # Path to PM files
  AUTOLATEX_PM_PATH = os.path.join(AUTOLATEX_INSTALL_PATH, 'pm')

  # Binary file
  AUTOLATEX_BINARY = bin_autolatex
  if AUTOLATEX_DEV_PATH:
    path = os.path.join(dev_path, 'autolatex.pl')
    if os.path.exists(path):
      AUTOLATEX_BINARY = path
  DEFAULT_AUTOLATEX_BINARY = AUTOLATEX_BINARY

  AUTOLATEX_BACKEND_BINARY = which('autolatex-backend')
  if AUTOLATEX_DEV_PATH:
    path = os.path.join(dev_path, 'autolatex-backend.pl')
    if os.path.exists(path):
      AUTOLATEX_BACKEND_BINARY = path
  DEFAULT_AUTOLATEX_BACKEND_BINARY = AUTOLATEX_BACKEND_BINARY

  AUTOLATEX_CONFIG_BINARY = which('autolatex-config')
  if AUTOLATEX_DEV_PATH:
    path = os.path.join(dev_path, 'autolatex-config.py')
    if os.path.exists(path):
      AUTOLATEX_CONFIG_BINARY = path
  DEFAULT_AUTOLATEX_CONFIG_BINARY = AUTOLATEX_CONFIG_BINARY

  # Init internationalization tools
  gettext.bindtextdomain(po_name, AUTOLATEX_PO_PATH)
  gettext.textdomain(po_name)

# Find the path to an icons
# @param name - basename of the icon.
# @param size - size of the icon.
def _find_icon(name, size):
  path = os.path.join('/usr', 'share', 'icons', name)
  if (os.path.isfile(path)):
    return path
  path = os.path.join(AUTOLATEX_APP_PATH, 'icons', size, name)
  if (os.path.isfile(path)):
    return path
  path = os.path.join(AUTOLATEX_DEV_PATH, 'icons', size, name)
  if (os.path.isfile(path)):
    return path
  path = os.path.join(AUTOLATEX_DEV_PATH, 'libs', 'gtk3', 'autolatex', 'icons', size, name)
  if (os.path.isfile(path)):
    return path
  return os.path.join('/usr', 'share', 'icons', 'autolatex', size, name)

# Make a fully qualified path to the given icon for
# use in a toolbar, assuming
# that it is stored in the AutoLaTeX distribution.
def make_toolbar_icon_path(name):
  return _find_icon(name, '24')

# Make a fully qualified path to the given icon for
# use in a notebook tab, assuming
# that it is stored in the AutoLaTeX distribution.
def make_notebook_icon_path(name):
  return _find_icon(name, '16')

# Make a fully qualified path to the given icon for
# use in a table, assuming
# that it is stored in the AutoLaTeX distribution.
def make_table_icon_path(name):
  return _find_icon(name, '16')

# Convert an array of bytes to a String.
def convert_bytes_to_string(bytes):
  if (bytes):
    return bytes.decode(sys.stdin.encoding)
  return ''

# Replies the first non-null value in the given values.
def first_of(*values):
  for value in values:
    if value is not None:
      return value
  return None

# Replies the name of folder where the AutoLateX 'user' configuration is.
def get_autolatex_user_config_directory():
  if os.name == 'posix':
    return os.path.join(os.path.expanduser("~"), ".autolatex")
  elif os.name == 'nt':
    return  os.path.join(os.path.expanduser("~"),"Local Settings","Application Data","autolatex")
  else:
    return os.path.join(os.path.expanduser("~"), "autolatex")

# Replies the name of file where the AutoLateX 'user' configuration is.
def get_autolatex_user_config_file():
  directory = get_autolatex_user_config_directory()
  if os.path.isdir(directory):
    return os.path.join(directory, 'autolatex.conf')
  if os.name == 'posix':
    return os.path.join(os.path.expanduser("~"), ".autolatex")
  elif os.name == 'nt':
    return  os.path.join(os.path.expanduser("~"),"Local Settings","Application Data","autolatex.conf")
  else:
    return os.path.join(os.path.expanduser("~"), "autolatex.conf")

# Replies the filename of the AutoLateX 'project' configuration when
# it is located in the given directory.
def get_autolatex_document_config_file(directory):
  if os.name == 'posix':
    return os.path.join(directory, ".autolatex_project.cfg")
  else:
    return os.path.join(directory, "autolatex_project.cfg")

# Test if a given string is a standard extension for TeX document
def is_TeX_extension(ext):
  ext = ext.lower()
  if ext == '.tex' or ext =='.latex':
    return True
  else:
    return False

# Replies if the active document is a TeX document.
# @param filename - replies if the given filename is for TeX.
def is_TeX_document(filename):
  if filename:
    ext = os.path.splitext(filename)[-1]
    return is_TeX_extension(ext)
  return False

# Try to find the directory where an AutoLaTeX configuration file is
# located. The search is traversing the parent directory from the current
# document.
# @param current_document - path to the current LaTeX document.
# @return The path to the folder where the AutoLaTeX configuration was found.
#         It is 'current_document' or a parent directory of 'current_document'.
def find_AutoLaTeX_directory(current_document):
  adir = None
  if os.path.isdir(current_document):
    directory = current_document
  else:
    directory = os.path.dirname(current_document)
  directory = os.path.abspath(directory)
  document_dir = directory
  cfgFile = get_autolatex_document_config_file(directory)
  previousFile = ''
  while previousFile != cfgFile and not os.path.exists(cfgFile):
    directory = os.path.dirname(directory)
    previousFile = cfgFile
    cfgFile = get_autolatex_document_config_file(directory)

  if previousFile != cfgFile:
    adir = os.path.dirname(cfgFile)
  else:
    ext = os.path.splitext(current_document)[-1]
    if is_TeX_extension(ext):
      adir = document_dir

  return adir




# BACKEND INTERFACE:
# Replies the installed translators for AutoLaTeX.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @return an INI data structure.
def backend_get_translators(directory):
  os.chdir(directory)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'get', 'translators'], stdout=subprocess.PIPE )
  data = process.communicate()[0]
  string_in = io.StringIO(convert_bytes_to_string(data))
  config = configparser.ConfigParser()
  config.readfp(string_in)
  string_in.close()
  return config

# BACKEND INTERFACE:
# Replies the loaded translators in AutoLaTeX.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @return an INI data structure.
def backend_get_loads(directory):
  os.chdir(directory)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'get', 'loads', ], stdout=subprocess.PIPE )
  data = process.communicate()[0]
  string_in = io.StringIO(convert_bytes_to_string(data))
  config = configparser.ConfigParser()
  config.readfp(string_in)
  string_in.close()
  return config

# BACKEND INTERFACE:
# Replies the configuration of AutoLaTeX.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @return an INI data structure.
def backend_get_configuration(directory, level, section):
  os.chdir(directory)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'get', 'config', level, section], stdout=subprocess.PIPE )
  data = process.communicate()[0]
  string_in = io.StringIO(convert_bytes_to_string(data))
  config = configparser.ConfigParser()
  config.readfp(string_in)
  string_in.close()
  return config

# BACKEND INTERFACE:
# Replies the images that must be auto-generated by AutoLaTeX.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @return an INI data structure.
def backend_get_images(directory):
  os.chdir(directory)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'get', 'images'], stdout=subprocess.PIPE )
  data = process.communicate()[0]
  string_in = io.StringIO(convert_bytes_to_string(data))
  config = configparser.ConfigParser()
  config.readfp(string_in)
  string_in.close()
  return config

# BACKEND INTERFACE:
# Change the loaded translators in the AutoLaTeX configuration.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @param load_config - an INI data structure that contains the plugin states
# @return true on success, false on error
def backend_set_loads(directory, load_config):
  os.chdir(directory)
  string_out = io.StringIO()
  load_config.write(string_out)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'set', 'loads', ], stdin=subprocess.PIPE)
  process.communicate(input=string_out.getvalue())
  string_out.close()
  return process.returncode == 0

# BACKEND INTERFACE:
# Change the configuration of AutoLaTeX.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @param level - indicates the configuration level. It must be one of
#                'user', 'project'.
# @param settings - an INI data structure that contains the new configuration
# @return true on success, false on error
def backend_set_configuration(directory, level, settings):
  os.chdir(directory)
  string_out = io.StringIO()
  settings.write(string_out)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'set', 'config', level, 'false' ], stdin=subprocess.PIPE)
  process.communicate(input=string_out.getvalue())
  string_out.close()
  return process.returncode == 0

# BACKEND INTERFACE:
# Change the configuration related to the auto-generated images by AutoLaTeX.
# @param directory - name of the directory in which the
#                    translators must be search for.
#                    It is usually the directory of
#                    the LaTeX document.
# @param settings - an INI data structure that contains the new configuration.
# @return true on success, false on error
def backend_set_images(directory, settings):
  os.chdir(directory)
  string_out = io.StringIO()
  settings.write(string_out)
  process = subprocess.Popen( [AUTOLATEX_BACKEND_BINARY, 'set', 'images', 'false' ], stdin=subprocess.PIPE)
  process.communicate(input=string_out.getvalue())
  string_out.close()
  return process.returncode == 0

