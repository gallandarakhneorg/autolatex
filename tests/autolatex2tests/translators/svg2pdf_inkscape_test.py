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

from autolatex2tests.translators.abstracttesttype import AbstractTranslatorTest

class TestTranslator_svg2pdf_inkscape(AbstractTranslatorTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def get_translator_name(self) -> str:
		return 'svg2pdf_inkscape'

	def get_input_filename(self) -> str:
		return 'Test.svg'

	def get_output_filename(self) -> str:
		return 'Test.pdf'
