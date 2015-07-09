#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015  Stephane Galland <galland@arakhne.org>
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
import pathlib

from autolatex2.tex import dependencyanalyzer

from autolatex2.utils import debug

class TestDependencyAnalyzer(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__lastDirname = None
		self.__lastBasename = None
		self.__lastFilename = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)

	def ___run(self, content : str, *filenames : str):
		f = tempfile.NamedTemporaryFile(delete=False)
		name = f.name
		self.__lastFilename = name
		self.__lastDirname = os.path.dirname(name)
		self.__lastBasename = os.path.basename(name)
		f.file.write(bytes(content, 'UTF-8'))
		f.seek(0)
		f.close
		for filename in filenames:
			pathlib.Path(os.path.join(self.__lastDirname, filename)).touch()
		analyzer = dependencyanalyzer.DependencyAnalyzer(name, self.__lastDirname)
		analyzer.run()
		os.remove(name)
		for filename in filenames:
			os.remove(os.path.join(self.__lastDirname, filename))
		return analyzer

	def test_emptyString(self):
		analyzer = self.___run('')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_input_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\input{myfile}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_input_file(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\input{myfile}\end{document}', 'myfile.tex')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(1, len(types))
		self.assertTrue('tex' in types)
		texDeps = analyzer.getDependencies('tex')
		self.assertEqual({os.path.join(self.__lastDirname, "myfile.tex")}, texDeps)
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_include_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\include{myfile}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_include_file(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\include{myfile}\end{document}', 'myfile.tex')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(1, len(types))
		self.assertTrue('tex' in types)
		texDeps = analyzer.getDependencies('tex')
		self.assertEqual({os.path.join(self.__lastDirname, "myfile.tex")}, texDeps)
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_makeindex(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\makeindex\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertTrue(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_printindex(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\printindex\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertTrue(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_multibib(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage{multibib}\begin{document}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_biblatex(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage{biblatex}\begin{document}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_biber(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage[backend=biber]{biblatex}\begin{document}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_biblatex)
		self.assertTrue(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_usepackage_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage{mypackage}\begin{document}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_usepackage_file(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage{mypackage}\begin{document}\end{document}', 'mypackage.sty')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(1, len(types))
		self.assertTrue('sty' in types)
		texDeps = analyzer.getDependencies('sty')
		self.assertEqual({os.path.join(self.__lastDirname, "mypackage.sty")}, texDeps)
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_requirepackage_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\RequirePackage{mypackage}\begin{document}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_requirepackage_file(self):
		analyzer = self.___run(r'\documentclass{article}\RequirePackage{mypackage}\begin{document}\end{document}', 'mypackage.sty')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(1, len(types))
		self.assertTrue('sty' in types)
		texDeps = analyzer.getDependencies('sty')
		self.assertEqual({os.path.join(self.__lastDirname, "mypackage.sty")}, texDeps)
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_documentclass_nofile(self):
		analyzer = self.___run(r'\documentclass{myarticle}\begin{document}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_documentclass_file(self):
		analyzer = self.___run(r'\documentclass{myarticle}\begin{document}\end{document}', 'myarticle.cls')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(1, len(types))
		self.assertTrue('cls' in types)
		texDeps = analyzer.getDependencies('cls')
		self.assertEqual({os.path.join(self.__lastDirname, "myarticle.cls")}, texDeps)
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_bibliography_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\bibliography{mybib}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_bibliography_file(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\bibliography{mybib}\end{document}', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(1, len(types))
		self.assertTrue(self.__lastBasename in types)
		dbs = analyzer.getBibDependencies('bib', self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertEqual({os.path.join(self.__lastDirname, "mybib.bib")}, dbs)

	def test_bibliographyXXX_nomultibib_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\bibliographyXXX{mybib}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_nomultibib_file(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\bibliographyXXX{mybib}\end{document}', 'mybib.cls')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_multibib_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage{multibib}\begin{document}\bibliographyXXX{mybib}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_multibib_file(self):
		analyzer = self.___run(r'\documentclass{article}\usepackage{multibib}\begin{document}\bibliographyXXX{mybib}\end{document}', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(1, len(types))
		self.assertTrue('XXX' in types)
		dbs = analyzer.getBibDependencies('bib', 'XXX')
		self.assertEqual(1, len(dbs))
		self.assertEqual({os.path.join(self.__lastDirname, "mybib.bib")}, dbs)

	def test_bibliographystyle_nofile(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\bibliographystyle{mystyle}\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(0, len(types))

	def test_bibliographystyle_file(self):
		analyzer = self.___run(r'\documentclass{article}\begin{document}\bibliographystyle{mystyle}\end{document}', 'mystyle.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.getDependencyTypes()
		self.assertEqual(0, len(types))
		types = analyzer.getBibDataBases()
		self.assertEqual(1, len(types))
		self.assertTrue(self.__lastBasename in types)
		dbs = analyzer.getBibDependencies('bst', self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertEqual({os.path.join(self.__lastDirname, "mystyle.bst")}, dbs)




if __name__ == '__main__':
    unittest.main()

