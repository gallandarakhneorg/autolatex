# autolatex - Flattener.pm
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

Flattener.pm - Make a TeX document flatten

=head1 DESCRIPTION

This tool creates a flattened version of a TeX document.
A flattened document contains a single TeX file, and all the
other related files are put inside the same directory of
the TeX file.

To use this library, type C<use AutoLaTeX::TeX::Flattener;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::TeX::Flattener;

$VERSION = '7.0';
@ISA = ('Exporter');
@EXPORT = qw( &flattenTeX ) ;
@EXPORT_OK = qw();

require 5.014;
use strict;
use utf8;
use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION);
use Config; # Perl configuration

use File::Spec;
use File::Basename;
use File::Copy;
use File::Path qw(make_path remove_tree);

use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::IntUtils;
use AutoLaTeX::TeX::TeXParser;

my %MACROS = (
	'input'				=> '!{}',
	'include'			=> '!{}',
	'usepackage'			=> '![]!{}',
	'RequirePackage'		=> '![]!{}',
	'documentclass'			=> '![]!{}',
	'includeanimatedfigure'		=> '![]!{}',
	'includeanimatedfigurewtex'	=> '![]!{}',
	'includefigurewtex'		=> '![]!{}',
	'includegraphics'		=> '![]!{}',
	'includegraphicswtex'		=> '![]!{}',
	'graphicspath'			=> '![]!{}',
	'mfigure'			=> '![]!{}!{}!{}!{}',
	'mfigure*'			=> '![]!{}!{}!{}!{}',
	'msubfigure'			=> '![]!{}!{}!{}',
	'msubfigure*'			=> '![]!{}!{}!{}',
	'mfiguretex'			=> '![]!{}!{}!{}!{}',
	'mfiguretex*'			=> '![]!{}!{}!{}!{}',
	'addbibresource'                => '![]!{}',
	);

=pod

=item B<flattenTeX($$\@$)>

This functions creates a flattened version of a TeX document.
A flattened document contains a single TeX file, and all the
other related files are put inside the same directory of
the TeX file.

=over 4

=item * C<rootTex> is the name of the TeX file to parse.

=item * C<outputDir> is the name of the output directory.

=item * C<images> is the array that lists the images of the document.

=item * C<usebiblio> indicates if the flattener should use Bibliography instead of inline bibliography.

=back

=cut
sub flattenTeX($$\@$) {
	my $input = shift;
	my $output = shift;
	my $imageDb = shift;
	my $usebiblio = shift;
	return '' unless ($output);

	if (-d "$output") {
		remove_tree("$output");
	}

	make_path("$output") or printErr(formatText(_T("{}: {}"), $output, $!));
	
	printDbg(formatText(_T('Analysing {}'), basename($input)));
	my $content = readFileLines("$input");

	my $listener = AutoLaTeX::TeX::Flattener->_new($input, $output, $imageDb, $usebiblio);

	my $parser = AutoLaTeX::TeX::TeXParser->new("$input", $listener);

	while (my ($k,$v) = each(%MACROS)) {
		$parser->addTextModeMacro($k,$v);
		$parser->addMathModeMacro($k,$v);
	}

	$parser->parse( $content );

	# Replace PREAMBLE content
	if ($listener->{'data'}{'expandedContent'}) {
		my $preamble = '';
		foreach my $entry (values %{$listener->{'preamble'}}) {
			if ($preamble) {
				$preamble .= "\n";
			}
			$preamble .= $entry;
		}
		$listener->{'data'}{'expandedContent'} =~ s/\Q%%%%% AUTOLATEX PREAMBLE\E/$preamble/;
	}

	# Create the main TeX file
	my $outputFile = File::Spec->catfile($output, basename($input));
	printDbg(formatText(_T('Writing {}'), basename($outputFile)));
	writeFileLines($outputFile, $listener->{'data'}{'expandedContent'});

	# Make the copy of the resources
	foreach my $cat ('bib', 'cls', 'bst', 'sty', 'figures') {
		while (my ($source, $target) = each(%{$listener->{'data'}{$cat}})) {
			$target = File::Spec->catfile("$output", "$target");
			printDbg(formatText(_T('Copying resource {} to {}'), basename($source), basename($target)));
			copy("$source", "$target") or printErr(formatText(_T("{} -> {}: {}"), $source, $target, $!));
		}
	}
}

sub _makeFilename($$;@) {
	my $self = shift;
	my $fn = shift || '';
	my $ext = shift || '';
	my $changed;
	do {
		$changed = 0;
		foreach my $e (@_) {
			if ($fn =~ /^(.+)\Q$e\E$/i) {
				$fn = $1;
				$changed = 1;
			}
		}
	}
	while ($changed);
	if ($ext && $fn !~ /\Q$ext\E$/i) {
		$fn .= $ext;
	}
	if (!File::Spec->file_name_is_absolute($fn)) {
		return File::Spec->catfile($self->{'dirname'}, $fn);
	}
	return $fn;
}

sub _isDocumentFile($) {
	my $self = shift;
	my $filename = shift;
	if (-f "$filename") {
		my $root = $self->{'dirname'};
		return "$filename" =~ /^\Q$root\E/s;
	}
	return 0;
}

sub _isDocumentPicture($) {
	my $self = shift;
	my $filename = shift;
	return 0;
}

sub _uniq($$) {
	my $self = shift;
	my $filename = shift;
	my $ext = shift;
	my $bn = basename($filename, $ext);
	my $name = $bn;
	my $i = 0;
	while (exists $self->{'data'}{'uniq'}{"$name$ext"}) {
		$name = "${bn}_$i";
		$i++;
	}
	$self->{'data'}{'uniq'}{"$name$ext"} = $filename;
	return $name;
}

sub _findPicture($) {
	my $self = shift;
	my $texname = shift;
	my $prefix = '';
	my $filename = $self->_makeFilename($texname,'');
	my @texexts = ('.pdftex_t','.pstex_t','.pdf_tex','.ps_tex','.tex');
	if (!-f $filename) {
		my @figexts = (	'.pdf', '.eps', '.ps',
				'.png', '.jpeg', '.jpg', '.gif', '.bmp');
		my @exts = (@figexts,@texexts);
		my $ofilename = $filename;

		# Search if the registered images
		my $template = basename($filename, @exts);
		my %filenames = ();
		if ($self->{'images'}) {
			my $ext;
			for(my $k=0; $k<@{$self->{'includepaths'}}; $k++) {
				my $path = $self->{'includepaths'}[$k];
				for(my $j=0; $j<@{$self->{'images'}}; $j++)  {
					my $img = $self->{'images'}[$j];
					for(my $i=0; $i<@figexts; $i++)  {
						$ext = $figexts[$i];
						my $fullname = File::Spec->catfile($path,"$template$ext");
						$fullname = $self->_makeFilename($fullname,'');
						if (-f $fullname) {
							$filenames{$fullname} = 0;
						}
					}
					for(my $i=0; $i<@texexts; $i++)  {
						$ext = $texexts[$i];
						my $fullname = File::Spec->catfile($path,"$template$ext");
						$fullname = $self->_makeFilename($fullname,'');
						if (-f $fullname) {
							$filenames{$fullname} = 1;
						}
					}
				}
			}
		}
		
		if (!%filenames) {
			# Search in the folder, from the document directory.
			$template = File::Spec->catfile(dirname($ofilename), basename($ofilename, @exts));
			my $ext;
			for(my $i=0; $i<@figexts; $i++)  {
				$ext = $figexts[$i];
				my $fn = "$template$ext";
				if (-f $fn) {
					$filenames{$fn} = 0;
				}
			}
			for(my $i=0; $i<@texexts; $i++)  {
				$ext = $texexts[$i];
				my $fn = "$template$ext";
				if (-f $fn) {
					$filenames{$fn} = 1;
				}
			}
		}

		if (!%filenames) {
			printErr(formatText(_T('Picture not found: {}'), $texname));
		}
		else {
			my $ext;
			my @selectedName1 = ();
			my $selectedName2 = undef;
			foreach $filename (keys %filenames) {
				$filename =~ /(\.[^.]+)$/s;
				$ext = $1 || '';
				$texname = $self->_uniq($filename, $ext).$ext;
				if ($filenames{$filename}) {
					if (!@selectedName1) {
						@selectedName1 = ($texname,$filename);
					}
				}
				else {
					$self->{'data'}{'figures'}{$filename} = $texname;
					$selectedName2 = $texname;
				}
			}
			if (@selectedName1) {
				($texname, $filename) = @selectedName1;
				printDbg(formatText(_T('Embedding {}'), $filename));
				my $filecontent = readFileLines("$filename");
				# Replacing the filename in the TeX file
				while (my ($localFile, $texfile) = each(%{$self->{'data'}{'figures'}})) {
					$filecontent =~ s/\Q$localFile\E/$texfile/g;
				}
				$prefix .="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
				       "%%% BEGIN FILE: ".basename($texname)."\n".
				       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
					"\\begin{filecontents*}{".basename($texname)."}\n".
					$filecontent.
					"\\end{filecontents*}\n".
					"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n\n";
				$self->{'preamble'}{'filecontents'} = "\\usepackage{filecontents}";
			}
			elsif ($selectedName2) {
				$texname = $selectedName2;
			}
		}
	}
	else {
		$texname =~ /(\.[^.]+)$/s;
		my $ext = $1 || '';
		$texname = $self->_uniq($filename, $ext).$ext;
		if (!arrayContains(@texexts, $ext)) {
			$self->{'data'}{'figures'}{$filename} = $texname;
		}
	}

	return ($texname,$prefix);
}

sub _expandMacro($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $macro = shift;

	if (		$macro eq '\\usepackage' || $macro eq '\\RequirePackage') {
		my $texname = $_[1]->{'text'};
		my $filename = $self->_makeFilename("$texname", '.sty');

		my $ret = '';

		if ($texname eq 'biblatex') {
			if (!$self->{'usebiblio'}) {
				my $filename = $self->_makeFilename($self->{'basename'}, '.bbl', '.tex');
				if (-f "$filename") {
					printDbg(formatText(_T('Embedding {}'), $filename));
					$self->{'preamble'}{'filecontents'} = "\\usepackage{filecontents}";
					$ret .="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
					       "%%% BEGIN FILE: ".basename($filename)."\n".
					       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
						"\\begin{filecontents*}{".basename($filename)."}\n".
						readFileLines("$filename").
						"\\end{filecontents*}\n".
						"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n\n";
				}
				else {
					printErr(formatText(_T('File not found: {}'), $filename));
				}
			}
		}
		elsif ($self->_isDocumentFile($filename)) {
			printDbg(formatText(_T('Embedding {}'), $filename));
			$self->{'preamble'}{'filecontents'} = "\\usepackage{filecontents}";
			$ret .="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
			       "%%% BEGIN FILE: ".basename($filename)."\n".
			       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
				"\\begin{filecontents*}{".basename($filename)."}\n".
				readFileLines("$filename").
				"\\end{filecontents*}\n".
				"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n\n";
		}
		$ret .= $macro;
		$ret .= '['.$_[0]->{'text'}.']' if ($_[0]->{'text'});
		$ret .= '{'.$texname.'}';
		return $ret;
	}
	elsif (		$macro eq '\\documentclass') {
		my $texname = $_[1]->{'text'};
		my $filename = $self->_makeFilename("$texname", '.cls');
		if ($self->_isDocumentFile($filename)) {
			$texname = $self->_uniq($filename,'.cls');
			$self->{'data'}{'cls'}{$filename} = "$texname.cls";
		}
		my $ret = $macro;
		$ret .= '['.$_[0]->{'text'}.']' if ($_[0]->{'text'});
		$ret .= '{'.$texname.'}';
		$ret .= "\n\n%%%%% AUTOLATEX PREAMBLE\n\n";
		return $ret;
	}
	elsif (		($macro eq '\\includegraphics')
		||	($macro eq '\\includeanimatedfigure')
		||	($macro eq '\\includeanimatedfigurewtex')
		||	($macro eq '\\includefigurewtex')
		||	($macro eq '\\includegraphicswtex')) {
		my ($texname,$prefix) = $self->_findPicture($_[1]->{'text'});
		my $ret = $prefix.$macro;
		$ret .= '['.$_[0]->{'text'}.']' if ($_[0]->{'text'});
		$ret .= '{'.$texname.'}';
		return $ret;
	}
	elsif (		$macro eq '\\graphicspath') {
		my @paths = ();
		my $t = $_[1]->{'text'}; 
		while ($t && $t =~ /^\s*(?:(?:\{([^\}]+)\})|([^,]+))\s*[,;]?\s*(.*)$/g) {
			my $prev = "$t";
			(my $path, $t) = (($1||$2), $3);
			push @paths, "$path";
		}
		unshift @{$self->{'includepaths'}}, @paths;
		return '\\graphicspath{{.}}';
	}
	elsif (		$macro eq '\\mfigure' || $macro eq '\\mfigure*' ||
			$macro eq '\\mfiguretex' || $macro eq '\\mfiguretex*') {
		my ($texname,$prefix) = $self->_findPicture($_[2]->{'text'});
		my $ret = $prefix.$macro;
		$ret .= '['.$_[0]->{'text'}.']' if ($_[0]->{'text'});
		$ret .= '{'.$_[1]->{'text'}.'}';
		$ret .= '{'.$texname.'}';
		$ret .= '{'.$_[3]->{'text'}.'}';
		$ret .= '{'.$_[4]->{'text'}.'}';
		return $ret;
	}
	elsif (		$macro eq '\\msubfigure' || $macro eq '\\msubfigure*') {
		my ($texname,$prefix) = $self->_findPicture($_[2]->{'text'});
		my $ret = $prefix.$macro;
		$ret .= '['.$_[0]->{'text'}.']' if ($_[0]->{'text'});
		$ret .= '{'.$_[1]->{'text'}.'}';
		$ret .= '{'.$texname.'}';
		$ret .= '{'.$_[3]->{'text'}.'}';
		return $ret;
	}
	elsif (		$macro eq '\\include' || $macro eq '\\input') {
		my $filename = $self->_makeFilename($_[0]->{'text'},'.tex');
		my $subcontent = readFileLines($filename);
		$subcontent .= "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
		               "%%% END FILE: $filename\n".
		               "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n";

		$parser->putBack($subcontent);
		return "\n\n".
		       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
		       "%%% BEGIN FILE: $filename\n".
		       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n";
	}
	elsif ($macro =~ /^\\bibliographystyle(.*)$/s ) {
		if ($self->{'usebiblio'}) {
			my $bibdb = $1;
			$bibdb = $self->{'basename'} unless ($bibdb);
			my $texname = $_[0]->{'text'};
			my $filename = $self->_makeFilename("$texname", '.bst');
			if ($self->_isDocumentFile($filename)) {
				$texname = $self->_uniq($filename,'.bst');
				$self->{'data'}{'bst'}{$filename} = "$texname.bst";
			}
			my $ret = $macro;
			$ret .= '{'.$texname.'}';
			return $ret;
		}
		return '';
	}
	elsif ($macro =~ /^\\bibliography(.*)$/s ) {
		my $bibdb = $1;
		$bibdb = $self->{'basename'} unless ($bibdb);
		if ($self->{'usebiblio'}) {
			my $texname = $_[0]->{'text'};
			my $filename = $self->_makeFilename("$texname",'.bib');
			if ($self->_isDocumentFile($filename)) {
				$texname = $self->_uniq($filename,'.bib');
				$self->{'data'}{'bib'}{$filename} = "$texname.bib";
			}
			my $ret = $macro;
			$ret .= '{'.$texname.'}';
			return $ret;
		}
		else {
			my $bblFile = "$bibdb.bbl";
			if (!File::Spec->file_name_is_absolute($bblFile)) {
				$bblFile = File::Spec->catfile($self->{'dirname'}, "$bblFile");
			}
			if (-f "$bblFile") {
				my $ret = "\n\n".
				       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n".
				       "%%% BEGIN FILE: ".basename($bblFile)."\n".
				       "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n";
				$ret .= readFileLines("$bblFile");
				$ret .= "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n";
				return $ret;
			}
			else {
				printErr(formatText(_T('File not found: {}'), $bblFile));
			}
		}
	}
	elsif (		$macro eq '\\addbibresource') {
		if ($self->{'usebiblio'}) {
			my $texname = $_[1]->{'text'};
			my $filename = $self->_makeFilename("$texname", '.bib');
			if ($self->_isDocumentFile($filename)) {
				$texname = $self->_uniq($filename,'.bib');
				$self->{'data'}{'bib'}{$filename} = "$texname.bib";
			}
			my $ret = $macro;
			$ret .= '{'.$texname.'}';
			return $ret;
		}
		else {
			return '';
		}
	}

	return $macro;
}

sub _outputString($$@) : method {
	my $self = shift;
	my $parser = shift;
	my $text = shift;
	if (defined($text)) {
		$self->{'data'}{'expandedContent'} .= $text;
	}
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

sub _new($$$$) : method {
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
			'dirname' => File::Spec->rel2abs(dirname($_[0])),
			'file' => $_[0],
			'output' => $_[1],
			'images' => $_[2],
			'includepaths' => [ File::Spec->curdir() ],
			'usebiblio' => $_[3],
			'outputString' => \&_outputString,
			'expandMacro' => \&_expandMacro,
			'discoverMacroDefinition' => \&_discoverMacroDefinition,
			'preamble' => {},
			'data' => {
				'figures' => {},
				'cls' => {},
				'sty' => {},
				'bib' => {},
				'bst' => {},
				'expandedContent' => '',
				'uniq' => {},
			}
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
