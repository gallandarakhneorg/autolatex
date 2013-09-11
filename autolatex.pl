#!/usr/bin/perl -W

# autolatex - autolatex.pl
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

require 5.014;

use strict ;

use File::Basename ;
use File::Spec ;
use File::Copy ;
use Carp;

$| = 1; # autoflush to get the progress indicator working

#------------------------------------------------------
#
# Initialization code
#
#------------------------------------------------------
{
	my $PERLSCRIPTDIR ;
	my $PERLSCRIPTNAME ;
	my $LAUNCHINGNAME ;
	BEGIN{
	  # Where is this script?
	  $PERLSCRIPTDIR = "$0";
	  $LAUNCHINGNAME = basename("$0");
	  my $scriptdir = dirname( $PERLSCRIPTDIR );
	  while ( -e $PERLSCRIPTDIR && -l $PERLSCRIPTDIR ) {
	    $PERLSCRIPTDIR = readlink($PERLSCRIPTDIR);
	    if ( substr( $PERLSCRIPTDIR, 0, 1 ) eq '.' ) {
	      $PERLSCRIPTDIR = File::Spec->catfile( $scriptdir, "$PERLSCRIPTDIR" ) ;
	    }
	    $scriptdir = dirname( $PERLSCRIPTDIR );
	  }
	  $PERLSCRIPTNAME = basename( $PERLSCRIPTDIR ) ;
	  $PERLSCRIPTDIR = dirname( $PERLSCRIPTDIR ) ;
	  $PERLSCRIPTDIR = File::Spec->rel2abs( "$PERLSCRIPTDIR" );
	  # Push the path where the script is to retreive the arakhne.org packages
	  push(@INC,"$PERLSCRIPTDIR");
	  push(@INC,File::Spec->catfile("$PERLSCRIPTDIR","pm"));

	}
	use AutoLaTeX::Core::Util;
	AutoLaTeX::Core::Util::setAutoLaTeXInfo("$LAUNCHINGNAME","$PERLSCRIPTNAME","$PERLSCRIPTDIR");
}

use AutoLaTeX::Core::Main;
use AutoLaTeX::Core::Util;
use AutoLaTeX::Core::OS;
use AutoLaTeX::Core::Config;
use AutoLaTeX::Core::IntUtils;
use AutoLaTeX::Core::Progress;
use AutoLaTeX::Core::Translator;
use AutoLaTeX::Make::Make;
use AutoLaTeX::TeX::Flattener;

###################################################
# Add the include path to the "user" interpreters #
###################################################
push @INC, File::Spec->catfile(getUserConfigDirectory(),"translators");


my %configuration;
my %autolatexData = ();

# Helping function to init the progress bar
sub __initProgress($) {
	my $max = shift;
	my $show = $configuration{'__private__'}{'action.show progress'};
	if ($show) {
		my $progress = AutoLaTeX::Core::Progress->new($max);
		$progress->setCarriageReturn($show ne 'n');
		return $progress;
	}
	return undef;
}

sub __subProgress($;$) {
	my $progress = shift;
	my $inparent = shift;
	if ($progress) {
		if ($inparent) {
			return $progress->subProgress($inparent);
		}
		else {
			return $progress->subProgress();
		}
	}
	return undef;
}

#------------------------------------------------------
#
# IMAGE MANAGEMENT
#
#------------------------------------------------------

sub al_generateimages($) {
	my $progress = shift;
	if (cfgBoolean($configuration{'generation.generate images'})) {
		my $pv = 0;
		my $imageCount = $autolatexData{'numberOfImages'};
		$progress->setMax($imageCount) if ($progress);
		foreach my $formatName (@{$autolatexData{'activatedImageExtensions'}}) {
			my $entry = $autolatexData{'imageDatabase'}{"$formatName"};
			my $trans = $entry->{'translator'};
			my $fileCount = ($entry->{'files'}) ? @{$entry->{'files'}} : 0;
			if ($fileCount>0) {
				foreach my $file (@{$entry->{'files'}}) {
					runRootTranslator(%configuration, $trans, $file, %{$autolatexData{'translators'}}, 0);
					$progress->increment() if ($progress);
				}
			}
		}
		$progress->stop() if ($progress);
	}
}

sub al_run_images {
	my $i_ref = shift;
	# Force the generation of images
	$configuration{'generation.generate images'} = 'yes';
	my $progress = __initProgress(10000);
	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	$progress->setValue(100) if ($progress);
	loadTranslatableImageList(%configuration,%autolatexData);
	$progress->setValue(200) if ($progress);
	al_generateimages(__subProgress($progress));
	$progress->stop() if ($progress);
}

sub al_run_showimages {
	my $i_ref = shift;
	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	loadTranslatableImageList(%configuration,%autolatexData);
	my @images = ();
	foreach my $value (values %{$autolatexData{'imageDatabase'}}) {
		if (exists $value->{'files'}) {
			foreach my $f (@{$value->{'files'}}) {
				$f = File::Spec->abs2rel($f, $configuration{'__private__'}{'input.project directory'});
				push @images, $f;
			}
		}
	}
	@images = sort @images;
	print STDOUT join("\n", @images)."\n";
}

sub al_run_showimagemap {
	my $i_ref = shift;
	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	loadTranslatableImageList(%configuration,%autolatexData);
	my %images = ();
	foreach my $value (values %{$autolatexData{'imageDatabase'}}) {
		if (exists $value->{'files'}) {
			foreach my $img (@{$value->{'files'}}) {
				$img = File::Spec->abs2rel($img, $configuration{'__private__'}{'input.project directory'});
				$images{$img} = $value->{'translator'};
				die("no translator for: $img\n") unless $images{$img};
			}
		}
	}
	foreach my $k (sort keys %images) {
		my $h = "$k";
		if (length($h)>=50) {
			$h .= "\n";
			for(my $i=0; $i<50; ++$i) {
				$h .= ' ';
			}
		}
		else {
			while (length($h)<50) {
				$h .= ' ';
			}
		}
		print STDERR "$h => $images{$k}\n";
	}
}

#------------------------------------------------------
#
# SCM MANAGEMENT
#
#------------------------------------------------------

sub al_run_commit {
	my $i_ref = shift;
	if ($$i_ref==0 || $ARGV[$$i_ref-1] ne 'cleanall') {
		splice @ARGV, $$i_ref, 0, 'cleanall';
	}
	elsif ($configuration{'scm.scm commit'}) {
		system($configuration{'scm.scm commit'});
	}
	else {
		printWarn(formatText(_T('The configuration entry \'{}\' is not defined.'), 'scm.scm commit'));
	}
}

sub al_run_update {
	my $i_ref = shift;
	if ($$i_ref==0 || $ARGV[$$i_ref-1] ne 'cleanall') {
		splice @ARGV, $$i_ref, 0, 'cleanall';
	}
	elsif ($configuration{'scm.scm update'}) {
		system($configuration{'scm.scm update'});
	}
	else {
		printWarn(formatText(_T('The configuration entry \'{}\' is not defined.'), 'scm.scm update'));
	}
}

#------------------------------------------------------
#
# VIEW MANAGEMENT
#
#------------------------------------------------------

sub al_view() {
	my $pdfFile = File::Spec->catfile(
				$configuration{'__private__'}{'output.directory'},
				$configuration{'__private__'}{'output.latex basename'}.'.pdf');
	my $isWaiting = !cfgBoolean($configuration{'viewer.asynchronous run'});
	if ($configuration{'viewer.viewer'}) {
		if ($isWaiting) {
			printDbgFor(2, formatText(_T("Launching '{}'"), $configuration{'viewer.viewer'}));
		}
		else {
			printDbgFor(2, formatText(_T("Launching '{}' in background"), $configuration{'viewer.viewer'}));
		}
		runCommandSilently(
			{ 'wait' => $isWaiting },
			$configuration{'viewer.viewer'},  $pdfFile);
	}
	else {
		my $v = 0;
		foreach my $viewer ('acroread', 'evince', 'kpdf', 'xpdf', 'gv') {
			if (!$v) {
				my $bin = which($viewer);
				if ($bin) {
					$v = 1;
					if ($isWaiting) {
						printDbgFor(2, formatText(_T("Launching '{}'"), $bin));
					}
					else {
						printDbgFor(2, formatText(_T("Launching '{}' in background"), $bin));
					}
					runCommandSilently(
						{ 'wait' => $isWaiting },
						$bin,  $pdfFile);
				}
			}
		}
		if (!$v) {
			printErr(formatText(_T('Unable to find a viewer.')));
		}
	}
}

#------------------------------------------------------
#
# TEX MANAGEMENT
#
#------------------------------------------------------

sub al_make($) {
	my $progress = shift;
	my $make = AutoLaTeX::Make::Make->new(\%configuration);
	$make->enableBiblio(cfgBoolean($configuration{'generation.biblio'}));
	$make->generationType($configuration{'generation.generation type'});
	$make->addTeXFile( $configuration{'__private__'}{'input.latex file'} );
	$make->build($progress);
}

sub al_run_make {
	my $i_ref = shift;
	my $progress = __initProgress(10000);
	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	$progress->setValue(100) if ($progress);
	loadTranslatableImageList(%configuration,%autolatexData);
	$progress->setValue(200) if ($progress);
	al_generateimages(__subProgress($progress, 2500));
	al_make(__subProgress($progress));
	$progress->stop() if ($progress);
}

sub al_run_makeandview {
	my $i_ref = shift;
	my $force = shift;
	my $progress = __initProgress(10000);
	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	$progress->setValue(100) if ($progress);
	loadTranslatableImageList(%configuration,%autolatexData);
	$progress->setValue(200) if ($progress);
	al_generateimages(__subProgress($progress, 2500));
	al_make(__subProgress($progress, 7000));
	if ($force || cfgBoolean($configuration{'viewer.view'})) {
		al_view();
	}
	$progress->stop() if ($progress);
}

sub al_run_biblio {
	my $i_ref = shift;
	my $progress = __initProgress(10000);
	my $make = AutoLaTeX::Make::Make->new(\%configuration);
	$make->enableBiblio(1);
	$make->addTeXFile( $configuration{'__private__'}{'input.latex file'} );
	$progress->setValue(1000) if ($progress);
	$make->buildBiblio(__subProgress($progress));
	$progress->stop() if ($progress);
}

sub al_run_makeindex {
	my $i_ref = shift;
	my $progress = __initProgress(10000);
	my $make = AutoLaTeX::Make::Make->new(\%configuration);
	$make->enableMakeIndex(1);
	$make->addTeXFile( $configuration{'__private__'}{'input.latex file'} );
	$progress->setValue(1000) if ($progress);
	$make->buildMakeIndex(__subProgress($progress));
	$progress->stop() if ($progress);
}

#------------------------------------------------------
#
# CLEANING MANAGEMENT
#
#------------------------------------------------------

sub al_shell2re($) {
	return '' unless ($_[0]);
	my $shell = "$_[0]";
	my $re = "";
	while ($shell && $shell =~ /^(.*?)([*?]|(?:\[([^\]]+)\]))(.*)$/) {
		(my $prev, my $sep, $shell) = ($1,$2,$4);
		$re .= "\Q$prev\E";
		if ($sep eq '*') {
			$re .= '.*';
		}
		elsif ($sep eq '?') {
			$re .= '.';
		}
		else {
			$re .= '['.$3.']';
		}
		
	}
	if ($shell) {
		$re .= "\Q$shell\E";
	}
	if ($re) {
		$re = "(?:$re)";
	}
	return $re;
}

sub al_applyCleanRecursively(\@\@) {
	my $rootPatterns = shift;
	my $dirPatterns = shift;

	my %absFiles = ();

	# Convert shell wildcards to Perl re
	my $tpatterns = '';
	if ($rootPatterns) {
		foreach my $pattern (@{$rootPatterns}) {
			if (File::Spec->file_name_is_absolute($pattern)) {
				$absFiles{$pattern} = 1;
			}
			else {
				if ($tpatterns) {
					$tpatterns .= '|';
				}
				$tpatterns .= al_shell2re($pattern);
			}
		}
	}
	my $dpatterns = '';
	if ($dirPatterns) {
		foreach my $pattern (@{$dirPatterns}) {
			if (File::Spec->file_name_is_absolute($pattern)) {
				$absFiles{$pattern} = 1;
			}
			else {
				if ($dpatterns) {
					$dpatterns .= '|';
				}
				$dpatterns .= al_shell2re($pattern);
			}
		}
	}

	# Clean the files
	my @dirs = ( $configuration{'__private__'}{'output.directory'} );
	my $rootdir = 1;
	local *DIR;
	while (@dirs) {
		my $dir = shift @dirs;
		opendir(*DIR, "$dir") or printErr("$dir: $!");
		while (my $fn = readdir(*DIR)) {
			if ($fn ne File::Spec->updir() && $fn ne File::Spec->curdir()) {
				my $ffn = File::Spec->rel2abs(File::Spec->catfile("$dir","$fn"));
				if (-d "$ffn") {
					push @dirs, "$ffn";
				}
				elsif ($absFiles{$ffn}) {
						secure_unlink("$ffn");
				}
				else {
					if ($rootdir && $tpatterns && $fn =~ /^$tpatterns$/s) {
						secure_unlink("$ffn");
					}
					elsif ($dpatterns && $fn =~ /^$dpatterns$/s) {
						secure_unlink("$ffn");
					}
				}
			}
		}
		closedir(*DIR);
		$rootdir = 0;
	}
}

sub al_getcleanfiles() {
	my $outputFile = File::Spec->rel2abs(File::Spec->catfile(
				$configuration{'__private__'}{'output.directory'},
				$configuration{'__private__'}{'output.latex basename'}));
	my @filestoclean = (
		'.autolatex_stamp', 'autolatex_stamp',
		'autolatex_exec_stderr.log', 'autolatex_exec_stdout.log', 'autolatex_exec_stdin.log',
		'autolatex_autogenerated.tex',
		"$outputFile.pdf", "$outputFile.dvi", "$outputFile.xdvi", "$outputFile.xdv", "$outputFile.ps", "$outputFile.synctex.gz", "$outputFile.synctex",
	);
	my @filestocleanrec = (
		'*.aux', '*.log', '*.bbl', '*.blg',
		'*.cb', '*.toc', '*.out', '*.lof',
		'*.lot', '*.los', '*.maf', '*.snm',
		'*.nav', '*.lom', '*.tmp', '*.loa',
		'*.idx', '*.ilg', '*.ind', '*.mtc',
		'*.loe', '*.fls',
		'*.mtc[0-9]', '*.mtc[0-9][0-9]',
		'*.mtc[0-9][0-9][0-9]', '*.mtf',
		'*.mtf[0-9]', '*.mtf[0-9][0-9]',
		'*.mtf[0-9][0-9][0-9]', '*.mtl',
		'*.mtl[0-9]', '*.mtl[0-9][0-9]',
		'*.mtl[0-9][0-9][0-9]', '*.bmt',
		'*.thlodef', '*.lbl', '*.brf',
		'*.vrb', '*.spl',
		# Biber
		'*.bcf', '*.run.xml',
	);
	if ($configuration{'clean.files to clean'}) {
		if (!isArray($configuration{'clean.files to clean'})) {
			push @filestoclean, split(/\s+/, $configuration{'clean.files to clean'});
		}
		else {
			push @filestoclean, @{$configuration{'clean.files to clean'}};
		}
	}
	return (\@filestoclean, \@filestocleanrec);
}

sub al_getcleanmorefiles() {
	my @filestoclean = ();
	my @filestocleanrec = (
		'*~', '*.bak', '*.backup',
	);
	if ($configuration{'clean.files to desintegrate'}) {
		if (!isArray($configuration{'clean.files to desintegrate'})) {
			push @filestoclean, split(/\s+/, $configuration{'clean.files to desintegrate'});
		}
		else {
			push @filestoclean, @{$configuration{'clean.files to desintegrate'}};
		}
	}
	return (\@filestoclean, \@filestocleanrec);
}

sub al_run_clean {
	my $i_ref = shift;
	my ($a,$b) = al_getcleanfiles();
	printDbg(_T("Removing all the temporary files"));
	al_applyCleanRecursively(@$a, @$b);
}

sub al_run_cleanall {
	my $i_ref = shift;

	printDbg(_T("Removing all the temporary and generated files"));

	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	loadTranslatableImageList(%configuration,%autolatexData);

	my ($a,$b) = al_getcleanfiles();
	my ($c, $d) = al_getcleanmorefiles();
	my @e = (@$a, @$c);
	my @f = (@$b, @$d);
	al_applyCleanRecursively(@e,@f);

	# Remove generated images
	foreach my $entry (values %{$autolatexData{'imageDatabase'}}) {
		my $trans = $entry->{'translator'};
		foreach my $file (@{$entry->{'files'}}) {
			my $cleanpattern = $autolatexData{'translators'}{"$trans"}{'cleanpattern'};
			if (!$cleanpattern) {
				$cleanpattern = '';
				my $definition = $autolatexData{'translators'}{"$trans"}{'transdef'};
				if ($definition) {
					my $cleanPatterns = $definition->{'FILES_TO_CLEAN'}{'value'};
					foreach my $p (@{$cleanPatterns}) {
						if ($cleanpattern) {
							$cleanpattern .= '|';
						}
						$cleanpattern .= al_shell2re($p);
					}
					$autolatexData{'translators'}{"$trans"}{'cleanpattern'} = $cleanpattern;
				}
			}

			my @inputExtensions = @{$autolatexData{'translators'}{"$trans"}{'transdef'}{'INPUT_EXTENSIONS'}{'value'}};
			my $outputExtension = $autolatexData{'translators'}{"$trans"}{'transdef'}{'OUTPUT_EXTENSIONS'}{'value'}[0] || '';
			my $in = basename($file,@inputExtensions);
			my $dir = dirname($file);
			my $out = "$in";
			my $localpattern = "$cleanpattern";
			{
				my $ain = File::Spec->rel2abs("$file");
				my $aout = File::Spec->rel2abs(
						File::Spec->catfile("$dir","$out$outputExtension"));
				if ("$ain" ne "$aout") {
					if ($localpattern) {
						$localpattern .= '|';
					}
					$localpattern .= '$out'."\Q$outputExtension\E";
				}
			}

			$localpattern =~ s/\\?\$in/\Q$in\E/g;
			$localpattern =~ s/\\?\$out/\Q$out\E/g;

			local *DIR;
			if (opendir(*DIR, "$dir")) {
				my @files_to_remove = ();
				while (my $fn = readdir(*DIR)) {
					if ($fn ne File::Spec->curdir() && $fn ne File::Spec->updir()
						&& $fn =~ /^(?:$localpattern)$/s) {
						my $ffn = File::Spec->catfile("$dir","$fn");
						push @files_to_remove, $ffn;
					}
				}
				closedir(*DIR);
				foreach my $fn (@files_to_remove) {
					secure_unlink("$fn");
				}
			}
		}
	}
}

#------------------------------------------------------
#
# FLATTENING ACTIONS
#
#------------------------------------------------------

sub al_run_makeflat {
	my $i_ref = shift;

	my $progress = __initProgress(10000);

	# Treat the command line option --biblio
	my $biblio_option_on_cli = $configuration{'__private__'}{'CLI.biblio'};
	$biblio_option_on_cli = 'no' unless (defined($biblio_option_on_cli));
	$configuration{'generation.biblio'} = $biblio_option_on_cli;

	loadTranslatorsFromConfiguration(%configuration,%autolatexData);
	loadTranslatableImageList(%configuration,%autolatexData);

	$progress->setValue(200) if ($progress);

	al_generateimages(__subProgress($progress, 2500));

	# Generate all the document, in particular the BBL file.
	if (!cfgBoolean($biblio_option_on_cli)) {
		al_make(__subProgress($progress, 4500));
	}

	$progress->setValue(7200) if ($progress);

	my $output = $configuration{'makeflat.output'};
	if (!$output) {
		my $basename = $configuration{'makeflat.basename'};
		if (!$basename) {
			$basename = 'flat_version';
		}
		$output = File::Spec->catfile(
			dirname($configuration{'__private__'}{'input.latex file'}),
			$basename);
	}

	# Build the list of images
	my @images;
	{
		my %images = ();
		my $sprogress = __subProgress($progress, 1800);
		$sprogress->setMax($autolatexData{'numberOfImages'}) if ($sprogress);
		foreach my $trans (values %{$autolatexData{'imageDatabase'}}) {
			if ($trans->{'files'}) {
				my $transname = $trans->{'translator'};
				my $transdef = $autolatexData{'translators'}{$transname}{'transdef'};
				foreach my $file (@{$trans->{'files'}}) {
					my $template = File::Spec->catfile(
								dirname($file),
								basename($file, @{$transdef->{'INPUT_EXTENSIONS'}{'value'}}));
					foreach my $ext (@{$transdef->{'OUTPUT_EXTENSIONS'}{'value'}}) {
						$images{"$template$ext"} = 1;
					}
					$sprogress->increment() if ($sprogress);
				}
			}
		}
		@images = keys %images;
	}

	$progress->setValue(9000) if ($progress);

	flattenTeX($configuration{'__private__'}{'input.latex file'}, $output, @images, cfgBoolean($biblio_option_on_cli));

	$progress->stop() if ($progress);
}

#------------------------------------------------------
#
# MAIN PROGRAM
#
#------------------------------------------------------

# script parameters
my @ORIGINAL_ARGV = @ARGV;

setDebugLevel(0);

initTextDomain('autolatex', File::Spec->catfile(getAutoLaTeXDir(), 'po'), 'UTF-8');

%configuration = mainProgram(); # Exit on error

if (getDebugLevel()>=6) {
	exitDbg(\%configuration, \@ORIGINAL_ARGV);
}
elsif ($configuration{'__private__'}{'action.debug mode'}) {
	setDebugLevel(5);
	# Force to fail on Perl warnings
	$SIG{__WARN__} = sub { confess(@_); };
}
elsif (getDebugLevel()>=5) {
	# Force to fail on Perl warnings
	$SIG{__WARN__} = sub { confess(@_); };
}

if ($configuration{'__private__'}{'action.show progress'}) {
	setDebugLevel(0); # Force to be not verbose when progress indicator is displayed
}

@ORIGINAL_ARGV = (); # Not more necessary

# Run the action of the configuration file generation
my $optionalAction = 0;
if (defined $configuration{'__private__'}{'action.create config file'}) {
	my $filename;
        if (($configuration{'__private__'}{'action.create config file'})&&
            ($configuration{'__private__'}{'action.create config file'} eq 'project')) {
                printDbg(_T("Creating default project configuration file...\n"));
                $filename = getProjectConfigFilename($configuration{'__private__'}{'output.directory'});
        }
        else {
                printDbg(_T("Creating default user configuration file...\n"));
                $filename = getUserConfigFilename();
        }
        copy(getSystemConfigFilename(),"$filename") or printErr("$filename:", "$!");
	$optionalAction = 1;
}

# Run the action of the IST file generation
if (defined($configuration{'__private__'}{'action.create ist file'})) {
        printDbg(_T("Creating default makeindex style file...\n"));
        my $filename = File::Spec->catfile($configuration{'__private__'}{'output.directory'},"default.ist");
        copy(getSystemISTFilename(),"$filename") or printErr("$filename:","$!");
	$optionalAction = 1;
}

# Fix the configuration file
if (defined($configuration{'__private__'}{'action.fix config file'})) {
        if (!$configuration{'__private__'}{'action.fix config file'}) {
                $configuration{'__private__'}{'action.fix config file'} = getProjectConfigFilename($configuration{'__private__'}{'output.directory'});
                $configuration{'__private__'}{'action.fix config file'} = undef unless (-r $configuration{'__private__'}{'action.fix config file'});
        }
        if (!$configuration{'__private__'}{'action.fix config file'}) {
                $configuration{'__private__'}{'action.fix config file'} = getUserConfigFile();
        }
        if (-r $configuration{'__private__'}{'action.fix config file'}) {
                print "Fixing configuration file '".$configuration{'__private__'}{'action.fix config file'}."'\n";
                doConfigurationFileFixing($configuration{'__private__'}{'action.fix config file'});
        }
        else {
                printErr($configuration{'__private__'}{'action.fix config file'},':',"$!\n");
        }
	$optionalAction = 1;
}


# Apply the default CLI action
if (!@ARGV && !$optionalAction) {
	push @ARGV, 'all' ;
}

# Loop on CLI actions
for(my $i=0; $i<@ARGV; $i++) {

	if ($ARGV[$i] eq 'all' || $ARGV[$i] eq 'view') {
		my $forceview = ($ARGV[$i] eq 'view');
		al_run_makeandview(\$i,$forceview);
	}
	elsif ($ARGV[$i] eq 'clean') {
		al_run_clean(\$i);
	}
	elsif ($ARGV[$i] eq 'cleanall') {
		al_run_cleanall(\$i);
	}
	elsif ($ARGV[$i] eq 'gen_doc') {
		al_run_make(\$i);
	}
	elsif ($ARGV[$i] eq 'bibtex') {
		printWarn('The directive \'bibtex\' is deprecated from the command line interface.');
		al_run_biblio(\$i);
	}
	elsif ($ARGV[$i] eq 'biblio') {
		al_run_biblio(\$i);
	}
	elsif ($ARGV[$i] eq 'makeindex') {
		al_run_makeindex(\$i);
	}
	elsif ($ARGV[$i] eq 'images') {
		al_run_images(\$i);
	}
	elsif ($ARGV[$i] eq 'showimages') {
		al_run_showimages(\$i);
	}
	elsif ($ARGV[$i] eq 'showimagemap') {
		al_run_showimagemap(\$i);
	}
	elsif ($ARGV[$i] eq 'commit') {
		al_run_commit(\$i);
	}
	elsif ($ARGV[$i] eq 'update') {
		al_run_update(\$i);
	}
	elsif ($ARGV[$i] eq 'showpath') {
		print "PATH=".$ENV{'PATH'}."\n";
	}
	elsif ($ARGV[$i] eq 'makeflat') {
		al_run_makeflat(\$i);
	}
	else {
		printErr(formatText(_T('Command line action \'{}\' is not supported.'),$ARGV[$i]));
	}

}

exit(0);
__END__

