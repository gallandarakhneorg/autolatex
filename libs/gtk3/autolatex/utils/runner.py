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
import re
import subprocess

# Try to use the threading library if it is available
try:
  import threading as _threading
except ImportError:
  import dummy_threading as _threading

# Import AutoLaTeX libraries
from . import utils

#---------------------------------
# GLOBAL VARIABLES
#---------------------------------

# List of all the runners
_all_runners = []

#---------------------------------
# FUNCTIONS
#---------------------------------

# Kill all the lancuhed runners.
def kill_all_runners():
  global _all_runners
  tab = _all_runners
  _all_runners = []
  for r in tab:
    r.cancel()

#---------------------------------
# CLASS: Listener
#---------------------------------

#
# Listener are notified by the runner API when
# a task changes its state.
#
class Listener(object):
  # Replies if the current is running.
  # @return true if the task is running, false otherwise.
  def get_runner_progress(self):
    return False

  # Invoked when the task wants to create the associated UI.
  def on_runner_add_ui(self):
    pass

  # Invoked when the task wants to destroy the associated UI.
  def on_runner_remove_ui(self):
    pass

  # Invoked when the task has progressed.
  # @param amount - progression indicator.
  # @param comment - associated comment.
  def on_runner_progress(self, amount, comment):
    pass

  # Invoked when the task has finished.
  # @param retcode - return code of the task.
  # @param output - output of the task (standard output)
  # @param latex_warnings - list of detected warnings.
  def on_runner_finalize_execution(self, retcode, output, latex_warnings):
    pass

#---------------------------------
# CLASS: Runner
#---------------------------------

#
# A runner of a task.
# A task is run in a dedicated thread.
#
class Runner(_threading.Thread):

  # Constructor.
  # @param listener - the listener on the task events.
  # @param directory - the path to set as the current path for the task.
  # @param directive - the AutoLaTeX command, e.g. 'clean', 'all', etc.
  # @param params - the CLI options for AutoLaTeX.
  def __init__(self, listener, directory, directive, params):
    _threading.Thread.__init__(self)
    assert listener
    self.daemon = True
    self._listener = listener
    self._directory = directory
    self._cmd = [ utils.AUTOLATEX_BINARY, '--file-line-warning' ] + params
    if directive:
      self._cmd.append(directive)
    self._has_progress = False
    self._subprocess = None

  # Cancel the execution of the task.
  def cancel(self):
    if self._subprocess:
      self._subprocess.terminate()
      self._subprocess = None
    if self._has_progress:
      # Remove the info bar from the inside of the UI thread
      self._listener.on_runner_remove_ui()
    # Update the rest of the UI from the inside of the UI  thread
    self._listener.on_runner_finalize_execution(0, '', [])

  # Invoked by the background threading API for
  # running the task's activities.
  def run(self):
    global _all_runners
    _all_runners.append(self)
    progress_line_pattern = None

    self._has_progress = self._listener.get_runner_progress()

    if self._has_progress:
      # Add the progress UI
      self._listener.on_runner_add_ui()
      # Update the command line to obtain the progress data
      self._cmd.append('--progress=n')
      # Compile a regular expression to extract the progress amount
      progress_line_pattern = re.compile("^\\[\\s*([0-9]+)\\%\\]\\s+[#.]+(.*)$")

    # Launch the subprocess
    os.chdir(self._directory)
    self._subprocess = subprocess.Popen(self._cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ''
    if self._subprocess:
      if self._has_progress:
        # Use the info bar to draw the progress of the task
        if self._subprocess:
          self._subprocess.poll()
        # Loop until the subprocess is dead
        while self._subprocess and self._subprocess.returncode is None:
          if self._subprocess and not self._subprocess.stdout.closed:
            # Read a line from STDOUT and extract the progress amount
            if self._subprocess:
              self._subprocess.stdout.flush()
            if self._subprocess:
              line = self._subprocess.stdout.readline()
            if line:
              mo = re.match(progress_line_pattern, utils.convert_bytes_to_string(line))
              if mo:
                amount = (float(mo.group(1)) / 100.)
                comment = mo.group(2).strip()
                self._listener.on_runner_progress(amount, comment)

          if self._subprocess:
            self._subprocess.poll()
        # Kill the subprocess if 
        proc = self._subprocess
        if proc:
          retcode = proc.returncode
          # Read the error output of AutoLaTeX
          proc.stderr.flush()
          for line in proc.stderr:
            output = output + utils.convert_bytes_to_string(line)
          proc.stdout.close()
          proc.stderr.close()

      else:
        # Silent execution of the task
        out, err = self._subprocess.communicate() if self._subprocess else ('','')
        retcode = self._subprocess.returncode if self._subprocess else 0
        output = utils.convert_bytes_to_string(err)

      # Stop because the subprocess was cancelled
      if not self._subprocess:
        if self in _all_runners:
          _all_runners.remove(self) 
        return 0
      self._subprocess = None

      # If AutoLaTeX had failed, the output is assumed to
      # be the error message.
      # If AutoLaTeX had not failed, the output may contains
      # "warning" notifications.
      latex_warnings = []
      if retcode == 0:
        regex_expr = re.compile("^\\!\\!(.+?):(W[0-9]+):[^:]+:\\s*(.+?)\\s*$")
        for output_line in re.split("[\n\r]+", output):
          mo = re.match(regex_expr, output_line)
          if mo:
            latex_warnings.append([mo.group(3),mo.group(1), mo.group(2)])
        output = '' # Output is no more interesting

      if self._has_progress:
        # Remove the info bar from the inside of the UI thread
        self._listener.on_runner_remove_ui()
      
      # Update the rest of the UI from the inside of the UI  thread
      self._listener.on_runner_finalize_execution(retcode, output, latex_warnings)
    if self in _all_runners:
      _all_runners.remove(self)

