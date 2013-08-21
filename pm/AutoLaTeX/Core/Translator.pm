# autolatex - Translator.pm
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

Translator.pm - Translator Utilities

=head1 DESCRIPTION

Permits to get translators and to resolve conflicts on them.

To use this library, type C<use AutoLaTeX::Core::Translator;>.

=head1 FUNCTIONS

The provided functions are:

=over 4

=cut
package AutoLaTeX::Core::Translator;

$VERSION = '9.0';
@ISA = ('Exporter');
@EXPORT = qw( &getTranslatorFilesFrom &getLoadableTranslatorList &getTranslatorList
	      &detectConflicts @ALL_LEVELS 
	      &makeTranslatorHumanReadable &extractTranslatorNameComponents
	      &readTranslatorFile &runRootTranslator &runTranslator &loadTranslator
              &loadTranslatorsFromConfiguration &loadTranslatableImageList ) ;
@EXPORT_OK = qw();

use strict;

use vars qw(@ISA @EXPORT @EXPORT_OK $VERSION @ALL_LEVELS);
use Carp;
use File::Spec;
use File::Basename;
use File::Path qw(make_path remove_tree);
use File::Copy;

use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::Config;
use AutoLaTeX::Core::Locale;
use AutoLaTeX::Core::OS;

# Sorted list of the levels
our @ALL_LEVELS = ('system', 'user', 'project');

# Data for the translators
my %ROOT_TRANSLATORS = ();

=pod

=item * extractTranslatorNameComponents($)

Parse a complete translator name to extract the components.
The name must have the syntax:
=over 8

=item * C<"I<source>2I<target>">

=item * C<"I<source>2I<target>+I<target2>">

=item * C<"I<source>2I<target>_I<variante>">

=item * C<"I<source>2I<target>+I<target2>_I<variante>">

=back

I<Parameters:>

=over 8

=item * The name to parse (string).

=back

I<Returns:> a hashtable containing the components of the name. The keys are:

=over 8

=item * C<name> is the name of the translator.

=item * C<full-source> is the decoded of the source type.

=item * C<source> is the source type given in the parameter of the function.

=item * C<target> is the decoded target.

=item * C<variante> is the decoded variante.

=item * C<basename> is the basename of the translator.

=back

=cut
sub extractTranslatorNameComponents($) {
	my $name = shift;
	if ($name =~ /^([a-zA-Z+-]+)2([a-zA-Z0-9-]+)(?:\+([a-zA-Z0-9+-]+))?(?:_(.*))?$/) {
		my $source = $1;
		my $target = $2;
		my $target2 = $3||'';
		my $variante = $4||'';
		my $osource = "$source";
		my $basename = "${source}2${target}${target2}";
		if ($target2) {
			if ($target2 eq 'tex') {
				$source = "ltx.$source";
			}
			elsif ($target2 eq 'layers') {
				$source = "layers.$source";
			}
			elsif ($target2 eq 'layers+tex' || $target2 eq 'tex+layers') {
				$source = "layers.ltx.$source";
			}
			else {
				$target .= "+$target2";
			}
		}
		return { 'name' => $name, 'full-source' => $source, 'source' => $osource, 'target' => $target, 'variante' => $variante, 'basename' => $basename };
	}
	return undef;
}

=pod

=item * makeTranslatorHumanReadable($)

Replies a human readable string that corresponds to the specified translator data.

I<Parameters:>

=over 8

=item * C<description> is the description of the translator (hasharray). The value of the parameter may be obtained with C<extractTranslatorNameComponents()>.

=back

I<Returns:> the description of the translator.

=cut
sub makeTranslatorHumanReadable($) {
	my $data = shift;
	if ($data->{'variante'}) {
		return locGet(_T("Translate {} to {} with {} alternative"),
					$data->{'full-source'},
					$data->{'target'},
					$data->{'variante'});
	}
	else {
		return locGet(_T("Translate {} to {}"),
					$data->{'full-source'},
					$data->{'target'});
	}
}

=pod

=item * getTranslatorFilesFrom($)

Replies the descriptions of the translator files installed on the system.

I<Parameters:>

=over 8

=item * C<configuration> (hashtable) is the current configuration of AutoLaTeX.

=item * C<directory> (string) is the path to the directory to explore.

=item * C<fileSet> (hashtable) is the associative array in which the discovered translators will be put.

=item * C<recursive> (boolean) indicates if the function must recurse in the directories.

=item * C<warn> (boolean) indicates if the warning may be output or not.

=item * C<onlyincluded> (boolean) indicates if only the included translated will be considered as discovered.

=item * C<level> (string) is the level to consider (see C<@ALL_LEVELS>).

=back

I<Returns:> nothing.

=cut
sub getTranslatorFilesFrom(\%$\%$$$;$) {
	my $configuration = shift;
	my $filename = shift;
	my $fileSet = shift;
	my $recursive = shift;
	my $warn = shift;
	my $onlyincluded = shift;
	my $level = shift || 'unknown';
	my $ispdfmode = $configuration->{'generation.generation type'} eq 'pdf';
	local *DIR;
	if (-d "$filename") {
		my @dirs = ( "$filename" );
		while (@dirs) {
			my $dirname = shift @dirs;
			locDbg(_T("Get translator list from {}"),$dirname);
			if (opendir(*DIR,"$dirname")) {
				while (my $file = readdir(*DIR)) {
					if ( $file ne File::Spec->curdir() && $file ne File::Spec->updir() ) {
						my $fullname = File::Spec->catfile("$dirname","$file");
						if (-d "$fullname") {
							push @dirs, "$fullname" if ($recursive);
						}
						elsif ($file =~ /^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef$/i) {
							my $scriptname = "$1";
							if ($onlyincluded) {
								$fileSet->{"$scriptname"} = extractTranslatorNameComponents($scriptname);
								$fileSet->{"$scriptname"}{'human-readable'} = makeTranslatorHumanReadable($fileSet->{"$scriptname"});
								$fileSet->{"$scriptname"}{'file'} = "$fullname";
								$fileSet->{"$scriptname"}{'level'} = "$level";
								$fileSet->{"$scriptname"}{'ispdfmode'} = $ispdfmode;
							}					
							else {
								$fileSet->{"$scriptname"} = "$fullname";
							}
						}
					}
				}
				closedir(*DIR);
			}
			else {
				printWarn("$dirname:","$!");
			}
		}
	}
	elsif ($warn) {
		printWarn("$filename:","$!");
	}
	1;
}

=pod

=item * resolveConflicts($)

Resolve conflicts between translator inclusions.

I<Parameter:>

=over 8

=item * C<includedTranslators> (hashtable) is the loaded translators. The keys are the names of the translators, and the values are the filenames of the translators.

=back

I<Returns:> nothing.

=cut
sub resolveConflicts(\%) {
	my $includedTranslators = shift;
	my %bysources = ();
	# The targets with "*+tex" are translated into sources "ltx.*"
	# The targets with "*+layers" are translated into sources "layers.*"
	while (my ($trans,$transfile) = each (%{$includedTranslators})) {
		my $components = extractTranslatorNameComponents($trans);
		if ($components) {
			if (!$bysources{$components->{'full-source'}}) {
				$bysources{$components->{'full-source'}} = [];
			}
			push @{$bysources{$components->{'full-source'}}}, { 
				'source' => $components->{'source'},
				'target' => $components->{'target'},
				'variante' => $components->{'variante'},
				'filename' => "$transfile" };
		}
	}

	while (my ($source,$trans) = each(%bysources)) {
		if (@{$trans}>1) {
			my $msg = '';
			my ($excludemsg,$excludename);
			foreach my $t (@{$trans}) {
				$msg .= ",\n" if ($msg);
				$msg .= makeTranslatorHumanReadable($t);
				if (!$excludename) {
					$excludename = $t->{'source'}."2".$t->{'target'};
					$excludename .= "_".$t->{'variante'} if ($t->{'variante'});
				}
				if (!$excludemsg) {
					$excludemsg = "[$excludename]\ninclude module = no\n";
				}
			}
			printErr(locGet(_T("Several possibilities exist for generating a figure from a {} file:\n{}\n\nYou must specify which to include (resp. exclude) with --include (resp. --exclude).\n\nIt is recommended to update your {} file with the following configuration for each translator to exclude (example on the translator {}):\n\n{}\n"),
				$source,
				$msg,
				getUserConfigFilename(),
				$excludename,
				$excludemsg));
		}
	}
	1;
}

=pod

=item B<detectConflicts(\%)>

Replies the list of the translators that are in conflict.

I<Parameters:>

=over 8

=item * List of translator pairs (translator name => hashtable)

=back

I<Returns:> a hashtable containing (level => hash of translator descriptions) pairs.

=cut
sub detectConflicts(\%) {
	die('first parameter of detectConflicts() is not a hash')
		unless (isHash($_[0]));
	my %bysources = ();
	# Build the list of included translators
	while (my ($name,$data) = each(%{$_[0]})) {
		# By default a module is included
		for(my $i=0; $i<@ALL_LEVELS; $i++) {
			my $level = $ALL_LEVELS[$i];
			if ($data->{'included'}{$level}) {
				$bysources{$level}{$data->{'full-source'}}{$data->{'name'}} = $data;
				# Propagate the inclusion to the following levels
				for(my $j=$i+1; $j<@ALL_LEVELS; $j++) {
					my $flevel = $ALL_LEVELS[$j];
					$bysources{$flevel}{$data->{'full-source'}}{$data->{'name'}} = $data;
				}
			}
			elsif (defined($data->{'included'}{$level})) {
				# Propagate the non inclusion to the following levels
				# This action cancels previous propagation of included translators
				for(my $j=$i; $j<@ALL_LEVELS; $j++) {
					my $flevel = $ALL_LEVELS[$j];
					if ($bysources{$flevel}{$data->{'full-source'}}) {
						delete $bysources{$flevel}{$data->{'full-source'}}{$data->{'name'}};
					}
				}
			}
			elsif ($i==0) {
				# By default a module is included
				# Propagate the inclusion to the following levels
				$bysources{$level}{$data->{'full-source'}}{$data->{'name'}} = $data;
				for(my $j=$i+1; $j<@ALL_LEVELS; $j++) {
					my $flevel = $ALL_LEVELS[$j];
					$bysources{$flevel}{$data->{'full-source'}}{$data->{'name'}} = $data;
				}
			}
		}
	}

	# Remove the translators that are not under conflict
	foreach my $level (@ALL_LEVELS) {
		foreach my $source (keys %{$bysources{$level}}) {
			my @keys = keys %{$bysources{$level}{$source}};
			if (@keys<=1) {
				delete $bysources{$level}{$source};
			}
		}
		unless ($bysources{$level}) {
			delete $bysources{$level};
		}
	}

	return %bysources;
}

=pod

=item B<getLoadableTranslatorList(\%)>

Replies the list of the translators that could be loaded.

I<Parameters:>

=over 8

=item * hashtable that contains the current configuration, and that will
be updating by this function.

=back

I<Returns:> a hashtable containing (translator name => translator file) pairs.

=cut
sub getLoadableTranslatorList(\%) {
	local *DIR;

	my %includes = ();

	# Load distribution modules
	my $filename = File::Spec->catfile(getAutoLaTeXDir(),"translators");
	locDbg(_T("Get loadable translators from {}"),$filename);
	printDbgIndent();
	opendir(*DIR,"$filename")
		or printErr("$filename:","$!");
	while (my $file = readdir(*DIR)) {
		my $fullname = File::Spec->rel2abs(File::Spec->catfile("$filename","$file"));
		if (($file ne File::Spec->curdir())&&($file ne File::Spec->updir())&&
		    ($file =~ /^(.*)\.transdef$/i)) {
			my $scriptname = "$1";
			if ((!exists $_[0]->{"$scriptname.include module"})||
			    (cfgBoolean($_[0]->{"$scriptname.include module"}))) {
				$includes{"$scriptname"} = "$fullname";
			}
			else {
				locDbg(_T("Translator {} is ignored"),$scriptname);
			}
		}
	}
	closedir(*DIR);
	printDbgUnindent();

	# Load user modules recursively from ~/.autolatex/translators
	getTranslatorFilesFrom(
		%{$_[0]},
		File::Spec->catfile(getUserConfigDirectory(),"translators"),
		%includes,
		1, # recursion
		0, # no warning
		0, # only included translators
		'user' # configuration level
		);

	# Load user modules non-recursively the paths specified inside the configurations
	if ($_[0]->{'generation.translator include path'}) {
		my @paths = ();
		if ((isArray($_[0]->{'generation.translator include path'}))||
		    (isHash($_[0]->{'generation.translator include path'}))) {
			@paths = @{$_[0]->{'generation.translator include path'}};
		}
		else  {
			push @paths, $_[0]->{'generation.translator include path'};
		}
		foreach my $path (@paths) {
			getTranslatorFilesFrom(
				%{$_[0]},
				"$path",
				%includes,
				0, # no recursion
				1, # warning
				0, # only included translators
				'user' # configuration level
			);
		}
	}

	resolveConflicts(%includes);

	return %includes;
}

=pod

=item B<getTranslatorList(\%;$)>

Replies the list of the translators and their status.

I<Parameters:>

=over 8

=item * hashtable that contains the configuration.

=item * recurse on user inclusion directories

=back

I<Returns:> a hashtable containing (translator name => { 'file' => translator file,
'level' => installation level, 'ispdfmode' => boolean value indicating that
the pdf mode is one } ) pairs.

=cut
sub getTranslatorList(\%;$) {
	local *DIR;
	die('first parameter of getTranslatorList() is not a hash')
		unless(isHash($_[0]));

	my $recurse = $_[1];
	$recurse = 1 unless (defined($recurse));

	my $ispdfmode = ($_[0]->{'generation.generation type'} || 'pdf') eq 'pdf';

	my %translators = ();

	# Load distribution modules
	my $filename = File::Spec->catfile(getAutoLaTeXDir(),"translators");
	locDbg(_T("Get translators from {}"),$filename);
	printDbgIndent();
	opendir(*DIR,"$filename") or printErr("$filename:","$!");
	while (my $file = readdir(*DIR)) {
		my $fullname = File::Spec->rel2abs(File::Spec->catfile("$filename","$file"));
		if (($file ne File::Spec->curdir())&&($file ne File::Spec->updir())&&
		    ($file =~ /^(.*)\.transdef$/i)) {
			my $scriptname = "$1";
			$translators{"$scriptname"} = extractTranslatorNameComponents($scriptname);
			$translators{"$scriptname"}{'human-readable'} = makeTranslatorHumanReadable($translators{"$scriptname"});
			$translators{"$scriptname"}{'file'} = "$fullname";
			$translators{"$scriptname"}{'level'} = 'system';
			$translators{"$scriptname"}{'ispdfmode'} = $ispdfmode;
		}
	}
	closedir(*DIR);
	printDbgUnindent();

	if ($recurse) {
		# Load user modules recursively from ~/.autolatex/translators
		getTranslatorFilesFrom(
			%{$_[0]},
			File::Spec->catfile(getUserConfigDirectory(),"translators"),
			%translators,
			1, # recursion
			0, # no warning
			1, # all included and not-included translators
			'user' # configuration level
			);

		# Load user modules non-recursively the paths specified inside the configurations
		if ($_[0]->{'generation.translator include path'}) {
			my @paths = ();
			if ((isArray($_[0]->{'generation.translator include path'}))||
			    (isHash($_[0]->{'generation.translator include path'}))) {
				@paths = @{$_[0]->{'generation.translator include path'}};
			}
			else  {
				push @paths, $_[0]->{'generation.translator include path'};
			}
			foreach my $path (@paths) {
				getTranslatorFilesFrom(
					%{$_[0]},
					"$path",
					%translators,
					0, # no recursion
					1, # warning
					1, # all included and not-included translators
					'user' # configuration level
				);
			}
		}
	} # if ($recurse)

	return %translators;
}

=pod

=item B<readTranslatorFile($$)>

Replies the content of a translator definition file.

I<Parameters:>

=over 8

=item * C<file> is the name of the file to parse.

=item * C<ispdfmode> indicates of AutoLaTeX is in pdf mode (true) or in eps mode (false).

=back

I<Returns:> a hashtable containing the entries of the definition.

=cut
sub readTranslatorFile($$) {
	my $file = shift || confess('you must pass a filename to readTranslatorFile($$)');
	my $ispdfmode = shift;
	my %content = ();
	local *FILE;
	open(*FILE, "< $file") or printErr("$file: $!");
	my $curvar = '';
	my $eol = undef;
	my $lineno = 0;
	while (my $line = <FILE>) {
		$lineno++;
		if ($eol) {
			if ($line =~ /^\Q$eol\E\s*$/) {
				$eol = undef;
				$curvar = undef;
			}
			elsif ($curvar) {
				$content{"$curvar"}{'value'} .= $line;
			}
		}
		elsif ($line !~ /^\s*[#;]/) {
			if ($line =~ /^\s*([azA-Z0-9_]+)(?:\s+for\s+((?:pdf)|(?:eps)))?\s*=\<\<([a-zA-Z0-9_]+)\s*(.*?)\s*$/) {
				($curvar, my $mode, $eol, my $value) = ($1, $2, $3, $4);
				if (!$mode ||
				    ($ispdfmode && lc($mode) eq 'pdf') ||
				    (!$ispdfmode && lc($mode) eq 'eps')) {
					$curvar = uc($curvar);
					$content{"$curvar"} = {
						'lineno' => $lineno,
						'value' => $value,
					};
				}
				else {
					$curvar = '';
				}
			}
			elsif ($line =~ /^\s*([azA-Z0-9_]+)(?:\s+for\s+((?:pdf)|(?:eps)))?\s*=\s*(.*?)\s*$/i) {
				my ($var, $mode, $value) = ($1, $2, $3);
				if (!$mode ||
				    ($ispdfmode && lc($mode) eq 'pdf') ||
				    (!$ispdfmode && lc($mode) eq 'eps')) {
					$curvar = undef;
					$eol = undef;
					$content{uc("$var")} = {
						'lineno' => $lineno,
						'value' => $value,
					};
				}
			}
			elsif ($line !~ /^\s*$/) {
				printErr(locGet("Line outside a definition ({}:{}).",$lineno, $file));
			}
		}
	}
	close(*FILE);
	if ($eol) {
		printErr(locGet(_T("The block for the variable '{}' is not closed. Keyword '{}' was not found ({}:{})."),
				$curvar, $eol, $file, $lineno));
	}


	# Translate the values into suitable Perl objects
	if (exists $content{'INPUT_EXTENSIONS'}{'value'}) {
		my @exts = split(/\s+/, ($content{'INPUT_EXTENSIONS'}{'value'} || ''));
		$content{'INPUT_EXTENSIONS'}{'value'} = [];
		foreach my $e (@exts) {
			if ($e !~ /^\^s*$/) {
				if ($e !~ /^[\.+]/) {
					$e = ".$e";
				}
				push @{$content{'INPUT_EXTENSIONS'}{'value'}}, $e;
			}
		}
	}

	if (exists $content{'OUTPUT_EXTENSIONS'}{'value'}) {
		my @exts = split(/\s+/, ($content{'OUTPUT_EXTENSIONS'}{'value'} || ''));
		$content{'OUTPUT_EXTENSIONS'}{'value'} = [];
		foreach my $e (@exts) {
			if ($e !~ /^\^s*$/) {
				if ($e !~ /^\./) {
					$e = ".$e";
				}
				push @{$content{'OUTPUT_EXTENSIONS'}{'value'}}, $e;
			}
		}
	}

	if (exists $content{'TRANSLATOR_PERL_DEPENDENCIES'}{'value'}) {
		my @exts = split(/\s+/, ($content{'TRANSLATOR_PERL_DEPENDENCIES'}{'value'} || ''));
		$content{'TRANSLATOR_PERL_DEPENDENCIES'}{'value'} = [];
		while (@exts) {
			my $e = shift @exts;
			if ($exts[0] &&
			    ( ($exts[0] =~ /^\Q'\E.*?\Q'\E$/) ||
			      ($exts[0] =~ /^\Qqw(\E.+?\Q)\E$/) ||
			      ($exts[0] =~ /^\Qqw{\E.+?\Q}\E$/))) {
				my $p = shift @exts;
				$e .= " $p";
			}
			push @{$content{'TRANSLATOR_PERL_DEPENDENCIES'}{'value'}}, $e;
		}
	}

	if (exists $content{'FILES_TO_CLEAN'}{'value'}) {
		my @patterns = split(/\s+/, ($content{'FILES_TO_CLEAN'}{'value'} || ''));
		$content{'FILES_TO_CLEAN'}{'value'} = [];
		foreach my $p (@patterns) {
			if ($p !~ /^\^s*$/) {
				push @{$content{'FILES_TO_CLEAN'}{'value'}}, $p;
			}
		}
	}

	return \%content;
}

=pod

=item B<runRootTranslator(\%$$\%$;$)>

Run the translator on a file as a root translator.

I<Parameters:>

=over 8

=item * C<configuration> is AutoLaTeX configuration.

=item * C<name> is name of the translator.

=item * C<in> is the name of the input file.

=item * C<translators> definition of all the translators.

=item * C<force> indicates if the translation is always run (true) or only if the source file is more recent than the target file.

=back

I<Returns:> true if a file was created; otherwise false.

=cut

sub runRootTranslator(\%$$\%$) {
	my $configuration = shift || confess("configuration is mandatory");
	my $transname = shift || confess("transname is mandatory");
	my $in = shift || confess("input is mandatory");
	my $translators = shift || confess("translators are mandatory");
	my $force = shift;

	my $out;
	if ($in =~ /^(.*)\.[^.]+$/) {
		$out = "$1";
	}
	else {
		$out = "$in";
	}
	$out .= $translators->{"$transname"}{'transdef'}{'OUTPUT_EXTENSIONS'}{'value'}[0] || '';

	$ROOT_TRANSLATORS{'configuration'} = $configuration;
	$ROOT_TRANSLATORS{'translators'} = $translators;
	$ROOT_TRANSLATORS{'force'} = $force;
	$ROOT_TRANSLATORS{'loglevel'} = 1;

	return _runTranslator(
		$configuration,
		$translators,
		$transname,
		$in, 
		$out,
		$force,
		1);
}

=pod

=item B<runTranslator($$$)>

Run the translator on a file.

I<Parameters:>

=over 8

=item * C<name> is name of the translator.

=item * C<in> is the name of the input file.

=item * C<out> is the name of the output file.

=back

I<Returns:> true if a file was created; otherwise false.

=cut
sub runTranslator($$$) {
	my $transname = shift || confess("name is mandatory");
	my $in = shift || confess("input is mandatory");
	my $out = shift || confess("output is mandatory");
	if (!$ROOT_TRANSLATORS{'translators'}) {
		printErr(locGet(_T("You cannot call runTranslator() outside the call stack of runRootTranslator().")));
	}
	printDbgIndent();
	$ROOT_TRANSLATORS{'loglevel'}++;
	my $r = _runTranslator(
			$ROOT_TRANSLATORS{'configuration'},
			$ROOT_TRANSLATORS{'translators'},
			$transname,
			$in,
			$out,
			$ROOT_TRANSLATORS{'force'},
			$ROOT_TRANSLATORS{'loglevel'});
	$ROOT_TRANSLATORS{'loglevel'}--;
	printDbgUnindent();
	return $r;
}

# Private translator function
sub _runTranslator($$$$$$$) {
	my $configuration = shift || confess("configuration is mandatory");
	my $translators = shift || confess("translators are mandatory");
	my $transname = shift || confess("transname is mandatory");
	my $in = shift || confess("input is mandatory");
	my $out = shift || confess("output is mandatory");
	my $force = shift;
	my $logLevel = shift;
	my $ispdfmode = (($configuration->{'generation.generation type'} || 'pdf') eq 'pdf');
	my $isepsmode = !$ispdfmode;

	$in = File::Spec->rel2abs("$in");
	$out = File::Spec->rel2abs("$out");
	
	if (! -r "$in") {
		printErr(locGet(_T("{}: file not found or not readable."), $in));
	}

	if (!exists $translators->{"$transname"} ||
	    !exists $translators->{"$transname"}{'transdef'} ||
	    !$translators->{"$transname"}{'transdef'}) {
		# The requested translator was not enabled by the user.
		# We try to enable it on the fly.
		loadTranslator($transname, $translators);
	}

	# Try to avoid the translation if the source file is no more recent than the target file.
	if (!$force) {
		my $inChange = lastFileChange("$in");
		my $outChange = lastFileChange("$out");
		if (!defined($outChange)) {
			# No out file, try to detect other types of generated files
			local *DIR;
			my $dirname = dirname("$out");
			if (opendir(*DIR, "$dirname")) {
				my $fn;
				my $ext = $translators->{"$transname"}{'transdef'}{'OUTPUT_EXTENSIONS'}{'value'}[0] || '';
				my $bn = basename($out, $ext);
				while (!defined($outChange) && ($fn = readdir(*DIR))) {
					if ($fn ne File::Spec->updir() && $fn ne File::Spec->curdir()
						&& $fn =~ /^\Q${bn}_\E/s) {
						my $ffn = File::Spec->catfile("$dirname", "$fn");
						my $t = lastFileChange("$ffn");
						if (defined($t) && (!defined($outChange) || $t>$outChange)) {
							$outChange = $t;
						}
					}
				}
				closedir(*DIR);
			}
		}

		if (defined($outChange) && $inChange<$outChange) {
			# No need to translate again
			printDbgFor(2, locGet(_T("{} is up-to-date."), basename($out)));
			return 1;
		}
	}

	if ($logLevel) {
		printDbgFor($logLevel, locGet(_T("{} -> {}"), basename($in), basename($out)));
	}

	if ($translators->{"$transname"}{'transdef'}{'COMMAND_LINE'}{'value'}) {
		# Run an external command line
		my $cli = ($translators->{"$transname"}{'transdef'}{'COMMAND_LINE'}{'value'} || '');
		# Create the environment of variables for the CLI
		my %environment = (%{$translators->{"$transname"}{'environment_variables'}});
		while (my ($k,$v) = each(%{$configuration})) {
			if (!isArray($v) && !isHash($v)) {
				$environment{$k} = $v;
			}
		}
		$environment{'in'} = $in;
		$environment{'out'} = $out;
		# Create the CLI to run
		my @cli = parseCLI(\%environment, "$cli");
		
		if (getDebugLevel>=4) {
			$cli = '$';
			foreach my $elt (@cli) {
				$cli .= " ".addSlashes($elt);
			}
			printDbg("$cli");
		}

		runCommandOrFail(@cli);
	}
	elsif ($translators->{"$transname"}{'transdef'}{'TRANSLATOR_FUNCTION'}{'value'}) {
		# Run the embedded perl code
		my $lineno = $translators->{"$transname"}{'transdef'}{'TRANSLATOR_FUNCTION'}{'lineno'} - 1;
		my $code;
		{
			my $perlDeps = $translators->{"$transname"}{'transdef'}{'TRANSLATOR_PERL_DEPENDENCIES'}{'value'} || [];
			$code = "{\n";
			if ($perlDeps) {
				foreach my $dep (@{$perlDeps}) {
					$code .= "use ".$dep.";\n";
					$lineno++;
				}
			}
			$code .= $translators->{"$transname"}{'transdef'}{'TRANSLATOR_FUNCTION'}{'value'};
			$code .= "}\n";
		}		

		my @inexts = @{$translators->{"$transname"}{'transdef'}{'INPUT_EXTENSIONS'}{'value'}};
		my $outext = $translators->{"$transname"}{'transdef'}{'OUTPUT_EXTENSIONS'}{'value'}[0];
		my @outexts = @{$translators->{"$transname"}{'transdef'}{'OUTPUT_EXTENSIONS'}{'value'}};
		
		my $c = eval $code;
		if (!defined($c) && $@) {
			my $msg = "$@";
			$msg =~ s/(\(eval\s+[0-9]+\)\s*line\s+)([0-9]+)/$1.($2 + $lineno)."($2)"/egsi;
			printErr(locGet(_T("Error inthe TRANSLATOR_FUNCTION of '{}':\n{}"), $transname, $msg));
		}
	}
	else {
		printErr(locGet(_T("Unable to find the method of translation for '{}'."),
				$transname));
	}

	return 1;
}


=pod

=item B<loadTranslator()>

Load the all the data needed to run a translator.
This function read the translator definition (transdef)
file; it sets the 'environment_variables' entry; and
it make symbolic link from the translator basename to
the translator itself.

I<Parameters:>

=over 8

=item * C<name> is the name of the translator to load.

=item * C<translators> is the associative array that contains all the informations
about all the translators.

=back

I<Returns:> true if a file was created; otherwise false.

=cut
sub loadTranslator($\%) {
	my $name = shift || confess('you must pass the name of the translator to load');
	my $translators = shift || confess('you must pass the descriptions of the translators');

	printDbgFor(4, locGet(_T("Searching translator '{}'."), $name));

	# Check if the translator name corresponds to an existing translator.
	# If not, try to find a variante.
	if (!exists $translators->{$name} || 
	    !$translators->{$name} ||
	    !$translators->{$name}{'file'}) {
		my $loadedlinkname = undef;
		my $linkname = undef;
		while ((!$loadedlinkname) && (my ($k,$v) = each (%{$translators}))) {
			if (isHash($v) && $v->{'basename'} && $v->{'basename'} eq $name
				&& $v->{'file'}) {
				if (exists $v->{'transdef'}) {
					$loadedlinkname = $k;
				}
				else {
					$linkname = $k;	
				}
			}
		}
		if (!$linkname && !$loadedlinkname) {
			printErr(locGet(_T("The translator '{}' cannot be found."), $name));
		}
		elsif ($loadedlinkname) {
			$linkname = $loadedlinkname;
		}
		printDbgFor(4, locGet(_T("Linking '{}' to '{}'."), $name, $linkname));
		$translators->{"$name"} = $translators->{"$linkname"};
		$name = $linkname;
	}

	# Load the translator if not already loaded
	if (exists $translators->{$name}{'transdef'}) {
		printDbgFor(4, locGet(_T("'{}' is already loaded."), $name));
	}
	else {
		printDbgFor(4, locGet(_T("Loading translator '{}'."), $name));
		# Read the translator definition
		$translators->{$name}{'transdef'} = readTranslatorFile(
							$translators->{$name}{'file'},
							$translators->{$name}{'ispdfmode'});
		# Add environment variables
		while ( my ($k,$v) = each(%{$translators->{$name}{'transdef'}})) {
			if ($v && $v->{'value'} && !isHash($v->{'value'}) && !isArray($v->{'value'})) {
				$translators->{$name}{'environment_variables'}{"$k"} = $v->{'value'};
			}
		}
	}

}


=pod

=item B<loadTranslatorsFromConfiguration(%%)>

Run the algorithm that permits to load the translator
according to a given configuration.
This function is provided to be invoked by the main
program of AutoLaTex, or any other program that is
needing to load the list of translators according
to a configuration.

I<Parameters:>

=over 8

=item * C<configuration> is the associative array that contains the configuration.

=item * C<data> is the associative array that IS FILLED with the data of the loaded translators.

=back

I<Returns:> Nothing

=cut
sub loadTranslatorsFromConfiguration(\%\%) {
	my $configuration = shift or confess("First parameter is mandatory: the associative array of the configuration");
	my $data = shift or confess("Second parameter is mandatory: the associative array of loaded data");
	if (!$data->{'translators'}) {
		%{$data->{'translators'}} = getTranslatorList(%{$configuration});
	}
	if (!$data->{'loadableTranslators'}) {
		%{$data->{'loadableTranslators'}} = getLoadableTranslatorList(%{$configuration});

		foreach my $translator (keys %{$data->{'loadableTranslators'}}) {
			# Load the translator
			loadTranslator($translator, %{$data->{'translators'}});

			# Extract image extensions
			foreach my $input (@{$data->{'translators'}{$translator}{'transdef'}{'INPUT_EXTENSIONS'}{'value'}}) {
				$data->{'imageDatabase'}{"$input"}{'translator'} = $translator;
			}
		}
	}
	return undef;
}


=pod

=item B<loadTranslatableImageList(%%)>

Run the algorithm that permits to load the list
of the images that should be processed by the translators.
This function is provided to be invoked by the main
program of AutoLaTex, or any other program that is
needing this list.

I<Parameters:>

=over 8

=item * C<configuration> is the associative array that contains the configuration.

=item * C<data> is the associative array that IS FILLED with the data of the pictures.

=item * C<skipManualAssignment> (optional) is a boolean flag that indicates if the manual
assignments with C<"*.files to convert"> from the configuration must be skipped.

=back

I<Returns:> Nothing

=cut
sub loadTranslatableImageList(\%\%;$) {
	my $configuration = shift or confess("First parameter is mandatory: the associative array of the configuration");
	my $data = shift or confess("Second parameter is mandatory: the associative array of loaded data");
	my $skipManualAssignment = shift;
	if (!$data->{'imageDatabaseReady'} && exists $configuration->{'generation.image directory'}) {
		my $separator = getPathListSeparator();
		# Prepare the configuration entries '*.files to convert'
		if (!$skipManualAssignment) {
			$configuration->{'__private__'}{'files to convert'} = {};
			while (my ($k,$v) = each(%{$configuration})) {
				if ($k =~ /^(.+)\.files\s+to\s+convert$/) {
					my $trans = $1;
					my @t = split(/\s*\Q$separator\E\s*/, $v);
					foreach my $t (@t) {
						$t = File::Spec->rel2abs($t, $configuration->{'__private__'}{'input.project directory'});
						$configuration->{'__private__'}{'files to convert'}{$t} = $trans;
					}
				}
			}
		}
		# Detect the image from the file system
		local* DIR;
		locDbg(_T("Detecting images inside '{}'"), $configuration->{'generation.image directory'});
		my $rawdirs = $configuration->{'generation.image directory'};
		$rawdirs =~ s/^\s+//s;
		$rawdirs =~ s/\s+$//s;
		if ($rawdirs) {
			my $pattern = "[\Q".getPathListSeparator()."\E]";
			my @dirs = split( /$pattern/is, $rawdirs);
			my @imageExtensions = keys $data->{'imageDatabase'};
			@imageExtensions = sort {
							my $la = length($a);
							my $lb = length($b);
							if ($la==$lb) {
								($a cmp $b);
							}
							else {
								($lb - $la);
							}
						} @imageExtensions;
			while (@dirs) {
				my $dir = shift @dirs;
				$dir = File::Spec->rel2abs($dir, $configuration->{'__private__'}{'input.project directory'});
				if (opendir(*DIR, "$dir")) {
					while (my $fn = readdir(*DIR)) {
						if ($fn ne File::Spec->curdir() && $fn ne File::Spec->updir()) {
							my $ffn = File::Spec->catfile("$dir", "$fn");
							if (-d "$ffn") {
								push @dirs, "$ffn";
							}
							else {
								my $selectedExtension = undef;
								if (!$skipManualAssignment &&
								    $configuration->{'__private__'}{'files to convert'}{$ffn}) {
									my $trans = $configuration->{'__private__'}{'files to convert'}{$ffn};
									$selectedExtension = "$separator$separator$trans$separator$separator";
									$data->{'imageDatabase'}{"$selectedExtension"}{'translator'} = $trans;
									loadTranslator($trans, %{$data->{'translators'}});
								}
								if (!$selectedExtension) {
									for(my $i=0; !$selectedExtension && $i<@imageExtensions; ++$i) {
										if ($fn =~ /\Q$imageExtensions[$i]\E$/i) {
											$selectedExtension = $imageExtensions[$i];
										}
									}
								}
								if ($selectedExtension) {
									if (!$data->{'imageDatabase'}{"$selectedExtension"}{'files'}) {
										$data->{'imageDatabase'}{"$selectedExtension"}{'files'} = [];
									}
									push @{$data->{'imageDatabase'}{"$selectedExtension"}{'files'}}, "$ffn";
								}
							}
						}
					}
					closedir(*DIR);
				}
			}
		}
		$data->{'imageDatabaseReady'} = 1;
	}
	return undef;
}

1;
__END__
=back

=head1 BUG REPORT AND FEEDBACK

To report bugs, provide feedback, suggest new features, etc. visit the AutoLaTeX Project management page at <http://www.arakhne.org/autolatex/> or send email to the author at L<galland@arakhne.org>.

=head1 LICENSE

S<GNU Public License (GPL)>

=head1 COPYRIGHT

S<Copyright (c) 1998-13 Stéphane Galland E<lt>galland@arakhne.orgE<gt>>

=head1 SEE ALSO

L<autolatex-dev>
