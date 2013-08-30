# autolatex - TeXDependencyAnalyzer.pm
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

TeXDependencyAnalyzer.pm - Detect dependencies of a TeX file.

=head1 DESCRIPTION

Tool that is extracting the dependencies of the TeX file.

To use this library, type C<use AutoLaTeX::TeX::TeXDependencyAnalyzer;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::TeX::TeXDependencyAnalyzer;

$VERSION = '4.0';
@ISA = ('Exporter');
@EXPORT = qw( &getDependenciesOfTeX ) ;
@EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Config; # Perl configuration
use File::Spec;
use File::Basename;
use AutoLaTeX::Core::Util;
use AutoLaTeX::TeX::TeXParser;

my %MACROS = (
	'input'				=> '!{}',
	'include'			=> '!{}',
	'makeindex'			=> '',
	'printindex'			=> '',
	'usepackage'			=> '![]!{}',
	'RequirePackage'		=> '![]!{}',
	'documentclass'			=> '![]!{}',
	'addbibresource'		=> '![]!{}',
	);

=pod

=item B<getDependenciesOfTeX($)>

Parse a TeX file and detect the included files.

=over 4

=item * C<file> is the name of the TeX file to parse.

=item * C<dir> is the reference directory for the relative path.

=back

I<Returns:> the included files from the TeX file into an associative array.

=cut
sub getDependenciesOfTeX($$) {
	my $input = shift;
	my $rootdir = shift;
	
	local *FILE;
	open(*FILE, "< $input") or printErr("$input: $!");
	my $content = '';
	while (my $line = <FILE>) {
		$content .= $line;
	}
	close(*FILE);

	my $listener = AutoLaTeX::TeX::TeXDependencyAnalyzer->_new($input,$rootdir);

	my $parser = AutoLaTeX::TeX::TeXParser->new("$input", $listener);

	while (my ($k,$v) = each(%MACROS)) {
		$parser->addTextModeMacro($k,$v);
		$parser->addMathModeMacro($k,$v);
	}

	$parser->parse( $content );

	my %analysis = ( %{$listener->{'dependencies'}} );

	foreach my $cat ('sty', 'tex') {
		if ($analysis{$cat}) {
			my @t = keys %{$analysis{$cat}};
			$analysis{$cat} = \@t;
		}
	}

	while (my ($bibdb,$bibdt) = each(%{$analysis{'biblio'}})) {
		foreach my $cat ('bib', 'bst', 'bbx', 'cbx') {
			if ($bibdt->{$cat}) {
				my @t = keys %{$bibdt->{$cat}};
				$bibdt->{$cat} = \@t;
			}
		}
	}

	$analysis{'biber'} = $listener->{'is_biber'};

	return %analysis;
}

sub _expandMacro($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;
	my $bibdb = '';

	if ( $macro eq '\\include' || $macro eq '\\input' ) {
		foreach my $param (@_) {
			my $value = $param->{'text'};
			if ($value) {
				my $texFile = "$value.tex";
				if (!File::Spec->file_name_is_absolute($texFile)) {
					$texFile = File::Spec->catfile($self->{'dirname'}, "$texFile");
				}
				if (-f "$texFile") {
					$self->{'dependencies'}{'tex'}{$texFile} = 1;
				}
			}
		}
	}
	elsif ( $macro eq '\\makeindex' || $macro eq '\\printindex' ) {
		$self->{'dependencies'}{'idx'} = 1;
	}
	elsif ( $macro eq '\\usepackage' || $macro eq '\\RequirePackage' ) {
		my $sty = $_[1]{'text'};
		my $styFile = "$sty";
		if ($styFile !~ /\.sty$/i) {
			$styFile .= ".sty";
		}
		if ($styFile eq 'multibib.sty') {
			$self->{'is_multibib'} = 1;
		}
		if ($styFile eq 'biblatex.sty') {
			$self->{'is_biblatex'} = 1;
			# Parse the biblatex parameters
			if ($_[0] && $_[0]->{'text'}) {
				my @params = split(/\s*\,\s*/, trim($_[0]->{'text'} || ''));
				foreach my $p (@params) {
					my ($k, $v);
					if ($p =~ /^([^=]+)\s*=\s*(.*)$/) {
						$k = $1;
						$v = $2 || '';
					}
					else {
						$k = $p;
						$v = '';
					}
					if  ($k eq 'backend') {
						$self->{'is_biber'} = ($v eq 'biber');
					}
					elsif  ($k eq 'style') {
						my $bbxFile = "$v";
						if ($bbxFile !~ /\.bbx$/i) {
							$bbxFile .= ".bbx";
						}
						if (!File::Spec->file_name_is_absolute($bbxFile)) {
							$bbxFile = File::Spec->catfile($self->{'dirname'}, "$bbxFile");
						}
						if (-f "$bbxFile") {
							$self->{'dependencies'}{'biblio'}{$bibdb}{'bbx'}{$bbxFile} = 1;
						}
						my $cbxFile = "$v";
						if ($cbxFile !~ /\.cbx$/i) {
							$cbxFile .= ".cbx";
						}
						if (!File::Spec->file_name_is_absolute($cbxFile)) {
							$cbxFile = File::Spec->catfile($self->{'dirname'}, "$cbxFile");
						}
						if (-f "$cbxFile") {
							$self->{'dependencies'}{'biblio'}{$bibdb}{'cbx'}{$cbxFile} = 1;
						}
					}
					elsif ($k eq 'bibstyle') {
						my $bbxFile = "$v";
						if ($bbxFile !~ /\.bbx$/i) {
							$bbxFile .= ".bbx";
						}
						if (!File::Spec->file_name_is_absolute($bbxFile)) {
							$bbxFile = File::Spec->catfile($self->{'dirname'}, "$bbxFile");
						}
						if (-f "$bbxFile") {
							$self->{'dependencies'}{'biblio'}{$bibdb}{'bbx'}{$bbxFile} = 1;
						}
					}
					elsif ($k eq 'citestyle') {
						my $cbxFile = "$v";
						if ($cbxFile !~ /\.cbx$/i) {
							$cbxFile .= ".cbx";
						}
						if (!File::Spec->file_name_is_absolute($cbxFile)) {
							$cbxFile = File::Spec->catfile($self->{'dirname'}, "$cbxFile");
						}
						if (-f "$cbxFile") {
							$self->{'dependencies'}{'biblio'}{$bibdb}{'cbx'}{$cbxFile} = 1;
						}
					}
				}
			}
		}
		if (!File::Spec->file_name_is_absolute($styFile)) {
			$styFile = File::Spec->catfile($self->{'dirname'}, "$styFile");
		}
		if (-f "$styFile") {
			$self->{'dependencies'}{'sty'}{"$styFile"} = 1;
		}
	}
	elsif ($macro eq '\\documentclass' ) {
		my $cls = $_[1]{'text'};
		my $clsFile = "$cls";
		if ($clsFile !~ /\.cls$/i) {
			$clsFile .= ".cls";
		}
		if (!File::Spec->file_name_is_absolute($clsFile)) {
			$clsFile = File::Spec->catfile($self->{'dirname'}, "$clsFile");
		}
		if (-f "$clsFile") {
			$self->{'dependencies'}{'cls'} = [ "$clsFile" ];
		}
	}
	elsif ($macro =~ /^\\bibliographystyle(.*)$/s ) {
		$bibdb = $1;
		$bibdb = $self->{'basename'} unless ($bibdb);
		foreach my $param (@_) {
			my $value = $param->{'text'};
			if ($value) {
				my $bstFile = "$value";
				if ($bstFile !~ /\.bst$/i) {
					$bstFile .= ".bst";
				}
				if (!File::Spec->file_name_is_absolute($bstFile)) {
					$bstFile = File::Spec->catfile($self->{'dirname'}, "$bstFile");
				}
				if (-f "$bstFile") {
					$self->{'dependencies'}{'biblio'}{$bibdb}{'bst'}{$bstFile} = 1;
				}
			}
		}
	}
	elsif ($macro =~ /^\\bibliography(.*)$/s) {		
		$bibdb = $1;
		$bibdb = $self->{'basename'} unless ($bibdb && $self->{'is_multibib'});
	}
	elsif ($macro eq '\\addbibresource') {		
		$bibdb = $self->{'basename'};
	}

	if ($bibdb) {
		foreach my $param (@_) {
			my $value = $param->{'text'};
			if ($value) {
				my $bibFile = "$value";
				if ($bibFile !~ /\.bib$/i) {
					$bibFile .= ".bib";
				}
				if (!File::Spec->file_name_is_absolute($bibFile)) {
					$bibFile = File::Spec->catfile($self->{'dirname'}, "$bibFile");
				}
				if (-f "$bibFile") {
					$self->{'dependencies'}{'biblio'}{$bibdb}{'bib'}{$bibFile} = 1;
				}
			}
		}
	}
	return '';
}

sub _discoverMacroDefinition($$$$) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;
	my $special = shift;
	if (!$special) {
		if ($macro =~ /^bibliographystyle/s ) {
			return '!{}';
		}
		elsif ($macro =~ /^bibliography/s ) {
			return '!{}';
		}
	}
	return undef;
}

sub _new($$) : method {
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
			'dirname' => File::Spec->rel2abs($_[1]),
			'expandMacro' => \&_expandMacro,
			'discoverMacroDefinition' => \&_discoverMacroDefinition,
			'dependencies' => {
				'biblio' => {},
				'tex' => {},
				'sty' => {},
				'cls' => [],
				'idx' => 0,
			},
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
