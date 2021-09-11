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
TeX parser.
'''

import re
import logging
import abc
from enum import Enum

import gettext
_T = gettext.gettext

######################################################################
##
class MathMode(Enum):
	inline = 1
	block = 2



######################################################################
##
class Parameter(object):
	'''
	Definition of a parameter for a macro.
	'''

	def __init__(self):
		'''
		Construct an expandable parameter.
		'''
		self.__expandable = True
		self.__value = None

	@property
	def expandable(self) -> bool:
		'''
		Indicates if the value of the parameter must be expanded.
		:return: True if the parameter must be expanded; False otherwise.
		:rtype: bool
		'''
		return self.__expandable

	@expandable.setter
	def expandable(self, e : bool):
		'''
		Change the flag indicating if the value of the parameter must be expanded.
		:param e: True if the parameter must be expanded; False otherwise.
		:type e: bool
		'''
		self.__expandable = e

	@property
	def value(self) -> str:
		'''
		The value of the argument.
		:return: The value of the argument.
		:rtype: str
		'''
		return self.__value

	@value.setter
	def value(self, v : str):
		'''
		Set the value of the argument.
		:param v: The value.
		:type v: str
		'''
		self.__value = v




######################################################################
##
class Parser(object):
	'''
	Public interface of a parser.
	'''
	__metaclass__ = abc.ABCMeta

	@property
	def math_mode(self) -> MathMode:
		'''
		Replies if the math mode is active.
		:return: The math mode.
		:rtype: MathMode
		'''
		raise NotImplementedError

	def putBack(self, text : str):
		'''
		Reinject a piece of text inside the parsed text in a way that it will
		be the next text to be parsed by this object.
		:param text: The text to reinject.
		:type text: str
		'''
		raise NotImplementedError

	def stop(self):
		'''
		Stop the parsing. The function parse() will stop its current loop.
		'''
		raise NotImplementedError


######################################################################
##
class Observer(object):
	'''
	Observer on events in the TeX parser.
	'''
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def text(self, parser : Parser, text : str):
		'''
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		'''
		pass

	@abc.abstractmethod
	def comment(self, parser : Parser, raw : str, comment : str) -> str:
		'''
		Invoked when comments were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param raw: Raw text of the comment to filter.
		:type raw: str
		:param comment: the comment to filter.
		:type comment: str
		:return: The text to reinject and to pass to the 'text' callback
		:rtype: str
		'''
		return None

	@abc.abstractmethod
	def openBlock(self, parser : Parser, text : str) -> str:
		'''
		Invoked when a block is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return None

	@abc.abstractmethod
	def closeBlock(self, parser : Parser, text : str) -> str:
		'''
		Invoked when a block is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return None

	@abc.abstractmethod
	def openMath(self, parser : Parser, inline : bool) -> str:
		'''
		Invoked when a math environment is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return None

	@abc.abstractmethod
	def closeMath(self, parser : Parser, inline : bool) -> str:
		'''
		Invoked when a math environment is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return None

	@abc.abstractmethod
	def findMacro(self, parser : Parser, name : str, special : bool, math : bool) -> str:
		'''
		Invoked each time a macro definition is not found in the parser data.
		:param parser: reference to the parser.
		:type parser: Parser
		:param name: Name of the macro.
		:type name: str
		:param special: Indicates if the macro is a special macro or not.
		:type special: bool
		:param math: Indicates if the math mode is active.
		:type math: bool
		:return: the definition of the macro, ie. the macro prototype. See the class documentation for an explanation about the format of the macro prototype.
		:rtype: str
		'''
		return None

	@abc.abstractmethod
	def expand(self, parser : Parser, rawtext : str, name : str, *parameter : dict) -> str:
		'''
		Expand the given macro on the given parameters.
		:param parser: reference to the parser.
		:type parser: Parser
		:param rawtext: The raw text that is the source of the expansion.
		:type rawtext: str
		:param name: Name of the macro.
		:type name: str
		:param parameter: Descriptions of the values passed to the TeX macro.
		:type parameter: dict
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		'''
		return None



######################################################################
##
class ReinjectObserver(Observer):
	'''
	Observer on events in the TeX parser that is putting back the detected text into the given content.
	'''

	def __init__(self):
		self.__content = ''

	@property
	def content(self):
		'''
		Replies the content of the TeX file.
		'''
		return self.__content

	def text(self, parser : Parser, text : str):
		'''
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		'''
		t = str(text)
		if t:
			self.__content += t

	def comment(self, parser : Parser, raw : str, comment : str) -> str:
		'''
		Invoked when comments were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param raw: Raw text of the comment to filter.
		:type raw: str
		:param comment: the comment to filter.
		:type comment: str
		:return: The text to reinject and to pass to the 'text' callback
		:rtype: str
		'''
		return "%" + re.sub('[\n\r]',  ' ',  str(comment)) + "\n"

	def openBlock(self, parser : Parser, text : str) -> str:
		'''
		Invoked when a block is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return text

	def closeBlock(self, parser : Parser, text : str) -> str:
		'''
		Invoked when a block is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		return text

	def openMath(self, parser : Parser, inline : bool) -> str:
		'''
		Invoked when a math environment is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		if inline:
			return '$'
		else:
			return '\\['

	def closeMath(self, parser : Parser, inline : bool) -> str:
		'''
		Invoked when a math environment is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		'''
		if inline:
			return '$'
		else:
			return '\\]'

	def expand(self, parser : Parser, rawtext : str, name : str, *parameter : dict) -> str:
		'''
		Expand the given macro on the given parameters.
		:param parser: reference to the parser.
		:type parser: Parser
		:param rawtext: The raw text that is the source of the expansion.
		:type rawtext: str
		:param name: Name of the macro.
		:type name: str
		:param parameter: Descriptions of the values passed to the TeX macro.
		:type parameter: dict
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		'''
		return rawtext



######################################################################
##
class TeXParser(Parser):
	'''
	Parser of a TeX file.

	= Macro Prototype =

	The specification of the macro prototypes must be a sequence (eventually empty) of:
	* {} for a mandatory parameter;
	* [d] for an optional parameter, where d is the default value given to this parameter if it is not provided inside the LaTeX code;
	* \\ for a LaTeX command name;
	* ! for indicating that the following sign ({} or []) must not be interpreted by the LaTeX parser. It must be used for verbatim output.
	* - for reading the text until the end of the current LaTeX context.
	'''

	def __init__(self):
		'''
		Constructor.
		'''
		self.__put_back_text = ''
		self.__defaultTextModeMacros = None
		self.__defaultMathModeMacros = None
		self.__defaultTextModeActiveCharacters = None
		self.__defaultMathModeActiveCharacters = None
		self.__defaultCommentCharacters = None
		self.__observer = None
		self.__filename = None
		self.__mathMode = None
		self.__textModeMacros = None
		self.__mathModeMacros = None
		self.__textModeActiveCharacters = None
		self.__mathModeActiveCharacters = None
		self.__commentCharacters = None
		self.__separators = []
		self.__stopParsing = False

	@property
	def default_text_mode_macros(self) -> dict:
		'''
		Definition of the default text-mode macros.
		:return: the macros in text mode.
		:rtype: dict[str : str]
		'''
		if self.__defaultTextModeMacros is None:
			self.__defaultTextModeMacros = {
				' '                 : '',
				'_'                 : '',
				'-'                 : '',
				'$'                 : '',
				','                 : '',
				';'                 : '',
				'%'                 : '',
				'}'                 : '',
				'{'                 : '',
				'&'                 : '',
				'\\'                : '',
				'&'                 : '',
				'#'		     		: '',
				'\''                : '{}',
				'`'                 : '{}',
				'~'                 : '{}',
				'"'                 : '{}',
				'^'                 : '{}',
				'='                 : '{}',
				'AA'                : '',
				'aa'                : '',
				'AE'                : '',
				'ae'                : '',
				'begin'             : '!{}',
				'backslash'         : '',
				'beginblock'        : '',
				'bibliographystyle' : '!{}',
				'bibliography'      : '!{}',
				'bf'                : '-',
				'bfseries'          : '-',
				'BibTeX'            : '',
				'c'                 : '{}',
				'caption'	    	: '{}',
				'centering'	    	: '-',
				'cdot'              : '',
				'cite'              : '[]{}',
				'def'               : '\\{}',
				'degree'            : '',
				'dg'                : '',
				'DH'                : '',
				'div'               : '',
				'edef'              : '\\{}',
				'Emph'              : '{}',
				'em'                : '-',
				'emph'              : '{}',
				'end'               : '!{}',
				'enditemize'        : '',
				'ensuremath'        : '{}',
				'euro'        	    : '',
				'footnotesize'      : '-',
				'gdef'              : '\\{}',
				'global'            : '',
				'guillemotleft'     : '',
				'guillemotright'    : '',
				'Huge'              : '-',
				'html'              : '!{}',
				'huge'              : '-',
				'i'                 : '',
				'include'	    	: '!{}',
				'includegraphics'   : '[]!{}',
				'indexentry'	    : '{}',
				'input'		    	: '!{}',
				'it'                : '-',
				'item'              : '[]',
				'itshape'           : '-',
				'L'		     		: '',
				'label'		    	: '{}',
				'LARGE'             : '-',
				'Large'             : '-',
				'LaTeX'             : '',
				'large'             : '-',
				'lnot'              : '',
				'mdseries'          : '-',
				'newcommand'        : '{}[][]{}',
				'newif'             : '\\',
				'normalfont'        : '-',
				'normalsize'        : '-',
				'O'                 : '',
				'o'                 : '',
				'OE'                : '',
				'oe'                : '',
				'P'                 : '',
				'pm'                : '',
				'pounds'            : '',
				'providecommand'    : '{}[][]{}',
				'ref'		    	: '{}',
				'renewcommand'      : '{}[][]{}',
				'rm'                : '-',
				'rmfamily'          : '-',
				'S'                 : '',
				'sc'                : '-',
				'scriptsize'        : '-',
				'scshape'           : '-',
				'sf'                : '-',
				'sffamily'          : '-',
				'sl'                : '-',
				'slshape'           : '-',
				'small'             : '-',
				'smash'             : '{}',
				'ss'                : '',
				'startblock'        : '',
				'startitemize'      : '',
				'string'            : '{}',
				'TeX'               : '',
				'text'              : '{}',
				'textasciicircum'   : '',
				'textasciitilde'    : '',
				'textbackslash'     : '',
				'textbf'            : '{}',
				'textbrokenbar'     : '',
				'textcent'          : '',
				'textcopyright'     : '',
				'textcurrency'      : '',
				'textexcladown'     : '',
				'textit'            : '{}',
				'textmd'            : '{}',
				'textnormal'        : '{}',
				'textonehalf'       : '',
				'textonequarter'    : '',
				'textordfeminine'   : '',
				'textordmasculine'  : '',
				'textquestiondown'  : '',
				'textregistered'    : '',
				'textrm'            : '{}',
				'textsc'            : '{}',
				'textsf'            : '{}',
				'textsl'            : '{}',
				'textthreequarters' : '',
				'texttt'            : '{}',
				'textup'            : '{}',
				'textyen'           : '',
				'times'             : '',
				'tiny'              : '-',
				'TH'                : '',
				'th'                : '',
				'tt'                : '-',
				'ttfamily'          : '-',
				'u'                 : '{}',
				'underline'         : '{}',
				'uline'             : '{}',
				'upshape'           : '{}',
				'url'               : '[]{}',
				'v'                 : '{}',
				'xdef'              : '\\{}',
				'xspace'            : '',
			}
		return self.__defaultTextModeMacros

	@property
	def default_math_mode_macros(self) -> dict:
		'''
		Definition of the default math-mode macros.
		:return: the macros in math mode.
		:rtype: dict[str : str]
		'''
		if self.__defaultMathModeMacros is None:
			self.__defaultMathModeMacros = {
				'}'					: '',
				'{'					: '',
				'&'					: '',
				'_'					: '',
				'mathmicro'			: '',
				'maththreesuperior'	: '',
				'mathtwosuperior'	: '',
				'alpha'				: "",
				'angle'				: "",
				'approx'			: "",
				'ast'				: "",
				'beta'				: "",
				'bot'				: "",
				'bullet'			: "",
				'cap'				: "",
				'cdots'				: "",
				'chi'				: "",
				'clubsuit'			: "",
				'cong'				: "",
				'cup'				: "",
				'dagger'			: "",
				'ddagger'			: "",
				'delta'				: "",
				'Delta'				: "",
				'dfrac'				: "{}{}",
				'diamondsuit'		: "",
				'div'				: "",
				'downarrow'			: "",
				'Downarrow'			: "",
				'emptyset'			: "",
				'epsilon'			: "",
				'Epsilon'			: "",
				'equiv'				: "",
				'eta'				: "",
				'exists'			: "",
				'forall'			: "",
				'frac'				: "{}{}",
				'gamma'				: "",
				'Gamma'				: "",
				'ge'				: "",
				'heartsuit'			: "",
				'Im'				: "",
				'in'				: "",
				'indexentry'		: '{}',
				'infty'				: "",
				'infinity'			: "",
				'int'				: "",
				'iota'				: "",
				'kappa'				: "",
				'lambda'			: "",
				'Lambda'			: "",
				'langle'			: "",
				'lceil'				: "",
				'ldots'				: "",
				'leftarrow'			: "",
				'Leftarrow'			: "",
				'leftrightarrow'	: "",
				'Leftrightarrow'	: "",
				'le'				: "",
				'lfloor'			: "",
				'mathbb'			: '{}',
				'mathbf'			: '{}',
				'mathit'			: '{}',
				'mathrm'			: '{}',
				'mathsf'			: '{}',
				'mathtt'  			: '{}',
				'mathnormal'		: '{}',
				'mu'				: "",
				'nabla'				: "",
				'ne'				: "",
				'neq'				: "",
				'ni'				: "",
				'not'				: "!{}",
				'nu'				: "",
				'omega'				: "",
				'Omega'				: "",
				'ominus'			: "",
				'oplus'				: "",
				'oslash'			: "",
				'Oslash'			: "",
				'otimes'			: "",
				'partial'			: "",
				'phi'				: "",
				'Phi'				: "",
				'pi'				: "",
				'Pi'				: "",
				'pm'				: "",
				'prime'				: "",
				'prod'				: "",
				'propto'			: "",
				'psi'				: "",
				'Psi'				: "",
				'rangle'			: "",
				'rceil'				: "",
				'Re'				: "",
				'rfloor'			: "",
				'rho'				: "",
				'rightarrow'		: "",
				'Rightarrow'		: "",
				'sfrac'				: "{}{}",
				'sigma'				: "",
				'Sigma'				: "",
				'sim'				: "",
				'spadesuit'			: "",
				'sqrt'				: "",
				'subseteq'			: "",
				'subset'			: "",
				'sum'				: "",
				'supseteq'			: "",
				'supset'			: "",
				'surd'				: "",
				'tau'				: "",
				'theta'				: "",
				'Theta'				: "",
				'times'				: "",
				'to'				: "",
				'uparrow'			: "",
				'Uparrow'			: "",
				'upsilon'			: "",
				'Upsilon'			: "",
				'varpi'				: "",
				'vee'				: "",
				'wedge'				: "",
				'wp'				: "",
				'xi'				: "",
				'Xi'				: "",
				'xspace'			: "",
				'zeta'				: "",
			}
		return self.__defaultMathModeMacros

	@property
	def default_text_mode_active_characters(self) -> dict:
		'''
		Definitions of the default active characters in text mode.
		:return: the active characters in text mode.
		:rtype: dict[str : str]
		'''
		if self.__defaultTextModeActiveCharacters is None:
			self.__defaultTextModeActiveCharacters = {
			}
		return self.__defaultTextModeActiveCharacters

	@property
	def default_math_mode_active_characters(self) -> dict:
		'''
		Definitions of the default active characters in math mode.
		:return: the active characters in math mode.
		:rtype: dict[str : str]
		'''
		if self.__defaultMathModeActiveCharacters is None:
			self.__defaultMathModeActiveCharacters = {
				'_'		: "{}",
				'^'		: "{}",
			}
		return self.__defaultMathModeActiveCharacters

	@property
	def default_comment_characters(self) -> list:
		'''
		Definition of the default characters for comments.
		:return: the list of comment characters.
		:rtype: list[str]
		'''
		if self.__defaultCommentCharacters is None:
			self.__defaultCommentCharacters = [
				'%',
			]
		return self.__defaultCommentCharacters

	@property
	def observer(self) -> Observer:
		'''
		Return the observer on the internal parser events.
		:return: The observer.
		:rtype: Observer
		'''
		return self.__observer

	@observer.setter
	def observer(self, observer : Observer):
		'''
		Set an observer on the internal parser events.
		:param observer: The observer.
		:type observer: Observer
		'''
		self.__observer = observer

	@property
	def filename(self) -> str:
		return self.__filename

	@filename.setter
	def filename(self, n : str):
		self.__filename = n

	@property
	def math_mode(self) -> MathMode:
		'''
		Replies if the math mode is active.
		:return: The math mode.
		:rtype: MathMode
		'''
		return self.__mathMode

	@math_mode.setter
	def math_mode(self, mode : MathMode):
		'''
		Set if the math mode is active.
		:param mode: The math mode or None if the parser must be in text mode.
		:type mode: MathMode
		'''
		self.__mathMode = mode

	@property
	def text_mode_macros(self) -> dict:
		'''
		List of the macros in text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are macro names; values are macro prototype.
		:rtype: dict[str : str]
		'''
		if self.__textModeMacros is None:
			self.__textModeMacros = {}
			self.__textModeMacros.update(self.default_text_mode_macros)
		return self.__textModeMacros

	def add_text_mode_macro(self, name : str, prototype : str):
		'''
		Add a macro for the text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param name: The name of the macro.
		:type name: str
		:param prototype: The prototype of the macro.
		:type prototype: str
		'''
		self.text_mode_macros
		self.__textModeMacros[name] = prototype

	@property
	def math_mode_macros(self) -> dict:
		'''
		List of the macros in math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are macro names; values are macro prototype.
		:rtype: dict[str : str]
		'''
		if self.__mathModeMacros is None:
			self.__mathModeMacros = {}
			self.__mathModeMacros.update(self.default_math_mode_macros)
		return self.__mathModeMacros

	def add_math_mode_macro(self, name : str, prototype : str):
		'''
		Add a macro for the math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param name: The name of the macro.
		:type name: str
		:param prototype: The prototype of the macro.
		:type prototype: str
		'''
		self.math_mode_macros
		self.__mathModeMacros[name] = prototype

	@property
	def text_mode_active_characters(self) -> dict:
		'''
		List of the active characters in text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are active characters; values are macro prototype.
		:rtype: dict[str : str]
		'''
		if self.__textModeActiveCharacters is None:
			self.__textModeActiveCharacters = {}
			self.__textModeActiveCharacters.update(self.default_text_mode_active_characters)
		return self.__textModeActiveCharacters

	def add_text_mode_active_character(self, character: str, prototype : str):
		'''
		Add an active character for the text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param character: The active character.
		:type character: str
		:param prototype: The prototype of the active character.
		:type prototype: str
		'''
		self.text_mode_active_characters
		self.__textModeActiveCharacters[character] = prototype
		self.separators = None

	@property
	def math_mode_active_characters(self) -> dict:
		'''
		List of the active characters in math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are active characters; values are macro prototype.
		:rtype: dict[str : str]
		'''
		if self.__mathModeActiveCharacters is None:
			self.__mathModeActiveCharacters = {}
			self.__mathModeActiveCharacters.update(self.default_math_mode_active_characters)
		return self.__mathModeActiveCharacters

	def add_math_mode_active_character(self, character : str, prototype : str):
		'''
		Add an active character for the math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param character: The active character.
		:type character: str
		:param prototype: The prototype of the active character.
		:type prototype: str
		'''
		self.math_mode_active_characters
		self.__mathModeActiveCharacters[character] = prototype
		self.separators = None

	@property
	def comment_characters(self) -> list:
		'''
		List of the comment characters.
		:return: the list of characters.
		:rtype: list[str]
		'''
		if self.__commentCharacters is None:
			self.__commentCharacters = []
			self.__commentCharacters.extend(self.default_comment_characters)
		return self.__commentCharacters

	@property
	def separators(self) -> list:
		'''
		List of the separators used by the parser.
		:return: the list of the separators.
		:rtype: list[str]
		'''
		return self.__separators

	@separators.setter
	def separators(self, s : list) -> list:
		'''
		Change of the separators used by the parser.
		:param s: the list of the separators.
		:type s: list[str]
		'''
		self.__separators = s or []

	def parse(self, text : str, lineno : int = 1):
		'''
		Parse the specified string and invoke the listeners on the TeX tokens.
		:param text: The string to parse.
		:type text: str
		:param lineno: The line number where the text can be found (default: 1).
		:type lineno: int
		'''
		if lineno < 1:
			lineno = 1
		# Search the first separator
		eaten, sep, text, crcount = self.__eatToSeparator(text)

		self.__stopParsing = False
		self.__mathMode = None

		while sep:

			# Stop parsing
			if self.__stopParsing:
				return None

			lineno += crcount

			# Parse the already eaten string
			if (eaten and self.observer is not None):
				self.observer.text(self, eaten)

			if sep == '{':
				c = self.observer.openBlock(self, sep)
				if c is not None:
					self.observer.text(self, c)
			elif sep == '}':
				c = self.observer.closeBlock(self, sep)
				if c is not None:
					self.observer.text(self, c)
			elif sep == '\\':
				c, text = self.__parseCmd(text, lineno, '\\')
				if (c is not None):
					self.observer.text(self, c)
			elif sep == '$':
				# Math mode
				if self.math_mode is None:
					c = self.observer.openMath(self, True)
					self.math_mode = MathMode.inline
					if c is not None:
						self.observer.text(self, c)
				elif self.math_mode == MathMode.inline:
					c = self.observer.closeMath(self, True)
					self.math_mode = None
					if c is not None:
						self.observer.text(self, c)
				else:
					logging.warning(
						_T("you try to close with a '\$' a mathematical mode opened with '\\[' (%s:%d)") % (self.filename, lineno))
			elif sep in self.comment_characters:
				# Comment
				r = re.match('^(.*?)[\n\r](.*)$', text, re.DOTALL)
				if r: # Not a comment until the end-of-file
					commentText = r.group(1)
					text = r.group(2)
				else:
					commentText = text
					text = ''
				
				c = self.observer.comment(self, sep + commentText, commentText.strip())
				if (c is not None):
					self.observer.text(self, c)
			else:
				isText = sep in self.text_mode_active_characters
				isMath = sep in self.math_mode_active_characters
				if isText or isMath:
					if self.math_mode is not None:
						if not isMath:
							logging.warning(
								_T("you cannot use in text mode the active character '%s', which is defined in math mode (%s:%d)") % (sep, self.filename, lineno))
							if (sep is not None):
								self.observer.text(self, sep)
						else:
							c, text = self.__parseActiveChar(sep + text, lineno)
							if c is not None:
								self.observer.text(self, c)
					elif (not isText):
						logging.warning(
							_T("you cannot use in math mode the active character '%s', which is defined in text mode (%s:%d)") % (sep, self.filename, lineno))
						if sep is not None:
							self.observer.text(self, sep)
					else:
						c, text = self.__parseActiveChar(sep + text, lineno)
						if c is not None:
							self.observer.text(self, c)
				else: # Unknow separator, treat as text
					if sep is not None:
						self.observer.text(self,sep)

			# Search the next separator
			eaten, sep, text, crcount = self.__eatToSeparator(text)

		if text is not None:
			self.observer.text(self, text)

		return None

	def putBack(self, text : str):
		'''
		Reinject a piece of text inside the parsed text in a way that it will
		be the next text to be parsed by this object.
		:param text: The text to reinject.
		:type text: str
		'''
		if text:
			self.__put_back_text = text

	def stop(self):
		'''
		Stop the parsing. The function parse() will stop its current loop.
		'''
		self.__stopParsing = True

	def __eatToSeparator(self, text : str, *seps : str) -> tuple:
		'''
		Eats the specified text until the first separator.
		:param text: The text to eat.
		:type text: str
		:param seps: The list of additional separators to consider.
		:type seps: str
		:return: the tuple (eaten text, detected separator, not eatend text, number of CR)
		:rtype: tuple
		'''
		if text is None:
			text = ''
		if seps is None:
			seps = ()

		if self.__put_back_text:
			text = self.__put_back_text + text
			self.__put_back_text = None

		separators = set()
		stdSeparators = self.separators
		if stdSeparators:
			separators.update(stdSeparators)
		else:
			separators.update(self.__buildSeparators())

		separators.update(seps)

		ret1 = ''
		sep = None
		after = ''
		crcount = 0

		regex = '^(.*?)(\n|\r'
		for s in separators:
			regex += '|'
			regex += re.escape(s)
		regex += ')(.*)$'
		r = re.match(regex, text, re.DOTALL)
		while r:
			before = r.group(1)
			sep = r.group(2)
			text = r.group(3)
			ret1 += before
			if sep != "\n":
				return (ret1, sep, text, crcount)
			ret1 += "\n"
			crcount += 1
			r = re.match(regex, text, re.DOTALL)
	
		if text:
			ret1 += text
			sep = None
			after = ''

		return (ret1, sep, after, crcount)

	def __buildSeparators(self):
		'''
		Build a list of separators.
		:return: The list of separators.
		:rtype: list[str]
		'''
		sepSet = set()
		sepSet.update(self.comment_characters)
		sepSet.update(self.text_mode_active_characters.keys())
		sepSet.update(self.math_mode_active_characters.keys())
		sepSet.update( { '{', '}', '\\$', '\\\\' } )
		seps = ''
		for v in sepSet:
			seps += v
		self.separators = seps
		return seps

	def __parseCmd(self, text : str, lineno : int, prefix : str = '') -> str:
		'''
		Parse a TeX command.
		:param text: The text, which follows the backslash, to scan.
		:type text: str
		:param lineno: The line number.
		:param int:
		:param prefix: A prefix merged to the command name. Use carefully.
		:type prefix: str
		:return: the tuple (the result of the expand of the macro, the rest of the tex text after the macro).
		:rtype: str
		'''
		expandTo = ''

		r = re.match('^\\[(.*)', text, re.DOTALL)
		if r: # Starts multi-line math mode
			text = r.group(1)
			expandTo = self.observer.openMath(self, False)
			self.math_mode = MathMode.block
		else:
			r = re.match('^\\](.*)', text, re.DOTALL)
			if r: # Stop multi-line math mode
				text = r.group(1)
				expandTo = self.observer.closeMath(self, False)
				self.math_mode = None
			else:
				r = re.match('^((?:[a-zA-Z]+\\*?)|.)(.*)', text, re.DOTALL)
				if r: # default LaTeX command
					cmdname = r.group(1)
					text = r.group(2)
					trans = self.__searchCmdTrans(cmdname, lineno, (prefix != "\\") )
					if not trans:
						trans = ''
					expandTo, text = self.__runCmd(prefix + cmdname, trans, text, lineno)
				else:
					self.warning(_T("invalid syntax for the TeX command: %s (lineno: %d)"), prefix + text, lineno)
		return (expandTo, text)

	def __parseActiveChar(self, text : str, lineno : int) -> str:
		'''
		Parse a TeX active character.
		:param text: The text, with the active char, to scan.
		:type text: str
		:param lineno: Line number.
		:type lineno: int
		:return: the rest of the tex text, after the active character.
		:rtype: str
		'''
		expandTo = ''

		r = re.match(r'^(.)(.*)', text, re.DOTALL)
		if r: # default LaTeX command
			activeChar = r.group(1)
			text = r.group(2)
			trans = self.__searchCmdTrans(activeChar, lineno, True)
			if not trans:
				trans = ''
			expandTo, text = self.__runCmd(activeChar, trans, text, lineno)
		else:
			self.warning(_T("invalid syntax for the TeX active character: %s (lineno: %d)"), text, lineno)
			expandTo = text[0:1] if len(text) > 0 else ''
			text = text[1:] if len(text) > 0 else ''

		return (expandTo, text)

	def __searchCmdTrans(self, name : str, lineno : int, special : bool = False):
		'''
		Replies the macro definition that corresponds to
		the specified TeX command.
		:param name: The name of the TeX command to search.
		:type name: str
		:param lineno: Line number.
		:type lineno: int
		:param special: Indicates if the searched command has a special purpose (example: _ in math mode).
		:type: bool
		'''
		found_math = False
		found_text = False
		math = None
		text = None

		if name:

			if special:
				if name in self.math_mode_active_characters:
					found_math = True
					math = self.math_mode_active_characters[name]
				if name in self.text_mode_active_characters:
					found_text = True
					text = self.text_mode_active_characters[name]
			else:
				if name in self.math_mode_macros:
					found_math = True
					math = self.math_mode_macros[name]
				if name in self.text_mode_macros:
					found_text = True
					text = self.text_mode_macros[name]

			if (not found_text and not found_math):
				proto = self.observer.findMacro(self, name, special, (self.math_mode is not None))
				if proto:
					if (self.math_mode is not None):
						found_math = True
						math = proto
					else:
						found_text = True
						text = proto

		logging.debug(_T("Found parameter definition for '%s': math=%s; text=%s (%s:%d)") % (name, (math or '<undef>'), (text or '<undef>'), self.filename, lineno))

		if found_math or found_text:
			if self.math_mode is not None:
				if not found_math:
					self.warning(_T("the command %s%s was not defined for math-mode, assumes to use the text-mode version instead (lineno: %d)"),
							( '' if (special) else '\\' ), name, lineno)
					return text
				else:
					return math
			elif not found_text:
				self.warning(_T("the command %s%s was not defined for text-mode, assumes to use the math-mode version instead (lineno: %d)"),
						( '' if (special) else '\\' ), name, lineno)
				return math
			else:
				return text

		return None

	def __runCmd(self, name : str, trans : str, text : str, lineno : int):
		'''
		Execute the specified macro on the specified tex string.
		:param name: The name of the TeX macro.
		:type name: str
		:param trans: The definition for the macro.
		:type trans: str
		:param text: The text from which some data must be extracted to treat the macro.
		:type text: str
		:param lineno: The line number where the text starts.
		:param lineno: int
		'''
		expandTo = ''
		if trans:
			# This macro has params
			logging.debug(_T("Expanding '%s' (%s:%d)") % (name, self.filename, lineno))
			text, params, rawparams = self.__eatCmdParameters(trans, text, name, lineno)
			# Apply the macro
			expandTo = self.observer.expand(self, name + rawparams, name, *params)
		else:
			# No param, put the string inside the output stream
			logging.debug(_T("Expanding '%s' (%s:%d)") % (name, self.filename, lineno))
			expandTo = self.observer.expand(self, name, name)
		return (expandTo, text)

	def __eatCmdParameters(self, p_params : str, text : str, macro : str, lineno : int) -> tuple:
		'''
		Eat the parameters for a macro.
		:param p_params: The description of the parameters to eat.
		:type p_params: str
		:param text: The text from which some data must be extracted.
		:type text: str
		:param macro: The name of the macro for which parameters must be extracted.
		:type macro: str
		:param lineno: The line number.
		:type lineno: int
		:return: The tuple (the rest of the text, the array of parameters, the raw representation of the parameters)
		:rtype: tuple
		'''
		params = []
		rawparams = ''
		logging.debug(_T("Macro prototype of '%s': %s (%s:%d)") % (macro, p_params, self.filename, lineno))
		for p in re.findall(r'((?:\!?\{\})|(?:\!?\[[^\]]*\])|-|\\)', p_params, re.DOTALL):
			# Eats no significant white spaces
			r = re.match(r'^(\!?)\{\}', p, re.DOTALL)
			if r: # Eates a mandatory parameter
				optional = r.group(1) or ''
				prem = text[0:1]
				text = text[1:]
				if prem == '{':
					context, text = self.__eatContext(text, '\\}')
					params.append({
						'eval' : (optional != '!'),
						'text' : context })
					rawparams += "{" + context + "}"
				elif prem == '\\':
					if optional != '!':
						# The following macro is expandable
						c, text = self.__parseCmd(text, lineno, '\\')
						params.append({
							'eval' : True,
							'text' : c })
						rawparams += c
					else:
						# The following macro is not expandable
						r = re.match(r'^((?:[a-zA-Z]+\*?)|.)(.*)$', text, re.DOTALL)
						c = r.group(1)
						text = r.group(2)
						params.append({
							'eval' : False,
							'text' : c })
						rawparams += "\\" + c
				else:
					params.append({
						'eval' : (optional != '!'),
						'text' : prem })
					rawparams += prem
			else:
				r = re.match(r'^(\!?)\[([^\]]*)\]', p, re.DOTALL)
				if r: # Eates an optional parameter
					optional = r.group(1) or ''
					default_val = r.group(2) or ''
					prem = text[0:1]
					if prem == '[':
						context, text = self.__eatContext(text[1:], ']')
						params.append({
								'eval' : (optional != '!'),
								'text' : context })
						rawparams += "[" + context + "]"
					else:
						params.append({
								'eval' : (optional != '!'),
								'text' : default_val })
				elif p == '\\': # Eates a TeX command name
					r = re.match(r'^\\((?:[a-zA-Z]+\*?)|.)(.*)$', text, re.DOTALL)
					if r:
						n = r.group(1)
						text = r.group(2)
						params.append({
								'eval' : True,
								'text' : n })
						rawparams += "\\" +n
					else:
						msg = text[0:50]
						msg = re.sub('[\n\r]', '\\n', msg, 0, re.DOTALL)
						msg = msg.replace("\t", "\\t")
						logging.warning(_T("expected a TeX macro for expanding the macro %s, here: '%s' (%s:%d)") % (macro, msg, self.filename, lineno))
						params.append({
								'eval' : 1,
								'text' : '' })
						rawparams += "\\"
				elif p == '-': # Eates until the end of the current context
					context, text = self.__eatContext(text, '\\}')
					params.append({
							'eval' : True,
							'text' : context })
					rawparams += context
				else:
					raise Exception[_T("unable to recognize the following argument specification: %s") % p]
		return (text, params, rawparams)


	def __eatContext(self, text : str, enddelim : str):
		'''
		Eat the current context.
		:param text: The text from which some data must be extracted.
		:type text: str
		:param enddelim: The ending separator.
		:type enddelim: str
		'''
		context = ''
		contextlevel = 0

		# Search the first separator
		eaten, sep, text, crcount = self.__eatToSeparator(text, enddelim)
		while sep:

			if sep == '{': # open a context
				contextlevel += 1
				eaten += sep
			elif sep == '}': # close a context
				if contextlevel <= 0:
					return (context + eaten, text)
				eaten += sep
				contextlevel -= 1
			elif sep == '\\':
				r = re.match(r'^([a-zA-Z]+\*?|.)(.*)$', text, re.DOTALL)
				eaten += "\\" + r.group(1)
				text = r.group(2)
			elif (contextlevel <= 0) and (re.match(re.escape(enddelim), sep, re.DOTALL)): # The closing delemiter was found
				return (context + eaten, text)
			else: # Unknow separator, treat as text
				eaten += sep

			# Translate the text before the separator
			context += eaten

			# Search the next separator
			eaten, sep, text, crcount = self.__eatToSeparator(text, enddelim)

		return (context + eaten, text)

