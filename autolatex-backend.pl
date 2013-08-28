#!/usr/bin/perl -W

# autolatex - autolatex-backend.pl
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

require 5.014;

use strict ;

use File::Basename ;
use File::Spec ;
use File::Temp qw/ :POSIX / ;
use Config::Simple;
use Carp;

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
use AutoLaTeX::Core::Config;
use AutoLaTeX::Core::OS;
use AutoLaTeX::Core::Translator;
use AutoLaTeX::Core::Config;
use AutoLaTeX::Core::IntUtils;

sub readStdin() {
	my $tmpfile = tmpnam();
	local *OUTFILE;
	open(*OUTFILE, ">$tmpfile") or exit(255);
	while (my $line = <STDIN>) {
		print OUTFILE $line;
	}
	close(*OUTFILE);
	my $cfgReader = new Config::Simple("$tmpfile");
	my %cfg = $cfgReader->vars();
	unlink("$tmpfile");
	my %rcfg = ();
	while (my ($k,$v) = (each %cfg)) {
		$k =~ /^([^.]+)\.(.+)$/;
		my ($g, $r) = ($1, $2);
		$rcfg{$g}{$r} = $v;
	}
	return %rcfg;
}

sub printComment($$) {
	my $cmd = shift;
	my $comment = shift;
	print STDERR "\$> $cmd\n";
	my %params = (	'limit' => 70,
			'indent' => 5,
			'prefix_nosplit' => '',
			'prefix_split' => '',
			'postfix_split' => '',
			'indent_char' => ' ',
	);
	my $text = join("\n", makeMessageLong(%params, $comment));
	print STDERR "$text\n\n";
}

setDebugLevel(0);

initTextDomain('autolatex', File::Spec->catfile(getAutoLaTeXDir(), 'po'), 'UTF-8');

my %currentConfiguration = mainProgram(0);

my %systemConfiguration = readOnlySystemConfiguration();
my %userConfiguration = readOnlyUserConfiguration();
my %projectConfiguration = ();
my @projectConfigurationPath = ();

if ($currentConfiguration{'__private__'}{'input.project directory'}) {
	@projectConfigurationPath = File::Spec->splitdir($currentConfiguration{'__private__'}{'input.project directory'});
	my $cfg = readOnlyProjectConfiguration(@projectConfigurationPath);
	if ($cfg && isHash($cfg)) {
		%projectConfiguration = %{$cfg};
	}
}

my $a1 = $ARGV[0] || '';
my $a2 = $ARGV[1] || '';
my $a3 = $ARGV[2] || '';
my $a4 = $ARGV[3] || '';

if ($a1 eq 'get') {
	if ($a2 eq 'config') {
		my $tmpfile = tmpnam();
		my %cfgOutput = ();
		if ($a3 eq 'project') {
			%cfgOutput = %projectConfiguration;
		}
		elsif ($a3 eq 'user') {
			%cfgOutput = %userConfiguration;
		}
		elsif ($a3 eq 'system') {
			%cfgOutput = %systemConfiguration;
		}
		elsif (!$a3 || $a3 eq 'all') {
			# Reinject the main file because it was removed by the reading functions.
			if ($projectConfiguration{'generation.main file'}) {
				$currentConfiguration{'generation.main file'} = $projectConfiguration{'generation.main file'};
			}
			%cfgOutput = %currentConfiguration;
		}
		else {
			exit(255);
		}
		if ($a4) {
			if ($a4 eq '__private__') {
				%cfgOutput =  %{$cfgOutput{'__private__'}};
				if ($cfgOutput{'internationalization'}) {
					$cfgOutput{'internationalization.locale'} = $cfgOutput{'internationalization'}{'locale'} || '';
					$cfgOutput{'internationalization.language'} = $cfgOutput{'internationalization'}{'language'} || '';
					$cfgOutput{'internationalization.codeset'} = $cfgOutput{'internationalization'}{'codeset'} || '';
					$cfgOutput{'internationalization.domains'} = join(',',@{$cfgOutput{'internationalization'}{'domains'}});
					delete $cfgOutput{'internationalization'}
				}
				foreach my $k (keys %cfgOutput) {
					unless (defined($cfgOutput{$k})) {
						$cfgOutput{$k} = ''
					}
				}
			}
			else {
				foreach my $k (keys %cfgOutput) {
					if ($k !~ /^\Q$a4.\E/) {
						delete $cfgOutput{$k};
					}
				}
			}
		}
		writeConfigFile($tmpfile, %cfgOutput);
		local *INFILE;
		open(*INFILE, "<$tmpfile") or exit(255);
		while (my $line = <INFILE>) {
			print STDOUT $line;
		}
		close(*INFILE);
		unlink("$tmpfile");
	}
	elsif ($a2 eq 'translators') {
		my %translators = getTranslatorList(%currentConfiguration);
		my @keys = sort keys %translators;
		foreach my $name (@keys) {
			my $v = $translators{$name};
			print STDOUT "[$name]\n";
			while (my ($k, $kv) = each(%{$v})) {
				print STDOUT "$k=$kv\n";
			}
			print STDOUT "\n";
		}
	}
	elsif ($a2 eq 'conflicts') {
		my %translators = getTranslatorList(%currentConfiguration);
		if ($a3 eq 'resolved') {
			setInclusionFlags(%translators,
					%systemConfiguration,
					%userConfiguration,
					%projectConfiguration);
		}
		elsif ($a3) {
			exit(255);
		}
		my %conflicts = detectConflicts(%translators);
		foreach my $k (keys %conflicts) {
			print STDOUT "[$k]\n";
			foreach my $source (keys %{$conflicts{$k}}) {
				foreach my $t (keys %{$conflicts{$k}{$source}}) {
					print STDOUT "$source=$t\n";
				}
			}
			print STDOUT "\n";
		}
	}
	elsif ($a2 eq 'loads') {
		my %translators = getTranslatorList(%currentConfiguration);

		setInclusionFlags(%translators,
				%systemConfiguration,
				%userConfiguration,
				%projectConfiguration);

		foreach my $level (@ALL_LEVELS) {
			print STDOUT "[$level]\n";
			while (my ($transName,$data) = each(%translators)) {
				if (defined($data->{'included'}{$level})) {
					my $val = cfgToBoolean($data->{'included'}{$level});
					print STDOUT "$transName=$val\n";
				}
			}
			print STDOUT "\n";
		}
	}
	elsif ($a2 eq 'images') {
		my %autolatexData = ();
		loadTranslatorsFromConfiguration(%currentConfiguration,%autolatexData);
		loadTranslatableImageList(%currentConfiguration,%autolatexData,1);
		# Convert 'files to convert' from scalar to array
		my $separator = getPathListSeparator();
		my %files_to_convert = ();
		foreach my $key (keys %currentConfiguration) {
			if ($key =~ /^(.+)\.files\s+to\s+convert$/) {
				my $trans = $1;
				my @f = split(/\s*\Q$separator\E\s*/, $currentConfiguration{$key});
				foreach my $f (@f) {
					$f = File::Spec->rel2abs($f, $currentConfiguration{'__private__'}{'input.project directory'});
					$files_to_convert{$f} = $trans;
				}
			}
		}
		# Build the data for each translator
		my %translators = ();
		my %reinjected_files = ();
		foreach my $value (values %{$autolatexData{'imageDatabase'}}) {
			if (exists $value->{'files'} && $value->{'translator'}) {
				if (!$translators{$value->{'translator'}}{'automatic assignment'}) {
					$translators{$value->{'translator'}}{'automatic assignment'} = [];
				}
				if (!$translators{$value->{'translator'}}{'overriden assignment'}) {
					$translators{$value->{'translator'}}{'overriden assignment'} = [];
				}
				foreach my $file (@{$value->{'files'}}) {
					my $absfile = File::Spec->rel2abs($file, $currentConfiguration{'__private__'}{'input.project directory'});
					my $relfile = File::Spec->abs2rel($absfile, $currentConfiguration{'__private__'}{'input.project directory'});
					if ($files_to_convert{$absfile}) {
						if (!$reinjected_files{$files_to_convert{$absfile}}) {
							$reinjected_files{$files_to_convert{$absfile}} = [];
						}
						push @{$translators{$value->{'translator'}}{'overriden assignment'}}, $relfile;
						push @{$reinjected_files{$files_to_convert{$absfile}}}, $relfile;
					}
					else {
						push @{$translators{$value->{'translator'}}{'automatic assignment'}}, $relfile;
					}
				}
			}
		}
		# Reinject the manually selected files
		while (my ($translator, $desc) = each(%reinjected_files)) {
			if (!$translators{$translator}{'files to convert'}) {
				$translators{$translator}{'files to convert'} = [];
			}
			push @{$translators{$translator}{'files to convert'}}, @{$desc};
		}
		# Output the data for each translator
		while (my ($translator, $desc) = each(%translators)) {
			print STDOUT "[$translator]\n";
			while (my ($key, $files) = each(%{$desc})) {
				if ($files && @{$files}) {
					print STDOUT "$key=";
					print STDOUT join($separator,@{$files});
					print STDOUT "\n";
				}
			}
			print STDOUT "\n";
		}
	}
	else {
		exit(255);
	}
}
elsif ($a1 eq 'set') {
	if ($a2 eq 'loads') {
		my %new_config = readStdin();
		foreach my $k (keys %userConfiguration) {
			if ($k =~ /\.include module$/) {
				delete $userConfiguration{$k};
			}
		}
		if ($new_config{'user'}) {
			while (my ($translator, $inc) = each(%{$new_config{'user'}})) {
				$userConfiguration{"$translator.include module"} = (cfgBoolean($inc) ? 'true' : 'false');
			}
		}
		my $userFile = getUserConfigFilename();
		writeConfigFile($userFile, %userConfiguration);
		if (@projectConfigurationPath) {
			foreach my $k (keys %projectConfiguration) {
				if ($k =~ /\.include module$/) {
					delete $projectConfiguration{$k};
				}
			}
			if ($new_config{'project'}) {
				while (my ($translator, $inc) = each(%{$new_config{'project'}})) {
					$projectConfiguration{"$translator.include module"} = (cfgBoolean($inc) ? 'true' : 'false');
				}
			}
			my $projectFile = getProjectConfigFilename(@projectConfigurationPath);
			writeConfigFile($projectFile, %projectConfiguration);
		}
	}
	elsif ($a2 eq 'config') {
		my %new_config = readStdin();
		if ($a3 eq 'user') {
			if ($a4 eq 'true') {
				%userConfiguration = ();
			}
			while (my ($section, $v) = each(%new_config)) {
				while (my ($key, $value) = each(%{$v})) {
					$userConfiguration{"$section.$key"} = $value;
				}
			}
			my $userFile = getUserConfigFilename();
			writeConfigFile($userFile, %userConfiguration);
		}
		elsif ($a3 eq 'project' && @projectConfigurationPath) {
			if ($a4 eq 'true') {
				%projectConfiguration = ();
			}
			while (my ($section, $v) = each(%new_config)) {
				while (my ($key, $value) = each(%{$v})) {
					$projectConfiguration{"$section.$key"} = $value;
				}
			}
			my $projectFile = getProjectConfigFilename(@projectConfigurationPath);
			writeConfigFile($projectFile, %projectConfiguration);
		}
		else {
			exit(255);
		}
	}
	elsif ($a2 eq 'images' && @projectConfigurationPath) {
		my %new_config = readStdin();
		my @keys = keys %projectConfiguration;
		foreach my $key (@keys) {
			if ($key =~ /^[^2]+2[^+_]+(?:\+[^+_]+)*(?:_[^.]+)?\.(.+)$/) {
				my $param = $1;
				if (($a3 eq 'true' && $param ne 'include module') ||
				    ($a3 ne 'true' && $param eq 'files to convert')) {
					delete $projectConfiguration{$key};
				}
			}
		}
		while (my ($section, $v) = each(%new_config)) {
			while (my ($key, $value) = each(%{$v})) {
				if ($key ne 'automatic assignment' && $key ne 'overriden assignment') {
					$projectConfiguration{"$section.$key"} = $value;
				}
			}
		}
		my $projectFile = getProjectConfigFilename(@projectConfigurationPath);
		writeConfigFile($projectFile, %projectConfiguration);
	}
	else {
		exit(255);
	}
}
elsif (!$a1) {
	my $bn = basename($0);
	printComment(
		"$bn get config [all|system|user|project] ["._T("<section>")."]",
		_T("Output the configuration for the given level. If the 4th param is given, output only the section with this name. If section is \"__private__\", the hidden configuration is output."));
	printComment(
		"$bn get translators",
		_T("Output the list of the installed translators."));
	printComment(
		"$bn get conflits [resolved]",
		_T("Output the translators potentially under conflicts. If 'resolved' is given, apply the resolution mechanism."));
	printComment(
		"$bn get loads",
		_T("Output the loading directives for translators."));
	printComment(
		"$bn get images",
		_T("Output the list of figures detected by AutoLaTeX."));
	printComment(
		"$bn set config user|project [true|false]",
		_T("Read from STDIN an ini file that is a new configuration for the given level. The boolean param indicates if the configuration keys that are not given on STDIN will be removed (if true) or skipped (if false, the default) during the setting process."));
	printComment(
		"$bn set loads",
		_T("Read from STDIN an ini file for the loading directives of translators."));
	printComment(
		"$bn set images [true|false]",
		_T("Read from STDIN an ini file that is describing the attributes for the translators. The boolean param indicates if the configuration keys that are not given on STDIN will be removed (if true) or skipped (if false, the default) during the setting process."));
}
else {
	exit(255);
}

exit(0);
__END__

