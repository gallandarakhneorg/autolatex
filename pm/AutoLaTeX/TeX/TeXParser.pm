# autolatex - TeXParser.pm
# Copyright (C) 1998-13  Stephane Galland <galland@arakhne.org>
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

=pod

=head1 NAME

AutoLaTeX::TeX::TeXParser - A parser from TeX.

=head1 SYNOPSYS

use AutoLaTeX::TeX::TeXParser ;

my $gen = AutoLaTeX::TeX::TeXParser->new( filename ) ;

=head1 DESCRIPTION

AutoLaTeX::TeX::TeXParser is a Perl module, which parse a
TeX file.

=head1 GETTING STARTED

=head2 Initialization

To create a parser, say something like this:

    use AutoLaTeX::TeX::TeXParser;

    my $listener = { ... };
    my $parser = AutoLaTeX::TeX::TeXParser->new( 'toto.tex', $listener ) ;

...or something similar. Acceptable parameters to the constructor are:

=over

=item * filename (string)

is the filename under parsing.

=item * listener (optional associative array)

is the listener, which will be invoked each time a statement in the TeX file is detected.
A listener is an associative array in which values are subs to run. The supported
keys are:

=over

=item * 'outputString': is invoked when characters must be filtered. I<Parameters>: reference to the listener, reference to the parser, and the text to filter. I<Returns>: nothing.

=item * 'filterComments': is invoked when comments must be filtered. I<Parameters>: reference to the listener, reference to the parser, and the text to filter. I<Returns>: the filtered comments.

=item * 'openBlock': is invoked when a block was opened. I<Parameters>: reference to the listener, and the reference to the parser. I<Returns>: nothing.

=item * 'closeBlock': is invoked when a block was closed. I<Parameters>: reference to the listener, and the reference to the parser. I<Returns>: nothing.

=item * 'inlineMathStart': the inline math mode is starting. I<Parameters>: reference to the listener, reference to the parser. I<Returns> the result of the expand of the symbol.

=item * 'multilineMathStart': the multiline math mode is starting. I<Parameters>: reference to the listener, reference to the parser. I<Returns>: the result of the expand of the symbol.

=item * 'inlineMathStop': the inline math mode is finished. I<Parameters>: reference to the listener, reference to the parser. I<Returns>: the result of the expand of the symbol.

=item * 'multilineMathStop': the multiline math mode is finished. I<Parameters>: reference to the listener, reference to the parser. I<Returns>: the result of the expand of the symbol.

=item * 'discoverMacroDefinition': is invoked each time a macro definition is not found in the parser data. I<Parameters>: reference to the listener, reference to the parser, the name of the macro to search for, a boolean value that is indicating if the macro is a special macro or not, a boolean flag indicating if the math mode is active. I<Returns>: the definition of the macro prototype.

=item * 'expandMacro': a macro is expandable. I<Parameters>: reference to the listener, reference to the parser, the name of the macro to expand, and the rest of the parameters are the descriptions of the values passed to the TeX macro. Each of the descriptions is an associative array with the keys 'eval' and 'text'. The 'eval' key indicates if the value of the parameter must be expanded in turn (if true), or used verbatim (if false). The 'text' is the value of the parameter. I<Returns>: the result of the expand of the macro.

=back

THe invoked subs may reply a text to build the text replied by the parser.

=back

=head1 METHOD DESCRIPTIONS

This section contains only the methods in TeXParser.pm itself.

=over

=cut

package AutoLaTeX::TeX::TeXParser;

@ISA = ('Exporter');
@EXPORT = qw();
@EXPORT_OK = qw( );

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Exporter;
use Carp ;

use AutoLaTeX::Core::Util ;
use AutoLaTeX::Core::Locale ;

#------------------------------------------------------
#
# Global vars
#
#------------------------------------------------------

# Version number of the parser
my $VERSION = "4.0" ;

# Definition of the default text-mode macros
my %TEX_DEFAULT_TEXT_MODE_MACROS = (
	' '                 => '',
	'_'                 => '',
	'-'                 => '',
	'$'                 => '',
	','                 => '',
	';'                 => '',
	'%'                 => '',
	'}'                 => '',
	'{'                 => '',
	'&'                 => '',
	'\\'                => '',
	'&'                 => '',
	'#'		     => '',
	'\''                => '{}',
	'`'                 => '{}',
	'~'                 => '{}',
	'"'                 => '{}',
	'^'                 => '{}',
	'='                 => '{}',
	'AA'                => '',
	'aa'                => '',
	'AE'                => '',
	'ae'                => '',
	'begin'             => '!{}',
	'backslash'         => '',
	'beginblock'        => '',
	'bibliographystyle' => '!{}',
	'bibliography'      => '!{}',
	'bf'                => '-',
	'bfseries'          => '-',
	'BibTeX'            => '',
	'c'                 => '{}',
	'caption'	    => '{}',
	'centering'	    => '-',
	'cdot'              => '',
	'cite'              => '[]{}',
	'def'               => '\\{}',
	'degree'            => '',
	'dg'                => '',
	'DH'                => '',
	'div'               => '',
	'edef'              => '\\{}',
	'Emph'              => '{}',
	'em'                => '-',
	'emph'              => '{}',
	'end'               => '!{}',
	'enditemize'        => '',
	'ensuremath'        => '{}',
	'euro'        	     => '',
	'footnotesize'      => '-',
	'gdef'              => '\\{}',
	'global'            => '',
	'guillemotleft'     => '',
	'guillemotright'    => '',
	'Huge'              => '-',
	'html'              => '!{}',
	'huge'              => '-',
	'i'                 => '',
	'include'	    => '!{}',
	'includegraphics'   => '[]!{}',
	'indexentry'	    => '{}',
	'input'		    => '!{}',
	'it'                => '-',
	'item'              => '[]',
	'itshape'           => '-',
	'L'		     => '',
	'label'		    => '{}',
	'LARGE'             => '-',
	'Large'             => '-',
	'LaTeX'             => '',
	'large'             => '-',
	'lnot'              => '',
	'mdseries'          => '-',
	'newcommand'        => '{}[][]{}',
	'newif'             => '\\',
	'normalfont'        => '-',
	'normalsize'        => '-',
	'O'                 => '',
	'o'                 => '',
	'OE'                => '',
	'oe'                => '',
	'P'                 => '',
	'pm'                => '',
	'pounds'            => '',
	'providecommand'    => '{}[][]{}',
	'ref'		    => '{}',
	'renewcommand'      => '{}[][]{}',
	'rm'                => '-',
	'rmfamily'          => '-',
	'S'                 => '',
	'sc'                => '-',
	'scriptsize'        => '-',
	'scshape'           => '-',
	'sf'                => '-',
	'sffamily'          => '-',
	'sl'                => '-',
	'slshape'           => '-',
	'small'             => '-',
	'smash'             => '{}',
	'ss'                => '',
	'startblock'        => '',
	'startitemize'      => '',
	'string'            => '{}',
	'TeX'               => '',
	'text'              => '{}',
	'textasciicircum'   => '',
	'textasciitilde'    => '',
	'textbackslash'     => '',
	'textbf'            => '{}',
	'textbrokenbar'     => '',
	'textcent'          => '',
	'textcopyright'     => '',
	'textcurrency'      => '',
	'textexcladown'     => '',
	'textit'            => '{}',
	'textmd'            => '{}',
	'textnormal'        => '{}',
	'textonehalf'       => '',
	'textonequarter'    => '',
	'textordfeminine'   => '',
	'textordmasculine'  => '',
	'textquestiondown'  => '',
	'textregistered'    => '',
	'textrm'            => '{}',
	'textsc'            => '{}',
	'textsf'            => '{}',
	'textsl'            => '{}',
	'textthreequarters' => '',
	'texttt'            => '{}',
	'textup'            => '{}',
	'textyen'           => '',
	'times'             => '',
	'tiny'              => '-',
	'TH'                => '',
	'th'                => '',
	'tt'                => '-',
	'ttfamily'          => '-',
	'u'                 => '{}',
	'underline'         => '{}',
	'uline'             => '{}',
	'upshape'           => '{}',
	'url'               => '[]{}',
	'v'                 => '{}',
	'xdef'              => '\\{}',
	'xspace'            => '',
);

# Definition of the default math-mode macros
my %TEX_DEFAULT_MATH_MODE_MACROS = (
	'}'				=> '',
	'{'				=> '',
	'&'				=> '',
	'_'				=> '',
	'mathmicro'			=> '',
	'maththreesuperior'		=> '',
	'mathtwosuperior'		=> '',
	'alpha'				=> "",
	'angle'				=> "",
	'approx'			=> "",
	'ast'				=> "",
	'beta'				=> "",
	'bot'				=> "",
	'bullet'			=> "",
	'cap'				=> "",
	'cdots'				=> "",
	'chi'				=> "",
	'clubsuit'			=> "",
	'cong'				=> "",
	'cup'				=> "",
	'dagger'			=> "",
	'ddagger'			=> "",
	'delta'				=> "",
	'Delta'				=> "",
	'dfrac'				=> "{}{}",
	'diamondsuit'			=> "",
	'div'				=> "",
	'downarrow'			=> "",
	'Downarrow'			=> "",
	'emptyset'			=> "",
	'epsilon'			=> "",
	'Epsilon'			=> "",
	'equiv'				=> "",
	'eta'				=> "",
	'exists'			=> "",
	'forall'			=> "",
	'frac'				=> "{}{}",
	'gamma'				=> "",
	'Gamma'				=> "",,
	'ge'				=> "",,
	'heartsuit'			=> "",,
	'Im'				=> "",
	'in'				=> "",
	'indexentry'			=> '{}',
	'infty'				=> "",
	'infinity'			=> "",
	'int'				=> "",
	'iota'				=> "",
	'kappa'				=> "",
	'lambda'			=> "",
	'Lambda'			=> "",
	'langle'			=> "",
	'lceil'				=> "",
	'ldots'				=> "",
	'leftarrow'			=> "",
	'Leftarrow'			=> "",
	'leftrightarrow'		=> "",
	'Leftrightarrow'		=> "",
	'le'				=> "",
	'lfloor'			=> "",
	'mathbb'			=> '{}',
	'mathbf'			=> '{}',
	'mathit'			=> '{}',
	'mathrm'			=> '{}',
	'mathsf'			=> '{}',
	'mathtt'  			=> '{}',
	'mathnormal'			=> '{}',
	'mu'				=> "",
	'nabla'				=> "",
	'ne'				=> "",
	'neq'				=> "",
	'ni'				=> "",
	'not'				=> "!{}",
	'nu'				=> "",
	'omega'				=> "",
	'Omega'				=> "",
	'ominus'			=> "",
	'oplus'				=> "",
	'oslash'			=> "",
	'Oslash'			=> "",
	'otimes'			=> "",
	'partial'			=> "",
	'phi'				=> "",
	'Phi'				=> "",
	'pi'				=> "",
	'Pi'				=> "",
	'pm'				=> "",
	'prime'				=> "",
	'prod'				=> "",
	'propto'			=> "",
	'psi'				=> "",
	'Psi'				=> "",
	'rangle'			=> "",
	'rceil'				=> "",
	'Re'				=> "",
	'rfloor'			=> "",
	'rho'				=> "",
	'rightarrow'			=> "",
	'Rightarrow'			=> "",
	'sfrac'				=> "{}{}",
	'sigma'				=> "",
	'Sigma'				=> "",
	'sim'				=> "",
	'spadesuit'			=> "",
	'sqrt'				=> "",
	'subseteq'			=> "",
	'subset'			=> "",
	'sum'				=> "",
	'supseteq'			=> "",
	'supset'			=> "",
	'surd'				=> "",
	'tau'				=> "",
	'theta'				=> "",
	'Theta'				=> "",
	'times'				=> "",
	'to'				=> "",
	'uparrow'			=> "",
	'Uparrow'			=> "",
	'upsilon'			=> "",
	'Upsilon'			=> "",
	'varpi'				=> "",
	'vee'				=> "",
	'wedge'				=> "",
	'wp'				=> "",
	'xi'				=> "",
	'Xi'				=> "",
	'xspace'			=> "",
	'zeta'				=> "",
);

# Definition of the default text-mode active characters
my %TEX_DEFAULT_TEXT_MODE_ACTIVE_CHARACTERS = (
);

# Definition of the default math-mode active characters
my %TEX_DEFAULT_MATH_MODE_ACTIVE_CHARACTERS = (
	'_'		=> "{}",
	'^'		=> "{}",
);

# Definition of the default characters for comments
my @TEX_DEFAULT_COMMENT_CHARACTERS = (
	'%',
);

#------------------------------------------------------
#
# Inner methods
#
#------------------------------------------------------

# Print a warning.
sub warning($$) : method {
	my $self = shift;
	my $msg = shift;
	my $lineno = shift;
	if ($lineno>0) {
		printWarn($msg.' ('.$self->{'FILENAME'}.':'.$lineno.')');
	}
	else {
		printWarn($msg.' ('.$self->{'FILENAME'}.')');
	}
}

# Test is the first parameter is not defined or an empty string.
sub __isset($) {
	my $v = shift;
	return 0 unless defined($v);
	return "$v" ne '';
}

# Notifies the listener
# $_[0]: name of the listener to call
# $_[1]: default value to reply when no listener to invoke, or the listener replied undef.
# @_: parameters to pass to the listener, when it was found.
# $_: depends on the semantic of the callback.
sub callListener($$@) : method {
	my $self = shift;
	my $callback = shift;
	my $defaultValue = shift;
	my $func = $self->{'PARSER_LISTENER'}{"$callback"};
	my $ret = undef;
	if ($func) {
		$ret = $func->($self->{'PARSER_LISTENER'}, $self, @_);
	}
	if (!defined($ret)) {
		$ret = $defaultValue;
	}
	return $ret;
}

#------------------------------------------------------
#
# Constructor
#
#------------------------------------------------------

sub new($$) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $parent = ref($proto) && $proto ;

	my $self ;
	if ( $parent ) {
		%{$self} = %{$parent} ;
	}
	else {
		my %cmt = map { $_ => 1 } @TEX_DEFAULT_COMMENT_CHARACTERS;
		$self = {
			'FILENAME' => $_[0] || '',
			'MATH_MODE' => 0,
			'PARSER_LISTENER' => $_[1] || {},
			'TEXT_MODE_MACROS' => { },
			'MATH_MODE_MACROS' => { },
			'TEXT_MODE_ACTIVE_CHARACTERS' => { },
			'MATH_MODE_ACTIVE_CHARACTERS' => { },
			'COMMENT_CHARACTERS' => \%cmt,
			'SEPARATORS' => '',
		};
	}
	bless( $self, $class );
	return $self;
}

#------------------------------------------------------
#
# Parsing API
#
#------------------------------------------------------

=pod

=item * parse()

Parse the specified string.
Takes 3 args:

=over

=item * text (string)

is the text to parse

=item * lineno (optional integer)

is the line number where the text can be found

=back

I<Returns:> Nothing.

=cut
sub parse($;$) : method {
	my $self = shift ;
	my $text = shift || '';
	my $lineno = shift || 0 ;

	$lineno = 1 if ($lineno<1);

	# Search the first separator
	my ($eaten,$sep,$tex,$crcount) = $self->eat_to_separator($text) ;

	while ($sep) {

		$lineno += $crcount;

		# Parse the already eaten string
		if (__isset($eaten)) {
			$self->callListener( 'outputString', undef, $eaten ) ;
		}

		if ($sep eq '{' ) {
			my $c = $self->callListener( 'openBlock', '{' ) ;
			if (__isset($c)) {
				$self->callListener( 'outputString', undef, $c ) ;
			}
		}
		elsif ($sep eq '}' ) {
			my $c = $self->callListener( 'closeBlock', '}' ) ;
			if (__isset($c)) {
				$self->callListener( 'outputString', undef, $c ) ;
			}
		}
		elsif ( $sep eq '\\' ) {
			(my $c, $tex) = $self->parse_cmd($tex, $lineno, '\\') ;
			if (__isset($c)) {
				$self->callListener( 'outputString', undef, $c ) ;
			}
		}
		elsif ( $sep eq '$' ) {
			# Math mode
			my $c = '';			
			if ( ! $self->is_math_mode() ) {
				$c = $self->start_math_mode(1) ;
			}
			elsif ( $self->is_inline_math_mode() ) {
				$c = $self->stop_math_mode(1) ;
			}
			else {
				$self->warning(
					_T("you try to close with a '\$' a mathematical mode opened with '\\['"),
					$lineno) ;
			}
			if (__isset($c)) {
				$self->callListener( 'outputString', undef, $c ) ;
			}
		}
		elsif (exists $self->{'COMMENT_CHARACTERS'}{$sep}) {
			# Comment
			$tex =~ s/^(.*?[\n\r])//s;
			my $c = $self->callListener( 'filterComments', "%".$1, $1 ) ;
			if (__isset($c)) {
				$self->callListener( 'outputString', undef, $c ) ;
			}
		}
		else {
			my $isText = (exists $self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{$sep});
			my $isMath = (exists $self->{'MATH_MODE_ACTIVE_CHARACTERS'}{$sep});
			if ($isText || $isMath) {
				if ($self->is_math_mode()) {
					if (!$isMath) {
						$self->warning(
							locGet(_T("you cannot use in text mode the active character '{}', which is defined in math mode"), $sep),
							$lineno) ;
						if (__isset($sep)) {
							$self->callListener( 'outputString', undef, $sep ) ;
						}
					}
					else {
						(my $c,$tex) = $self->parse_active_char( $sep.$tex, $lineno ) ;
						if (__isset($c)) {
							$self->callListener( 'outputString', undef, $c ) ;
						}
					}
				}
				else {
					if (!$isText) {
						$self->warning(
							locGet(_T("you cannot use in math mode the active character '{}', which is defined in text mode"), $sep),
							$lineno) ;
						if (__isset($sep)) {
							$self->callListener( 'outputString', undef, $sep ) ;
						}
					}
					else {
						(my $c,$tex) = $self->parse_active_char( $sep.$tex, $lineno ) ;
						if (__isset($c)) {
							$self->callListener( 'outputString', undef, $c ) ;
						}
					}
				}
			}
			else { # Unknow separator, treat as text
				if (__isset($sep)) {
					$self->callListener( 'outputString', undef, $sep ) ;
				}
			}
		}

		# Search the next separator
		($eaten,$sep,$tex,$crcount) = $self->eat_to_separator($tex) ;
	}

	if (__isset($tex)) {
		$self->callListener( 'outputString', undef, $tex ) ;
	}

	return undef ;
}

=pod

=item * putBack($)

Reinject a piece of text inside the parsed text in a way that it will
be the next text to be parsed by this object.

=cut
sub putBack($) : method {
	my $self = shift;
	my $text = shift;
	if ($text) {
		$self->{'put_back_text'} = $text;
	}
}

=pod

=item * eat_to_separator()

Eats the specified text until the first separator.
Takes 2 args:

=over

=item * text (string)

is the text to eat

=item * seps (optional string)

is the list of additional separators

=back

=cut
sub eat_to_separator($;$) : method {
	my $self = shift ;
	my $text = $_[0] || '' ;
	my $separators = $_[1] || '' ;
	my ($sep,$after) ;
	my $crcount = 0;

	if ($self->{'put_back_text'}) {
		$text = $self->{'put_back_text'}.$text;
		delete $self->{'put_back_text'};
	}

	my $stdSeparators = $self->{'SEPARATORS'};
	if (!$stdSeparators) {
		$stdSeparators = $self->build_separators();
	}
	$separators .= $stdSeparators;

	my $ret1 = '';

	while ( $text =~ /^(.*?)([\n$separators])(.*)$/s ) {
		(my $before,$sep,$text) = ($1,$2,$3) ;
		$ret1 .= "$before";
		if ($sep ne "\n") {
			return ($ret1,$sep,$text,$crcount) ;
		}
		$ret1 .= "\n";
		$crcount++;
	}
	
	if ($text) {
		$ret1 .= $text ;
		$sep = $after = '' ;
	}
	return ($ret1,$sep,$after,$crcount) ;
}

sub build_separators() {
	my $self = shift;
	my %seps = ();
	foreach my $k (keys %{$self->{'COMMENT_CHARACTERS'}}) {
		$seps{$k} = 1;
	}
	foreach my $k (keys %{$self->{'TEXT_MODE_ACTIVE_CHARACTERS'}}) {
		$seps{$k} = 1;
	}
	foreach my $k (keys %{$self->{'MATH_MODE_ACTIVE_CHARACTERS'}}) {
		$seps{$k} = 1;
	}
	$seps{'{'} = 1;
	$seps{'}'} = 1;
	$seps{'\\$'} = 1;
	$seps{'\\\\'} = 1;
	my $seps .= join('', keys %seps);
	$self->{'SEPARATORS'} = $seps;
	return $seps;
}

=pod

=item * parse_cmd()

Parse a TeX command.
Takes 3 args:

=over

=item * text (string)

is the text, which follows the backslash, to scan

=item * lineno (integer)

=item * prefix (optional string)

is a prefix merged to the command name. Use carefully.

=back

I<Returns:> (the result of the expand of the macro, the rest of the tex text, after the macro).

=cut
sub parse_cmd($$;$) : method {
	my $self = shift ;
	my ($tex,$lineno) = ($_[0] || '', $_[1] || 0 ) ;
	my $cmd_prefix = $_[2] || '' ;
	my $expandTo = '';

	if ( $tex =~ /^\[(.*)/s ) { # Starts multi-line math mode
		$tex = $1 ;
		$expandTo = $self->start_math_mode(2) ;
	}
	elsif ( $tex =~ /^\](.*)/s ) { # Stop multi-line math mode
		$tex = $1 ;
		$expandTo = $self->stop_math_mode(2) ;
	}
	elsif ( $tex =~ /^((?:[a-zA-Z]+\*?)|.)(.*)/s ) { # default LaTeX command
		(my $cmdname,$tex) = ($1,$2) ;
		my $trans = $self->search_cmd_trans( $cmdname, $lineno, ($cmd_prefix ne "\\") ) ;
		if ( ! defined( $trans ) || !$trans ) {
			$trans = '';
		}
		($expandTo,$tex) = $self->run_cmd( $cmd_prefix.$cmdname, $trans, $tex, $lineno ) ;
	}
	else {
		$self->warning( locGet(_T("invalid syntax for the TeX command: {}"),$cmd_prefix.$_[0]),
		                    $lineno ) ;
	}

	return ($expandTo,$tex) ;
}

=pod

=item * parse_active_char()

Parse a TeX active character.
Takes 3 args:

=over

=item * text (string)

is the text, with the active char, to scan

=item * lineno (integer)

=back

I<Returns:> the rest of the tex text, after the active character.

=cut
sub parse_active_char($$) : method {
	my $self = shift ;
	my ($tex,$lineno) = ($_[0] || '',
			      $_[1] || 0 ) ;
	my $expandTo = '';

	if ( $tex =~ /^(.)(.*)/s ) { # default LaTeX command
		(my $activeChar,$tex) = ($1,$2) ;
		my $trans = $self->search_cmd_trans( $activeChar, $lineno, 1 ) ;
		if ( ! defined( $trans ) || !$trans ) {
			$trans = '';
		}
		($expandTo,$tex) = $self->run_cmd( $activeChar, $trans, $tex, $lineno ) ;
	}
	else {
		$self->warning( locGet(_T("invalid syntax for the TeX active character: {}"), $_[0]),
		                    $lineno ) ;
		$expandTo = substr($tex,0,1) || '' ;
		$tex = substr($tex,1) || '' ;
	}

	return ($expandTo,$tex) ;
}

=pod

=item * search_cmd_trans()

Replies the macro definition that corresponds to
the specified TeX command.
Takes 3 args:

=over

=item * name (string)

is the name of the TeX command to search.

=item * lineno (integer)

=item * special (optional boolean)

indicates if the searched command has a special purpose
(example: _ in math mode)

=back

=cut
sub search_cmd_trans($$;$) : method {
	my $self = shift ;
	my $lineno = $_[1] || 0 ;
	my $special = $_[2] ;
	my ($found_math, $found_text) = (0,0);
	my ($math, $text) = (undef,undef);

	if ($_[0]) {

		if ($special) {
			if (exists $self->{'MATH_MODE_ACTIVE_CHARACTERS'}{$_[0]}) {
				$found_math = 1;
				$math = $self->{'MATH_MODE_ACTIVE_CHARACTERS'}{$_[0]};
			}
			if (exists $self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{$_[0]}) {
				$found_text = 1;
				$text = $self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{$_[0]};
			}
		}
		else {
			if (exists $self->{'MATH_MODE_MACROS'}{$_[0]}) {
				$found_math = 1;
				$math = $self->{'MATH_MODE_MACROS'}{$_[0]};
			}
			if (exists $self->{'TEXT_MODE_MACROS'}{$_[0]}) {
				$found_text = 1;
				$text = $self->{'TEXT_MODE_MACROS'}{$_[0]};
			}
		}

		if (!$found_text && !$found_math) {
			my $def = $self->callListener(
					'discoverMacroDefinition',
					undef,
					$_[0],
					$special,
					$self->is_math_mode());
			if (defined($def)) {
				if ($self->is_math_mode()) {
					$found_math = 1;
					$math = $def;
				}
				else {
					$found_text = 1;
					$text = $def;
				}
			}
		}
	}

	printDbgFor(5, locGet(_T('Found parameter definition for \'{}\': math={}; text={}'), $_[0], 
			(defined($math) ? $math : '<undef>'), (defined($text) ? $text : '<undef>')));

	if ( $found_math || $found_text ) {
		if ( $self->is_math_mode() ) {
			if ( ! $found_math ) {
				$self->warning( locGet(_T("the command {}{} was not defined for math-mode, assumes to use the text-mode version instead"), ( $special ? '' : '\\' ), $_[0]),
					$lineno ) ;
				return $text ;
			}
			else {
				return $math ;
			}
		}
		elsif ( ! $found_text ) {
			$self->warning( locGet(_T("the command {}{}  was not defined for text-mode, assumes to use the math-mode version instead"), ( $special ? '' : '\\' ), $_[0]),
			      $lineno ) ;
			return $math ;
		}
		else {
			return $text ;
		}
	}
	return undef ;
}

=pod

=item * run_cmd()

Execute the specified macro on the specified tex string.
Takes 4 args:

=over

=item * name (string)

is the name of the TeX macro.

=item * trans (string)

is the definition for the macro.

=item * text (string)

is the text from which some data must be extracted to
treat the macro.

=item * lineno (integer)

is le line number where the text starts

=back

I<Returns:> nothing.

=cut
sub run_cmd($$$$) : method {
	my $self = shift ;
	my ($cmdname,$tex,$lineno) = (
		       $_[0] || confess( 'you must supply the TeX command name'),
		       $_[2] || '',
		       $_[3] || 0 ) ;
	my $expandTo;

	if ( $_[1] ) {
		# This macro has params
		printDbgFor(5, locGet(_T('Expanding \'{}\''), $cmdname));
		($tex,my $params, my $rawparams) = $self->eat_cmd_parameters( $_[1], $tex, $cmdname, $lineno ) ;
		# Apply the macro
		$expandTo = $self->callListener('expandMacro', 
					$cmdname.$rawparams,
					$cmdname, @$params);
	}
	else {
		# No param, put the HTML string inside the output stream
		printDbgFor(5, locGet(_T('Expanding \'{}\''), $cmdname));
		$expandTo = $self->callListener('expandMacro', 
					$cmdname,
					$cmdname);
	}
	return ($expandTo,$tex) ;
}

=pod

=item * eat_cmd_parameters()

Eat the parameters for a macro.
Takes 3 args:

=over

=item * params (string)

is the description of the parameters to eat.

=item * text (string)

is the text from which some data must be extracted.

=item * macro (string) is the name of the macro for which parameters must be extracted.

=item * lineno (integer)

=back

I<Returns>: (the rest of the tex, the array of parameters, the raw representation of the parameters)

=cut
sub eat_cmd_parameters($$$$) : method {
	my $self = shift ;
	my $p_params = $_[0] || '' ;
	my $tex = $_[1] || '' ;
	my $macro = $_[2] || '';
	my $lineno = $_[3] || 0 ;
	my @params = () ;
	my $rawparams = '';
	printDbgFor(5, locGet(_T('Macro prototype of \'{}\': {}'), $macro, $p_params));
	while ( $p_params =~ /((?:\!?\{\})|(?:\!?\[[^\]]*\])|-|\\)/sg ) {
		my $p = $1 ;
		# Eats no significant white spaces
		#$tex =~ s/^ +//s ;
		if ( $p =~ /^(\!?)\{\}/s ) { # Eates a mandatory parameter
			my $optional = $1 || '' ;
			my $prem = substr($tex,0,1) ;
			$tex = substr($tex,1) ;
			if ( $prem eq '{' ) {
				(my $context,$tex) = $self->eat_context( $tex, '\\}' ) ;
				push @params, { 'eval' => ($optional ne '!'),
					'text' => $context,
				      } ;
				$rawparams .= "{$context}";
			}
			elsif ( $prem eq '\\' ) {
				if ($optional ne '!') {
					# The following macro is expandable
					(my $c, $tex) = $self->parse_cmd($tex, $lineno, '\\') ;
					push @params, { 'eval' => 1,
						'text' => $c,
					      } ;
					$rawparams .= "{$c}";
				}
				else {
					# The following macro is not expandable
					$tex =~ /^((?:[a-zA-Z]+\*?)|.)(.*)$/s;
					(my $c, $tex) = ($1,$2);
					push @params, { 'eval' => 0,
						'text' => $c,
					      } ;
					$rawparams .= "\\$c";
				}
			}
			else {
				push @params, { 'eval' => ($optional ne '!'),
					'text' => $prem,
				      } ;
				$rawparams .= "$prem";
			}
		}
		elsif( $p =~ /^(\!?)\[([^\]]*)\]/s ) { # Eates an optional parameter
			my ($optional,$default_val) = ( $1 || '', $2 || '' ) ;
			my $prem = substr($tex,0,1) ;
			if ( $prem eq '[' ) {
				(my $context,$tex) = $self->eat_context( substr($tex,1), '\\]' ) ;
				push @params, { 'eval' => ($optional ne '!'),
						'text' => $context,
					      } ;
				$rawparams .= "[$context]";
			}
			else {
				push @params, { 'eval' => ($optional ne '!'),
						'text' => $default_val,
					      } ;
			}
		}
		elsif( $p eq '\\' ) { # Eates a TeX command name
			if ( $tex =~ /^\\((?:[a-zA-Z]+\*?)|.)(.*)$/s ) {
				my $n = $1;
				$tex = $2 ;
				push @params, { 'eval' => 1,
						'text' => $n,
					      } ;
				$rawparams .= "\\$n";
			}
			else {
				my $msg = substr($tex, 0, 50);
				$msg =~ s/[\n\r]/\\n/sg;
				$msg =~ s/\t/\\t/sg;
				$msg = locGet(_T("expected a TeX macro for expanding the macro {}, here: '{}'"), $macro, $msg);
				$self->printWarn($msg, $lineno ) ;
				push @params, { 'eval' => 1,
						'text' => '',
					      } ;	
				$rawparams .= "\\";
			}
		}
		elsif ( $p eq '-' ) { # Eates until the end of the current context
			(my $context,$tex) = $self->eat_context( $tex, '\\}' ) ;
			push @params, { 'eval' => 1,
				      'text' => $context,
				    } ;
			$rawparams .= "$context";
		}
		else {
			confess( locGet(_T("unable to recognize the following argument specification: {}"), $p) ) ;
		}
	}
	return ($tex,\@params,$rawparams) ;
}

=pod

=item * eat_context()

Eaten the current context.
Takes 2 args:

=over

=item * text (string)

is the text from which some data must be extracted.

=item * end (string)

is the ending separator

=back

=cut
sub eat_context($$) : method {
	my $self = shift ;
	my $text = $_[0] || '' ;
	my $enddelim = $_[1] || confess( 'you must supply the closing delimiter' ) ;
	my $context = '' ;
	my $contextlevel = 0 ;

	# Search the first separator
	my ($eaten,$sep,$tex) = $self->eat_to_separator($text,$enddelim) ;

	while ($sep) {

		if ( $sep eq '{' )  { # open a context
			$contextlevel ++ ;
			$eaten .= $sep ;
		}
		elsif ( $sep eq '}' ) { # close a context
			if ( $contextlevel <= 0 ) {
				return ($context.$eaten,$tex) ;
			}
			$eaten .= $sep ;
			$contextlevel -- ;
		}
		elsif ( $sep eq '\\' ) {
			$tex =~ /^([a-zA-Z]+\*?|.)(.*)$/s ;
			$eaten .= "\\$1";
			$tex = $2 ;
		}
		elsif ( ( $contextlevel <= 0 ) &&
		    ( $sep =~ /$enddelim/s ) ) { # The closing delemiter was found
			return ($context.$eaten,$tex) ;
		}
		else { # Unknow separator, treat as text
			$eaten .= $sep ;
		}

		# Translate the text before the separator
		$context .= $eaten ;

		# Search the next separator
		($eaten,$sep,$tex) = $self->eat_to_separator($tex,$enddelim) ;
	}

	return ($context.$eaten,$tex) ;
}

#------------------------------------------------------
#
# Math mode
#
#------------------------------------------------------

=pod

=item * start_math_mode($)

Starts the mathematical mode.
Takes 1 arg:

=over

=item * mode (integer)

is the math mode to start (1: inline, 2: multi-line)

=back

I<Returns:> the result of the expansion of the math starting symbol.

=cut
sub start_math_mode($) {
	my $self = shift ;
	my $mode = ( $_[0] % 3 );
	my $default = ($mode == 2 ) ? '\\[' : '$';
	if (!$self->is_math_mode() ) {
		$self->{'MATH_MODE'} = $mode ;
		if ( $self->{'MATH_MODE'} == 2 ) {
			return $self->callListener('multilineMathStart', $default);
		}
		return $self->callListener('inlineMathStart', $default);
	}
	return $default;
}

=pod

=item * stop_math_mode($)

Stops the mathematical mode.

Takes 1 arg:

=over

=item * mode (integer)

is the math mode to stop (1: inline, 2: multi-line)

=back

I<Returns:> the result of the expansion of the math starting symbol.

=cut
sub stop_math_mode($) {
	my $self = shift ;
	my $mode = ( $_[0] % 3 );
	my $default = ($mode == 2 ) ? '\\]' : '$';
	if ( $self->is_math_mode() ) {
		my $m = $self->{'MATH_MODE'};
		$self->{'MATH_MODE'} = 0 ;
		if ( $m == 2 ) {
			return $self->callListener('multilineMathStop', $default);
		}
		return $self->callListener('inlineMathStop', $default);
	}
	return $default;
}

=pod

=item * is_math_mode()

Replies if inside a mathematical mode.

=cut
sub is_math_mode() {
	my $self = shift ;
	return ( $self->{'MATH_MODE'} != 0 ) ;
}

=pod

=item * is_inline_math_mode()

Replies if inside a inlined mathematical mode.

=cut
sub is_inline_math_mode() {
	my $self = shift ;
	return ( $self->{'MATH_MODE'} == 1 ) ;
}

=pod

=item * is_multiline_math_mode()

Replies if inside a multi-lined mathematical mode.

=cut
sub is_multiline_math_mode() {
	my $self = shift ;
	return ( $self->{'MATH_MODE'} == 2 ) ;
}

#------------------------------------------------------
#
# Comment characters
#
#------------------------------------------------------

=pod

=item * addCommentChar()

Add a comment character.
Takes 1 args:

=over

=item * char (string)

is the character to add

=back

=cut
sub addCommentChar($$) : method {
	my $self = shift;
	confess( 'you must supply the comment character' ) unless $_[0] ;
	$self->{'COMMENT_CHARACTERS'}{"$_[0]"} = 1;
}

=pod

=item * removeCommentChar()

Remove a comment char.
Takes 1 arg:

=over

=item * char (string)

is the character to remove

=back

=cut
sub removeCommentChar($) : method {
	my $self = shift;
	confess( 'you must supply the comment character' ) unless $_[0] ;
	delete $self->{'COMMENT_CHARACTERS'}{$_[0]};
}

=pod

=item * getCommentChars()

Replies the comment chars.

=cut
sub getCommentChars() : method {
	my $self = shift;
	return keys %{$self->{'COMMENT_CHARACTERS'}} ;
}

#------------------------------------------------------
#
# Text mode macros
#
#------------------------------------------------------

=pod

=item * addTextModeMacro($$;$)

Add a macro in text mode.
Takes 2 args:

=over

=item * name (string)

is the name of the macro.

=item * params (string)

is the specification of the parameters of the macro.
The parameter prototype of the LaTeX command. If not empty, it must contains one (or more) of:

=over

=item * C<{}>: for a mandatory parameter

=item * C<[d]>: for an optional parameter. C<d> is the default value given to this parameter if it was not provided inside the LaTeX code

=item * C<\>: for a LaTeX command name

=item * C<!>: indicates that the following sign (C<{}> or C<[]>) must not be interpreted by the LaTeX parser. It must be used for verbatim output

=item * C<->: to read the text until the end of the current LaTeX context

=back

=item * isSpecial (boolean)

indicates if the command is a special character, ie. a macro that is not needing to be
prefixed by '\'.

=back

=cut
sub addTextModeMacro($$;$) : method {
	my $self = shift;
	confess( 'you must supply the name of the macro' ) unless $_[0] ;
	if ($_[2]) {
		$self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{"$_[0]"} = ( $_[1] || '' );
		$self->{'SEPARATORS'} = '';
	}
	else {
		$self->{'TEXT_MODE_MACROS'}{"$_[0]"} = ( $_[1] || '' );
	}
}

=pod

=item * removeTextModeMacro()

Remove a text mode macro.
Takes 1 arg:

=over

=item * name (string)

is the name of the macro.

=item * isSpecial (boolean)

indicates if the command is a special character, ie. a macro that is not needing to be
prefixed by '\'.

=back

=cut
sub removeTextModeMacro($;$) : method {
	my $self = shift;
	confess( 'you must supply the name of the macro' ) unless $_[0] ;
	if ($_[1]) {
		if ($self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{"$_[0]"}) {
			delete $self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{"$_[0]"};
		}
		$self->{'SEPARATORS'} = '';
	}
	else {
		if ($self->{'TEXT_MODE_MACROS'}{"$_[0]"}) {
			delete $self->{'TEXT_MODE_MACROS'}{"$_[0]"};
		}
	}
}

=pod

=item * getTextModeMacros()

Replies the text mode macros.

=cut
sub getTextModeMacros() : method {
	my $self = shift;
	my %macros = (
		'macros' => $self->{'TEXT_MODE_MACROS'},
		'special' => $self->{'TEXT_MODE_ACTIVE_MACROS'},
	);
	return %macros;
}

=pod

=item * clearTextModeMacros()

Remove all the text mode macros.

=cut
sub clearTextModeMacros() : method {
	my $self = shift;
	$self->{'TEXT_MODE_MACROS'} = {};
	$self->{'TEXT_MODE_ACTIVE_MACROS'} = {};
}

#------------------------------------------------------
#
# Math mode macros
#
#------------------------------------------------------

=pod

=item * addMathModeMacro($$;$)

Add a macro in math mode.
Takes 2 args:

=over

=item * name (string)

is the name of the macro.

=item * params (string)

is the specification of the parameters of the macro.
The parameter prototype of the LaTeX command. If not empty, it must contains one (or more) of:

=over

=item * C<{}>: for a mandatory parameter

=item * C<[d]>: for an optional parameter. C<d> is the default value given to this parameter if it was not provided inside the LaTeX code

=item * C<\>: for a LaTeX command name

=item * C<!>: indicates that the following sign (C<{}> or C<[]>) must not be interpreted by the LaTeX parser. It must be used for verbatim output

=item * C<->: to read the text until the end of the current LaTeX context

=back

=item * isSpecial (boolean)

indicates if the command is a special character, ie. a macro that is not needing to be
prefixed by '\'.

=back

=cut
sub addMathModeMacro($$;$) : method {
	my $self = shift;
	confess( 'you must supply the name of the macro' ) unless $_[0] ;
	if ($_[2]) {
		$self->{'MATH_MODE_ACTIVE_CHARACTERS'}{"$_[0]"} = ( $_[1] || '' );
		$self->{'SEPARATORS'} = '';
	}
	else {
		$self->{'MATH_MODE_MACROS'}{"$_[0]"} = ( $_[1] || '' );
	}
}

=pod

=item * removeMathModeMacro()

Remove a math mode macro.
Takes 1 arg:

=over

=item * name (string)

is the name of the macro.

=item * isSpecial (boolean)

indicates if the command is a special character, ie. a macro that is not needing to be
prefixed by '\'.

=back

=cut
sub removeMathModeMacro($;$) : method {
	my $self = shift;
	confess( 'you must supply the name of the macro' ) unless $_[0] ;
	if ($_[1]) {
		if ($self->{'MATH_MODE_ACTIVE_CHARACTERS'}{"$_[0]"}) {
			delete $self->{'MATH_MODE_MACROS'}{"$_[0]"};
		}
		$self->{'SEPARATORS'} = '';
	}
	else {
		if ($self->{'MATH_MODE_MACROS'}{"$_[0]"}) {
			delete $self->{'MATH_MODE_MACROS'}{"$_[0]"};
		}
	}
}

=pod

=item * getMathModeMacros()

Replies the math mode macros.

=cut
sub getMathModeMacros() : method {
	my $self = shift;
	my %macros = (
		'macros' => $self->{'MATH_MODE_MACROS'},
		'special' => $self->{'MATH_MODE_ACTIVE_MACROS'},
	);
	return %macros;
}

=pod

=item * clearMathModeMacros()

Remove all the math mode macros.

=cut
sub clearMathModeMacros() : method {
	my $self = shift;
	$self->{'MATH_MODE_MACROS'} = {};
	$self->{'MATH_MODE_ACTIVE_MACROS'} = {};
}

#------------------------------------------------------
#
# Macros
#
#------------------------------------------------------

=pod

=item * addStandardMacros()

Add the standard LaTeX macros into the parser definitions.

=cut
sub addStandardMacros() : method {
	my $self = shift;
	while (my ($k,$v) = each(%TEX_DEFAULT_TEXT_MODE_MACROS)) {
		$self->{'TEXT_MODE_MACROS'}{$k} = $v;
	}
	while (my ($k,$v) = each(%TEX_DEFAULT_MATH_MODE_MACROS)) {
		$self->{'MATH_MODE_MACROS'}{$k} = $v;
	}
	while (my ($k,$v) = each(%TEX_DEFAULT_TEXT_MODE_ACTIVE_CHARACTERS)) {
		$self->{'TEXT_MODE_ACTIVE_CHARACTERS'}{$k} = $v;
	}
	while (my ($k,$v) = each(%TEX_DEFAULT_MATH_MODE_ACTIVE_CHARACTERS)) {
		$self->{'MATH_MODE_ACTIVE_CHARACTERS'}{$k} = $v;
	}
}

1;
__END__

=back

=head1 COPYRIGHT

(c) Copyright 1998-13 Stephane Galland E<lt>galland@arakhne.orgE<gt>, under GPL.

=head1 AUTHORS

=over

=item *

Conceived and initially developed by Stephane Galland E<lt>galland@arakhne.orgE<gt>.

=back

