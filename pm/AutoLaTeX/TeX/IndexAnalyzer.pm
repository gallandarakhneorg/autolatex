# autolatex - IndexAnalyzer.pm
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

IndexAnalyzer.pm - Extract index definitions from an IDX file.

=head1 DESCRIPTION

Tool that is extracting the definitions of indexes from an IDX file.

To use this library, type C<use AutoLaTeX::TeX::IndexAnalyzer;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::TeX::IndexAnalyzer;

$VERSION = '1.0';
@ISA = ('Exporter');
@EXPORT = qw( &getIdxIndexDefinitions &makeIdxIndexDefinitionMd5 ) ;
@EXPORT_OK = qw();

require 5.014;
use strict;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Config; # Perl configuration
use File::Spec;
use File::Basename;
use Digest::MD5 qw(md5_base64);

use AutoLaTeX::Core::Util;
use AutoLaTeX::TeX::TeXParser;

my %MACROS = (
	'indexentry'			=> '[]!{}!{}',
	);

=pod

=item B<getIdxIndexDefinitions($)>

Parse an idx file and extract the index definitions.

=over 4

=item * C<idxfile> is the name of the IDX file to parse.

=back

I<Returns:> the indexes

=cut
sub getIdxIndexDefinitions($) {
	my $input = shift;
	
	local *FILE;
	open(*FILE, "< $input") or printErr("$input: $!");
	my $content = '';
	while (my $line = <FILE>) {
		$content .= $line;
	}
	close(*FILE);

	my $listener = AutoLaTeX::TeX::IndexAnalyzer->_new($input);

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

=item B<makeIdxIndexDefinitionMd5($)>

Parse an idx file, extract the index definitions, and build a MD5.

=over 4

=item * C<idxfile> is the name of the IDX file to parse.

=back

I<Returns:> the MD5 of the indexes.

=cut
sub makeIdxIndexDefinitionMd5($) {
	my @citations = getIdxIndexDefinitions($_[0]);
	return md5_base64(@citations);
}

sub _expandMacro($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;
	if ($_[1]->{'text'} || $_[2]->{'text'}) {
		my $key = ($_[2]->{'text'} || '') . '|' . ($_[1]->{'text'} || '');
		$self->{'indexes'}{$key} = 1;
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
			'indexes' => {},
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
