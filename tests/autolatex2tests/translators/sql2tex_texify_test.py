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

from autolatex2tests.translators.abstracttesttype import AbstractTranslatorTest

class TestTranslator_sql2tex_texify(AbstractTranslatorTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def get_translator_name(self) -> str:
		return 'sql2tex_texify'

	def get_input_filename(self) -> str:
		return 'Test.sql'

	def get_output_filename(self) -> str:
		return 'Test.tex'
