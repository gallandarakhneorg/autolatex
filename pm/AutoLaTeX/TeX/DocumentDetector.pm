# autolatex - DocumentDetector.pm
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

=pod

=head1 NAME

DocumentDetector.pm - Detect if a TeX file contains a LaTeX document.

=head1 DESCRIPTION

Tool that is parsing a TeX file and detect if \documentclass is inside.

To use this library, type C<use AutoLaTeX::TeX::DocumentDetector;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::TeX::DocumentDetector;

$VERSION = '1.0';
@ISA = ('Exporter');
@EXPORT = qw( &isLaTeXDocument ) ;
@EXPORT_OK = qw();

require 5.014;
use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use AutoLaTeX::TeX::TeXParser;

my %MACROS = (
	'documentclass'			=> '![]!{}',
	);

=pod

=item B<isLaTeXDocument($)>

Replies if the given file is a LaTeX document, ie.
a text file that contains \documentclass.

=over 4

=item * C<file> is the name of the file to parse.

=back

I<Returns:> true if the file is a LaTeX document;
false otherwise.

=cut
sub isLaTeXDocument($) {
	my $input = shift;
	
	local *FILE;
	open(*FILE, "< $input") or printErr("$input: $!");
	my $content = '';
	while (my $line = <FILE>) {
		$content .= $line;
	}
	close(*FILE);

	my $listener = AutoLaTeX::TeX::DocumentDetector->_new();

	my $parser = AutoLaTeX::TeX::TeXParser->new("$input", $listener);

	while (my ($k,$v) = each(%MACROS)) {
		$parser->addTextModeMacro($k,$v);
		$parser->addMathModeMacro($k,$v);
	}

	$parser->parse( $content );

	return $listener->{'isLaTeXDocument'};
}

sub _expandMacro($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;
	if ($macro eq '\\documentclass' ) {
		$self->{'isLaTeXDocument'} = 1;
		$parser->stop();
	}
	return '';
}

sub _new() : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $parent = ref($proto) && $proto ;

	my $self ;
	if ( $parent ) {
		%{$self} = %{$parent} ;
	}
	else {
		$self = {
			'expandMacro' => \&_expandMacro,
			'isLaTeXDocument' => 0,
		};
	}
	bless( $self, $class );
	return $self;
}

1;
__END__
=back

=head1 BUG REPORT AND FEEDBACK

To report bugs, provide feedback, suggest new features, etc. visit the AutoLaTeX Project management page at <http://www.arakhne.org/autolatex/> or send email to the author at L<galland@arakhne.org>.

=head1 LICENSE

S<GNU Public License (GPL)>

=head1 COPYRIGHT

S<Copyright (c) 2013 Stéphane Galland E<lt>galland@arakhne.orgE<gt>>

=head1 SEE ALSO

L<autolatex-dev>
