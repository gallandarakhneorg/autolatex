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

require 5.004;

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
use AutoLaTeX::Core::Translator;

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

setDebugLevel(0);

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
			foreach my $k (keys %cfgOutput) {
				if ($k !~ /^\Q$a4.\E/) {
					delete $cfgOutput{$k};
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
	else {
		exit(255);
	}
}
elsif (!$a1) {
	my $bn = basename($0);
	print STDERR "\$> $bn get config [all|system|user|project] [<section>]\n";
	print STDERR "\tOutput the configuration for the given level.\n";
	print STDERR "\tIf the 4th param is given, output only the section with\n";
	print STDERR "\tthis name.\n\n";
	print STDERR "\$> $bn get translators\n";
	print STDERR "\tOutput the list of the installed translators.\n\n";
	print STDERR "\$> $bn get conflits [resolved]\n";
	print STDERR "\tOutput the translators potentially under conflicts.\n";
	print STDERR "\tIf 'resolved' is given, apply the resolution mechanism.\n\n";
	print STDERR "\$> $bn get loads\n";
	print STDERR "\tOutput the loading directives for translators.\n\n";
	print STDERR "\$> $bn set config user|project [true|false]\n";
	print STDERR "\tRead from STDIN an ini file that is a new configuration for\n";
	print STDERR "\tthe given level. The boolean param indicates if the configuration\n";
	print STDERR "\tkeys that are not given on STDIN will be removed (if true) or\n";
	print STDERR "\tskipped (if false, the default) during the setting process.\n\n";
	print STDERR "\$> $bn set loads\n";
	print STDERR "\tRead from STDIN an ini file for the loading directives of\n";
	print STDERR "\ttranslators.\n";
}
else {
	exit(255);
}

exit(0);
__END__

