# autolatex - GlossaryAnalyzer.pm
# Copyright (C) 2016  Stephane Galland <galland@arakhne.org>
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

GlossaryAnalyzer.pm - Extract glossary definitions from a GLS file.

=head1 DESCRIPTION

Tool that is extracting the definitions of glossary from a GLS file.

To use this library, type C<use AutoLaTeX::TeX::GlossaryAnalyzer;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::TeX::GlossaryAnalyzer;

$VERSION = '1.0';
@ISA = ('Exporter');
@EXPORT = qw( &getGlsIndexDefinitions &makeGlsIndexDefinitionMd5 ) ;
@EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Config; # Perl configuration
use File::Spec;
use File::Basename;
use Digest::MD5 qw(md5_base64);

use AutoLaTeX::Core::Util;
use AutoLaTeX::TeX::TeXParser;

my %MACROS = (
	'glossentry'			=> '[]!{}!{}',
	);

=pod

=item B<getGlsIndexDefinitions($)>

Parse a gls file and extract the glossary definitions.

=over 4

=item * C<glsfile> is the name of the GLS file to parse.

=back

I<Returns:> the glossary entries

=cut
sub getGlsIndexDefinitions($) {
	my $input = shift;
	
	local *FILE;
	open(*FILE, "< $input") or printErr("$input: $!");
	my $content = '';
	while (my $line = <FILE>) {
		$content .= $line;
	}
	close(*FILE);

	my $listener = AutoLaTeX::TeX::GlossaryAnalyzer->_new($input);

	my $parser = AutoLaTeX::TeX::TeXParser->new("$input", $listener);

	while (my ($k,$v) = each(%MACROS)) {
		$parser->addTextModeMacro($k,$v);
		$parser->addMathModeMacro($k,$v);
	}

	$parser->parse( $content );

	my @glossaryEntries = keys %{$listener->{'glossaryEntries'}};
	@glossaryEntries = sort @glossaryEntries;

	return @glossaryEntries;
}

=pod

=item B<makeGlsIndexDefinitionMd5($)>

Parse a gls file, extract the glossary definitions, and build a MD5.

=over 4

=item * C<glsfile> is the name of the GLS file to parse.

=back

I<Returns:> the MD5 of the glossary entries.

=cut
sub makeGlsIndexDefinitionMd5($) {
	my @glossaryEntries = getGlsIndexDefinitions($_[0]);
	return md5_base64(@glossaryEntries);
}

sub _expandMacro($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;
	if ($_[1]->{'text'} || $_[2]->{'text'}) {
		my $key = ($_[2]->{'text'} || '') . '|' . ($_[1]->{'text'} || '');
		$self->{'glossaryEntries'}{$key} = 1;
	}
	return '';
}

sub _new($) : method {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $parent = ref($proto) && $proto ;

	my $self ;
	if ( $parent ) {
		%{$self} = %{$parent} ;
	}
	else {
		$self = {
			'basename' => basename($_[0],'.tex'),
			'file' => $_[0],
			'expandMacro' => \&_expandMacro,
			'glossaryEntries' => {},
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
