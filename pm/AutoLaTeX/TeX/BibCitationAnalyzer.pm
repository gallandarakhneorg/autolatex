# autolatex - BibCitationAnalyzer.pm
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

BibCitationAnalyzer.pm - Extract bibliography citation from a AUX file.

=head1 DESCRIPTION

Tool that is extracting the bibliography citations from a AUX file.

To use this library, type C<use AutoLaTeX::TeX::BibCitationAnalyzer;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::TeX::BibCitationAnalyzer;

$VERSION = '2.0';
@ISA = ('Exporter');
@EXPORT = qw( &getAuxBibliographyData &getAuxBibliographyCitations &makeAuxBibliographyCitationMd5 ) ;
@EXPORT_OK = qw();

use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Config; # Perl configuration
use File::Spec;
use File::Basename;
use Digest::MD5 qw(md5_base64);

use AutoLaTeX::Core::Util;
use AutoLaTeX::TeX::TeXParser;

my %MACROS = (
	'citation'			=> '[]!{}',
	'bibcite'			=> '[]!{}',
	'bibdata'			=> '[]!{}',
	'bibstyle'			=> '[]!{}',
	);

=pod

=item B<getAuxBibliographyData($)>

Parse an aux file and extract the bibliography data.

=over 4

=item * C<auxfile> is the name of the AUX file to parse.

=back

I<Returns:> an associative array with the keys 'citations', 'databases', and 'styles'.

=cut
sub getAuxBibliographyData($) {
	my $input = shift;
	local *FILE;
	open(*FILE, "< $input") or printErr("$input: $!");
	my $content = '';
	while (my $line = <FILE>) {
		$content .= $line;
	}
	close(*FILE);

	my $listener = AutoLaTeX::TeX::BibCitationAnalyzer->_new($input);

	my $parser = AutoLaTeX::TeX::TeXParser->new("$input", $listener);

	while (my ($k,$v) = each(%MACROS)) {
		$parser->addTextModeMacro($k,$v);
		$parser->addMathModeMacro($k,$v);
	}

	$parser->parse( $content );

	my @citations = keys %{$listener->{'citations'}};
	@citations = sort @citations;
	my @databases = keys %{$listener->{'databases'}};
	my @styles = keys %{$listener->{'styles'}};
	my %data = (
		'citations' => \@citations,
		'databases' => \@databases,
		'styles' => \@styles,
	);

	return %data;
}

=pod

=item B<getAuxBibliographyCitations($)>

Parse an aux file and extract the bibliography citations.

=over 4

=item * C<auxfile> is the name of the AUX file to parse.

=back

I<Returns:> the included files from the TeX file into an associative array.

=cut
sub getAuxBibliographyCitations($) {
	my $input = shift;
	
	local *FILE;
	open(*FILE, "< $input") or printErr("$input: $!");
	my $content = '';
	while (my $line = <FILE>) {
		$content .= $line;
	}
	close(*FILE);

	my $listener = AutoLaTeX::TeX::BibCitationAnalyzer->_new($input);

	my $parser = AutoLaTeX::TeX::TeXParser->new("$input", $listener);

	while (my ($k,$v) = each(%MACROS)) {
		$parser->addTextModeMacro($k,$v);
		$parser->addMathModeMacro($k,$v);
	}

	$parser->parse( $content );

	my @citations = keys %{$listener->{'citations'}};
	@citations = sort @citations;

	return @citations;
}

=pod

=item B<makeAuxBibliographyCitationMd5($)>

Parse an aux file, extract the bibliography citations, and build a MD5.

=over 4

=item * C<auxfile> is the name of the AUX file to parse.

=back

I<Returns:> the MD5 of the citations.

=cut
sub makeAuxBibliographyCitationMd5($) {
	my @citations = getAuxBibliographyCitations($_[0]);
	return md5_base64(@citations);
}

sub _expandMacro($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;
	if ($macro eq '\\bibdata') {
		if ($_[1]->{'text'}) {
			$self->{'databases'}{$_[1]->{'text'}} = 1;
		}
	}
	elsif ($macro eq '\\bibstyle') {
		if ($_[1]->{'text'}) {
			$self->{'styles'}{$_[1]->{'text'}} = 1;
		}
	}
	elsif ($_[1]->{'text'}) {
		$self->{'citations'}{$_[1]->{'text'}} = 1;
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
			'citations' => {},
			'databases' => {},
			'styles' => {},
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
