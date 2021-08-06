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

import unittest
import tempfile
import os
import logging

from autolatex2.tex import glossaryanalyzer

class TestGlossaryAnalyzer(unittest.TestCase):

	IDXFILE = 	r'''
				\glossentry{Non-uniform random variate generation!Principle|hyperpage}{6}
				\glossentry{Uniform random variate generation|hyperpage}{6}
				\glossentry{Uniform random variate generation!Principle|hyperpage}{6}
				\glossentry{Uniform random variate generation!Algorithm|hyperpage}{6}
				\glossentry{Uniform random variate generation!Seed|hyperpage}{6}
				\glossentry{Uniform random variate generation!Seed|hyperpage}{7}
				\glossentry{Uniform random variate generation!Algorithm|hyperpage}{7}
				\glossentry{Uniform random variate generation!Properties|hyperpage}{7}
				\glossentry{Uniform random variate generation!Properties|hyperpage}{7}
				\glossentry{Uniform random variate generation!Seed|hyperpage}{7}
				\glossentry{Uniform random variate generation!Properties|hyperpage}{7}
				\glossentry{Non-uniform random variate generation!Inverse method|hyperpage}{7}
				\glossentry{Non-uniform random variate generation!Inverse method!Principle|hyperpage}{7}
				\glossentry{Non-uniform random variate generation!Inverse method!Probability distribution $f(x)$|hyperpage}{7}
				\glossentry{Non-uniform random variate generation!Principle!Cumulative distribution $D(x)$|hyperpage}{8}
				\glossentry{Non-uniform random variate generation!Inverse method!Normal distribution|hyperpage}{8}
				\glossentry{Non-uniform random variate generation!Gauss distribution|hyperindexformat{\see{Normal distribution}}}{8}
				\glossentry{Non-uniform random variate generation!Normal distribution!Probability distribution $f(x)$|hyperpage}{8}
				\glossentry{Non-uniform random variate generation!Normal distribution!Cumulative distribution $D(x)$|hyperpage}{8}
				\glossentry{Non-uniform random variate generation!Normal distribution!Cumulative distribution $D(x)$|hyperpage}{8}
				\glossentry{Non-uniform random variate generation!Normal distribution!$D^{-1}(x)$|hyperpage}{9}
				\glossentry{Non-uniform random variate generation!Inverse method!Exponential distribution|hyperpage}{9}
				\glossentry{Non-uniform random variate generation!Exponential distribution!Probability distribution $f(x)$|hyperpage}{9}
				\glossentry{Non-uniform random variate generation!Exponential distribution!Cumulative distribution $D(x)$|hyperpage}{10}
				\glossentry{Non-uniform random variate generation!Exponential distribution!$D^{-1}(x)$|hyperpage}{10}
				\glossentry{Non-uniform random variate generation!Inverse method!Log-normal distribution|hyperpage}{10}
				\glossentry{Non-uniform random variate generation!Log-normal distribution!Probability distribution $f(x)$|hyperpage}{11}
				\glossentry{Non-uniform random variate generation!Log-normal distribution!Cumulative distribution $D(x)$|hyperpage}{11}
				\glossentry{Non-uniform random variate generation!Log-normal distribution!Cumulative distribution $D(x)$|hyperpage}{11}
				\glossentry{Non-uniform random variate generation!Log-normal distribution!$D^{-1}(x)$|hyperpage}{11}
				\glossentry{Non-uniform random variate generation!Inverse method!Cauchy-Lorentz distribution|hyperpage}{11}
				\glossentry{Non-uniform random variate generation!Breit-Wigner distribution|hyperindexformat{\see{Cauchy-Lorentz distribution}}}{12}
				\glossentry{Non-uniform random variate generation!Cauchy-Lorentz distribution!Probability distribution \ensuremath  {f(x)}|hyperpage}{12}
				\glossentry{Non-uniform random variate generation!Cauchy-Lorentz distribution!Cumulative distribution $D(x)$|hyperpage}{12}
				\glossentry{Non-uniform random variate generation!Cauchy-Lorentz distribution!$D^{-1}(x)$|hyperpage}{12}
				\glossentry{Non-uniform random variate generation!Inverse method!Logistic distribution|hyperpage}{14}
				\glossentry{Non-uniform random variate generation!Logistic distribution!Probability distribution \ensuremath  {f(x)}|hyperpage}{14}
				\glossentry{Non-uniform random variate generation!Logistic distribution!Cumulative distribution $D(x)$|hyperpage}{14}
				\glossentry{Non-uniform random variate generation!Logistic distribution!Cumulative distribution $D(x)$|hyperpage}{14}
				\glossentry{Non-uniform random variate generation!Logistic distribution!$D^{-1}(x)$|hyperpage}{15}
				\glossentry{Non-uniform random variate generation!Inverse method!Triangular distribution|hyperpage}{15}
				\glossentry{Non-uniform random variate generation!Triangular distribution!Probability distribution $f(x)$|hyperpage}{15}
				\glossentry{Non-uniform random variate generation!Triangular distribution!Cumulative distribution $D(x)$|hyperpage}{15}
				\glossentry{Non-uniform random variate generation!Triangular distribution!Cumulative distribution $D(x)$|hyperpage}{16}
				\glossentry{Non-uniform random variate generation!Triangular distribution!$D^{-1}(x)$|hyperpage}{16}
				\glossentry{Non-uniform random variate generation!Inverse method!Linear distribution|hyperpage}{16}
				\glossentry{Non-uniform random variate generation!Linear distribution!Probability distribution $f(x)$|hyperpage}{16}
				\glossentry{Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage}{17}
				\glossentry{Non-uniform random variate generation!Linear distribution!Probability distribution $f(x)$|hyperpage}{17}
				\glossentry{Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage}{17}
				\glossentry{Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage}{17}
				\glossentry{Non-uniform random variate generation!Linear distribution!$D^{-1}(x)$|hyperpage}{17}
				\glossentry{Non-uniform random variate generation!Linear distribution!Probability distribution $f(x)$|hyperpage}{18}
				\glossentry{Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage}{18}
				\glossentry{Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage}{18}
				\glossentry{Non-uniform random variate generation!Linear distribution!$D^{-1}(x)$|hyperpage}{18}
				\glossentry{Non-uniform random variate generation!Procedural method|hyperpage}{19}
				\glossentry{Non-uniform random variate generation!Procedural method!Principle|hyperpage}{19}
				\glossentry{Non-uniform random variate generation!Procedural method!Bernoulli distribution|hyperpage}{19}
				\glossentry{Non-uniform random variate generation!Bernoulli distribution!Probability distribution $f(x)$|hyperpage}{19}
				\glossentry{Non-uniform random variate generation!Bernoulli distribution!Cumulative distribution $D(x)$|hyperpage}{19}
				\glossentry{Non-uniform random variate generation!Bernoulli distribution!$f^{-1}(x)$|hyperpage}{20}
				'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__lastDirname = None
		self.__lastBasename = None
		self.__lastFilename = None
		self.analyzer = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.analyzer = self.__run()

	def __run(self):
		f = tempfile.NamedTemporaryFile(delete=False)
		name = f.name
		self.__lastFilename = name
		self.__lastDirname = os.path.dirname(name)
		self.__lastBasename = os.path.basename(name)
		f.file.write(bytes(self.IDXFILE, 'UTF-8'))
		f.seek(0)
		f.close
		analyzer = glossaryanalyzer.GlossaryAnalyzer(name)
		analyzer.run()
		os.remove(name)
		return analyzer

	def test_basename(self):
		self.assertEqual(self.__lastBasename, self.analyzer.basename)

	def test_filename(self):
		self.assertEqual(self.__lastFilename, self.analyzer.filename)

	def test_glossaryEntries(self):
		self.assertEqual([
				'10|Non-uniform random variate generation!Exponential distribution!$D^{-1}(x)$|hyperpage',
				'10|Non-uniform random variate generation!Exponential distribution!Cumulative distribution $D(x)$|hyperpage',
				'10|Non-uniform random variate generation!Inverse method!Log-normal distribution|hyperpage',

				'11|Non-uniform random variate generation!Inverse method!Cauchy-Lorentz distribution|hyperpage',
				'11|Non-uniform random variate generation!Log-normal distribution!$D^{-1}(x)$|hyperpage',
				'11|Non-uniform random variate generation!Log-normal distribution!Cumulative distribution $D(x)$|hyperpage',
				'11|Non-uniform random variate generation!Log-normal distribution!Probability distribution $f(x)$|hyperpage',

				'12|Non-uniform random variate generation!Breit-Wigner distribution|hyperindexformat{\see{Cauchy-Lorentz distribution}}',
				'12|Non-uniform random variate generation!Cauchy-Lorentz distribution!$D^{-1}(x)$|hyperpage',
				'12|Non-uniform random variate generation!Cauchy-Lorentz distribution!Cumulative distribution $D(x)$|hyperpage',
				'12|Non-uniform random variate generation!Cauchy-Lorentz distribution!Probability distribution \ensuremath  {f(x)}|hyperpage',

				'14|Non-uniform random variate generation!Inverse method!Logistic distribution|hyperpage',
				'14|Non-uniform random variate generation!Logistic distribution!Cumulative distribution $D(x)$|hyperpage',
				'14|Non-uniform random variate generation!Logistic distribution!Probability distribution \ensuremath  {f(x)}|hyperpage',

				'15|Non-uniform random variate generation!Inverse method!Triangular distribution|hyperpage',
				'15|Non-uniform random variate generation!Logistic distribution!$D^{-1}(x)$|hyperpage',
				'15|Non-uniform random variate generation!Triangular distribution!Cumulative distribution $D(x)$|hyperpage',
				'15|Non-uniform random variate generation!Triangular distribution!Probability distribution $f(x)$|hyperpage',

				'16|Non-uniform random variate generation!Inverse method!Linear distribution|hyperpage',
				'16|Non-uniform random variate generation!Linear distribution!Probability distribution $f(x)$|hyperpage',
				'16|Non-uniform random variate generation!Triangular distribution!$D^{-1}(x)$|hyperpage',
				'16|Non-uniform random variate generation!Triangular distribution!Cumulative distribution $D(x)$|hyperpage',

				'17|Non-uniform random variate generation!Linear distribution!$D^{-1}(x)$|hyperpage',
				'17|Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage',
				'17|Non-uniform random variate generation!Linear distribution!Probability distribution $f(x)$|hyperpage',

				'18|Non-uniform random variate generation!Linear distribution!$D^{-1}(x)$|hyperpage',
				'18|Non-uniform random variate generation!Linear distribution!Cumulative distribution $D(x)$|hyperpage',
				'18|Non-uniform random variate generation!Linear distribution!Probability distribution $f(x)$|hyperpage',

				'19|Non-uniform random variate generation!Bernoulli distribution!Cumulative distribution $D(x)$|hyperpage',
				'19|Non-uniform random variate generation!Bernoulli distribution!Probability distribution $f(x)$|hyperpage',
				'19|Non-uniform random variate generation!Procedural method!Bernoulli distribution|hyperpage',
				'19|Non-uniform random variate generation!Procedural method!Principle|hyperpage',
				'19|Non-uniform random variate generation!Procedural method|hyperpage',

				'20|Non-uniform random variate generation!Bernoulli distribution!$f^{-1}(x)$|hyperpage',

				'6|Non-uniform random variate generation!Principle|hyperpage',
				'6|Uniform random variate generation!Algorithm|hyperpage',
				'6|Uniform random variate generation!Principle|hyperpage',
				'6|Uniform random variate generation!Seed|hyperpage',
				'6|Uniform random variate generation|hyperpage',

				'7|Non-uniform random variate generation!Inverse method!Principle|hyperpage',
				'7|Non-uniform random variate generation!Inverse method!Probability distribution $f(x)$|hyperpage',
				'7|Non-uniform random variate generation!Inverse method|hyperpage',
				'7|Uniform random variate generation!Algorithm|hyperpage',
				'7|Uniform random variate generation!Properties|hyperpage',
				'7|Uniform random variate generation!Seed|hyperpage',

				'8|Non-uniform random variate generation!Gauss distribution|hyperindexformat{\see{Normal distribution}}',
				'8|Non-uniform random variate generation!Inverse method!Normal distribution|hyperpage',
				'8|Non-uniform random variate generation!Normal distribution!Cumulative distribution $D(x)$|hyperpage',
				'8|Non-uniform random variate generation!Normal distribution!Probability distribution $f(x)$|hyperpage',
				'8|Non-uniform random variate generation!Principle!Cumulative distribution $D(x)$|hyperpage',

				'9|Non-uniform random variate generation!Exponential distribution!Probability distribution $f(x)$|hyperpage',
				'9|Non-uniform random variate generation!Inverse method!Exponential distribution|hyperpage',
				'9|Non-uniform random variate generation!Normal distribution!$D^{-1}(x)$|hyperpage'], self.analyzer.glossaryEntries)

	def test_md5(self):
		self.assertEqual('2Rzr2qBHOAih35rtX9lbCA==', self.analyzer.md5)




if __name__ == '__main__':
    unittest.main()

