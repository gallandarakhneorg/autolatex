#!/usr/bin/perl

use strict;
use warnings;
use Getopt::Long;
use File::Basename;
use File::Spec;
use File::Copy;
use File::Path qw(remove_tree);
use Compress::Zlib;
use Archive::Zip;
use Pod::Text;
use Pod::Man;
use pp;

my %MODULES = ( 'core' => 1 , 'sty' => 1, 'gedit' => 1, 'gtk' => 1, 'sublime2' => 1 );

# GENERAL INSTALLATION INFORMATIONS
my $ALLOW_SYMBOLIC_LINK;
my $INSTALLDIRECTORY;
my $BINDIRECTORY;
my $ETCDIRECTORY;
my $MANDIRECTORY;
my $DOCDIRECTORY;
my $LOCALEDIRECTORY;
my $ICONDIRECTORY;
my $STYDIRECTORY;
my $GSETTINGSSCHEMADIRECTORY;
my $GEDITPLUGINDIRECTORY;
my $SUBLIME2PLUGINDIRECTORY;

my $EXE_EXTENSION = '.bin';
my %BINARY_FILES = (
	'core' => {
			'autolatex.pl' => {
				'name' => 'autolatex',
				'opts' => [],
			},
			'autolatex-backend.pl' => {
				'name' => 'autolatex-backend',
				'opts' => [],
			},
	},
	'gtk' => {
			'autolatex-gtk.pl' => {
				'name' => 'autolatex-gtk',
				'opts' => ['-gui'],
			},
	},
);

#------------------------------------------------------------------------------------------
sub dbg(@) {
	use Data::Dumper;
	die(Dumper(@_));
}

#------------------------------------------------------------------------------------------
sub printColumns($$@) {
	my $prefix = shift || '';
	my $sep = shift || '';
	my $len = 0;
	my $i;
	$i = 0;
	while ($i<@_) {
		my $l = length($_[$i]);
		if ($l>$len) {
			$len = $l;
		}
		$i += 2;
	}
	$i = 0;
	while ($i<@_) {
		my $l = length($_[$i]);
		print $prefix.$_[$i];
		$i++;
		while ($l<$len) {
			print ' ';
			$l++;
		}
		print $sep.$_[$i]."\n";
		$i++;
	}
}

#------------------------------------------------------------------------------------------
sub isArray($) {
	return 0 unless defined($_[0]) ;
	my $r = ref( $_[0] ) ;
	return ( $r eq "ARRAY" ) ;
}

#------------------------------------------------------------------------------------------
sub arrayContains(\@$) {
	if (!$_[0]) {
		return 0;
	}
	foreach my $e (@{$_[0]}) {
		if ($_[1] eq $e) {
			return 1;
		}
	}
	return 0;
}

#------------------------------------------------------------------------------------------
sub removeFromArray(\@@) {
	my @tab2 = @_;
	my $t = shift @tab2;
	my @tab = ();
	foreach my $e (@{$t}) {
		if (!arrayContains(@tab2,$e)) {
			push @tab, "$e";
		}
	}
	@{$_[0]} = @tab;
}

#------------------------------------------------------------------------------------------
sub substShellPatterns($) {
	my $t = '';
	$t = "$_[0]" if ($_[0]);
	if ($t) {
		$_[0] =~ s/^~([a-z_0-9]+)/
			my @l = getpwnam("$1");
			if (@l>=8) {
				"$l[7]";
			}
			else {
				"~$1";
			}
			/e;
		$_[0] =~ s/^~\//$ENV{'HOME'}\//;
	}
	return $_[0];
}

#------------------------------------------------------------------------------------------
sub gzipfct($) {
	my $targetfile = shift;
	local *IN;
	my $gz = gzopen("$targetfile.gz","wb") or die("$targetfile.gz: $!");
	open(*IN, "<", "$targetfile") or die("$targetfile: $!");
	while (<IN>) {
		$gz->gzwrite($_);
	}
	close(*IN);
	$gz->gzclose();
	unlink "$targetfile";
}

#------------------------------------------------------------------------------------------
sub rm($) {
	my $delfile = shift;
	if (-f "$delfile") {
		print "delete $delfile\n";
		unlink "$delfile";
	}
}

#------------------------------------------------------------------------------------------
sub getFilesRec($$@) {
	my $exceptions = shift || [];
	my $directory = shift;
	my $pattern = shift;
	my @list = ();
	if (($pattern)&&(-d "$directory")) {
		# Make a pattern
		my $repattern = "$pattern";
		$repattern =~ s/\./\\./g;
		$repattern =~ s/\*/.*/g;

		# Get the directory content
		my @subdirs = ();
		local *DIR;
		opendir(*DIR,"$directory")
			or die("$directory: $!\n");
		while (my $d = readdir(*DIR)) {
			if (($d ne File::Spec->curdir())&&($d ne File::Spec->updir())&&
			    ($d =~ /^$repattern$/) &&
			    (!arrayContains(@{$exceptions}, "$d"))) {
				my $full = File::Spec->catfile($directory,$d);
				if (-d "$full") {
					push @subdirs, "$full";
				}
				elsif (!@_) {
					push @list, "$full";
				}
			}
		}
		closedir(*DIR);

		# Go into sub directories
		foreach my $d (@subdirs) {
			my @l = &getFilesRec($exceptions,"$d", @_);
			push @list, @l;
		}
	}
	return @list;
}
sub getFiles(@) {
	my $firstpart = shift;
	my $exceptions;
	if (isArray($firstpart)) {
		$exceptions = $firstpart;
		$firstpart = shift;
	}
	else {
		$exceptions = [];
	}
	if ($firstpart) {
		return getFilesRec($exceptions, '.',$firstpart,@_);
	}
	else {
		return getFilesRec($exceptions, File::Spec->rootdir(),@_);
	}
}

#------------------------------------------------------------------------------------------
sub getDirectories(@) {
	my @list;
	local *DIR;
	foreach my $d (@_) {
		if (-d "$d") {
			opendir(*DIR,"$d") or die("$d: $!\n");
			while (my $sd = readdir(*DIR)) {
				if (($sd ne File::Spec->curdir())&&($sd ne File::Spec->updir())) {
					my $full = File::Spec->catfile($d,$sd);
					if (-d "$full") {
						push @list, "$full";
					}
				}
			}			
			closedir(*DIR);
		}
	}
	return @list;
}

#------------------------------------------------------------------------------------------
sub getDirectoryBasenames(@) {
	my @list;
	local *DIR;
	foreach my $d (@_) {
		if (-d "$d") {
			opendir(*DIR,"$d") or die("$d: $!\n");
			while (my $sd = readdir(*DIR)) {
				if (($sd ne File::Spec->curdir())&&($sd ne File::Spec->updir())) {
					my $full = File::Spec->catfile($d,$sd);
					if (-d "$full") {
						push @list, "$sd";
					}
				}
			}			
			closedir(*DIR);
		}
	}
	return @list;
}

#------------------------------------------------------------------------------------------
sub mkdirrec(@) {
	foreach my $dir (@_) {
		my @parts = File::Spec->splitdir($dir);
		my @np = ();
		foreach my $d (@parts) {
			if ($d) {
				my $rep = @np ? File::Spec->catdir(@np,$d) : $d;
				unless (-d "$rep") {
					mkdir("$rep") or die("$rep: $!\n");
					chmod 0755, "$rep";
				}
			}
			push @np, $d;
		}		
	}
}

#------------------------------------------------------------------------------------------
sub install($$;$) {
	my $sourcefile = shift;
	my $targetdir = shift;
	my $newbasename = shift || basename("$sourcefile");
	mkdirrec($targetdir);
	print "installing $sourcefile into $targetdir\n";
	my $fullname = File::Spec->catfile($targetdir,$newbasename);
	copy("$sourcefile","$fullname")
		or die("$sourcefile: $!\n");
	chmod 0644, "$fullname";	
	return $fullname;
}

#------------------------------------------------------------------------------------------
sub installLink($$;$) {
	return '' unless ($ALLOW_SYMBOLIC_LINK);
	my $sourcefile = File::Spec->rel2abs(shift);
	my $targetdir = File::Spec->rel2abs(shift);
	my $newbasename = shift || basename("$sourcefile");
	mkdirrec($targetdir);
	print "installing link $sourcefile into $targetdir\n";
	my $fullname = File::Spec->catfile($targetdir,$newbasename);
	my $linkname = File::Spec->abs2rel("$sourcefile","$targetdir");
	unlink("$fullname") if (-e "$fullname");
	symlink("$linkname","$fullname")
		or die("$sourcefile: $!\n");
	return $fullname;
}

#------------------------------------------------------------------------------------------
sub installExec($$;$) {
	my $fullname = install($_[0],$_[1],$_[2]);
	chmod 0755, "$fullname";	
	return $fullname;
}

#------------------------------------------------------------------------------------------
sub installCfg($;$) {
	return install($_[0],$ETCDIRECTORY,$_[1]);
}

#------------------------------------------------------------------------------------------
sub installBin($;$) {
	return installExec($_[0],$BINDIRECTORY,$_[1]);
}

#------------------------------------------------------------------------------------------
sub installLinkedBin($$;$) {
	my $fullname = installExec($_[0],$_[1]);
	my $linkname = installLink($fullname,$BINDIRECTORY,$_[2]);
	return ($fullname,$linkname);
}

#------------------------------------------------------------------------------------------
sub installMan(@) {
	my @result = ();
	my %mandirectories = ();
	foreach my $man (@_) {
		my @parts = File::Spec->splitdir($man);
		my @files = getFiles(@parts);
		die("$man: no manual file found\n") unless (@files);
		foreach my $f (@files) {
			my $base = basename($f);
			if ($base =~ /^(.*?)\.([a-z_]+)\.([0-9]+\.gz)$/) {
				my $lang = "$2";
				my $name = "$1.$3";
				unless ($mandirectories{"$lang"}) {
					my @l = File::Spec->splitdir($MANDIRECTORY);
					my $last = pop @l;
					push @l, $lang;
					push @l, $last;
					$mandirectories{"$lang"} = File::Spec->catfile(@l);
				}
				install($f,$mandirectories{"$lang"},$name);
			}
			else {
				push @result, install($f,$MANDIRECTORY);
			}
		}
	}
	return @result;
}

#------------------------------------------------------------------------------------------
sub installInto($@) {
	my $target = shift;
	my @result = ();
	foreach my $fileToInstall (@_) {
		push @result, install($fileToInstall, $target);
	}
	return @result;
}

#------------------------------------------------------------------------------------------
sub installExecInto($@) {
	my $target = shift;
	my @files = installInto($target,@_);
	foreach my $file (@files) {
		chmod 0755, "$file";
	}
	return @files;
}

#------------------------------------------------------------------------------------------
sub checkPMInstallation($@) {
	my $projectDir = shift || die("no project directory");
	my %installed = ();
	foreach my $file (@_) {
		print "checking Perl modules in ".basename($file)."\n";
		local *PMFILE;
		open(*PMFILE, "<$file") or die("$file: $!\n");
		while (my $line = <PMFILE>) {
			if ($line =~ /^\s*use\s+([A-Z][_A-Za-z0-9]+(?:\:\:[_A-Za-z0-9]+)*)/) {
				my $pack = $1;
				if (!$installed{$pack}) {
					my $ret = system("perl -e \"BEGIN{push \@INC, \\\"$projectDir\\\";} use $pack;\"");
					if ($ret != 0) {
						exit(255);
					}
					else {
						$installed{$pack} = 1;
					}
				}
			}
		}
		close(*PMFILE);
	}
	print "Detected Perl modules:\n";
	foreach my $key (keys %installed) {
		print "\t$key\n";
	}
}

#------------------------------------------------------------------------------------------
sub runPAR($$;$\@) {
	my $script_file = shift || die("script file not given\n");
	my $output_file = shift || die("output file not given\n");
	my $icon_file = shift || '';
	my $opts = shift || [];
	# Update the command line
	my @OLD_ARGV = @ARGV;
	@ARGV = ('-v', '-o', $output_file, '-I', File::Spec->rel2abs(File::Spec->catfile(dirname($0),'pm')), '-z', '9');
	if ($icon_file) {
		push @ARGV, '-i', "$icon_file";
	}
	if ($opts && @{$opts}) {
		push @ARGV, @{$opts};
	}
	push @ARGV, "$script_file";
	# Run the packager
	my $ret = pp->go();
	# Restore the command line
	@ARGV = @OLD_ARGV;
	return $ret;
}


#------------------------------------------------------------------------------------------
sub DO_compile(\%) {
	print "DO AUTOLATEX COMPILATION...\n";

	my @direlts = File::Spec->splitdir($_[0]->{'directory'});
	my @pmFiles = ();
	@pmFiles = (@pmFiles, getFiles(@direlts, 'pm', 'AutoLaTeX', 'Core', '*.pm'));
	@pmFiles = (@pmFiles, getFiles(@direlts, 'pm', 'AutoLaTeX', 'Interpreter', '*.pm'));
	@pmFiles = (@pmFiles, getFiles(@direlts, 'pm', 'AutoLaTeX', 'Make', '*.pm'));
	@pmFiles = (@pmFiles, getFiles(@direlts, 'pm', 'AutoLaTeX', 'TeX', '*.pm'));
	@pmFiles = (@pmFiles, getFiles(@direlts, 'pm', 'AutoLaTeX', 'GUI', '*.pm'));
	@pmFiles = (@pmFiles, getFiles(@direlts, 'pm', 'AutoLaTeX', 'Gtk', '*.pm'));
	@pmFiles = (@pmFiles, getFiles(@direlts, '*.pl'));
	checkPMInstallation(File::Spec->catfile($_[0]->{'directory'}, 'pm'), @pmFiles);

	local *DIR;
	local *DIR2;

	my $podDirectory = File::Spec->catfile($_[0]->{'directory'},'doc');
	my $poDirectory = File::Spec->catfile($_[0]->{'directory'},'po');

	# Generate the READMEs
	my $text_parser = Pod::Text->new('sentence'=>0, 'utf8'=>1);

	opendir(*DIR, "$podDirectory") or die("$podDirectory: $!\n");
	while (my $file = readdir(*DIR)) {
		if ($file =~ /^autolatex(?:_([^.]+))?\.pod$/) {
			my $loc = $1 || '';
			my $targetFile = "README";
			$targetFile .= '_'.uc($loc) if ($loc);
			print "Generating $targetFile...\n";
			$text_parser->parse_from_file(
				File::Spec->catfile("$podDirectory","$file"),
				File::Spec->catfile($_[0]->{'directory'},"$targetFile"));
		}
	}
	closedir(*DIR);

	# Generate the manuals
	my $man_parser = Pod::Man->new('release'=>$_[0]->{'version'}, section => 1, 'utf8'=>1);

	opendir(*DIR, "$podDirectory") or die("$podDirectory: $!\n");
	while (my $file = readdir(*DIR)) {
		if ($file =~ /^autolatex(?:_([^.]+))?\.pod$/) {
			my $loc = $1 || '';
			my $targetFile = "autolatex";
			$targetFile .= '.'.lc($loc) if ($loc);
			$targetFile .= '.1';
			print "Generating $targetFile...\n";
			$text_parser->parse_from_file(
				File::Spec->catfile("$podDirectory","$file"),
				File::Spec->catfile("$podDirectory","$targetFile"));
			gzipfct(File::Spec->catfile("$podDirectory","$targetFile"));
		}
	}
	closedir(*DIR);

	# Generate the program translations
	opendir(*DIR,"$poDirectory") or die("$poDirectory: $!\n");
	while (my $topdir = readdir(*DIR)) {
		if (($topdir ne File::Spec->curdir())&&($topdir ne File::Spec->updir())) {
			my $subdirectory = File::Spec->catdir($poDirectory,$topdir,'LC_MESSAGES');
			opendir(*DIR2,"$subdirectory") or next;
			while (my $pofile = readdir(*DIR2)) {
				if ($pofile =~ /\.po$/i) {
					print "Generating translations for $pofile...\n";
					my $mofile = $pofile;
					$mofile =~ s/\.po/.mo/i;
					system('msgfmt','-v','-o',
						File::Spec->catfile("$subdirectory","$mofile"),
						File::Spec->catfile("$subdirectory","$pofile"));
				}
			}
			closedir(*DIR2);
		}
	}
	closedir(*DIR);

	# Create the Sublime Text Package
	{
		my $sublime_root_tmp = File::Spec->catfile('build', 'sublime2');
		my $sublime_tmp = File::Spec->catfile($sublime_root_tmp, 'autolatex');
		my $sublime_tmp_file = 'autolatex.sublime-package';
		mkdirrec($sublime_tmp);
		installInto(
			File::Spec->catfile($sublime_tmp, 'utils'),
			getFiles('python','utils','*'));
		installInto(
			$sublime_tmp,
			getFiles('plugins','sublime-text-2','*'));		
		installInto(
			File::Spec->catfile($sublime_tmp, 'utils'),
			getFiles('plugins','sublime-text-2','utils','*'));
		chdir($sublime_root_tmp) or die("$sublime_root_tmp: $!\n");
		my $zip = Archive::Zip->new();
		local *DIR;
		my @dirs = ( basename($sublime_tmp) );
		while (@dirs) {
			my $dir = shift @dirs;
			print "adding $dir...\n";
			$zip->addDirectory( $dir );
			opendir(*DIR, "$dir") or die("$dir: $!\n");
			while (my $f = readdir(*DIR)) {
				if ($f ne File::Spec->curdir() &&
				    $f ne File::Spec->updir()) {
					my $fn = File::Spec->catfile($dir, $f);
					if (-d "$fn") {
						push @dirs, $fn;
					}
					else {
						$zip->addFile($fn);
					}
				}
			}
			closedir(*DIR);
		}
		$zip->writeToFileNamed($sublime_tmp_file);
		chdir('..') or die("..: $!\n");
	}
}

#------------------------------------------------------------------------------------------
sub DO_install(\%) {
	print "DO AUTOLATEX INSTALLATION...\n";
	my @po_directories = getDirectoryBasenames('po');

	if ($MODULES{'core'}) {
		my $need_pm_files = 0;
		if (($_[0]->{'create-links'})&&($_[0]->{'create-bin-links'})) {
			while (my ($scriptfile, $binfile) = each(%{$BINARY_FILES{'core'}})) {
				if (-f $binfile->{'name'}.$EXE_EXTENSION) {
					installLinkedBin(
						$binfile->{'name'}.$EXE_EXTENSION,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
				else {
					$need_pm_files = 1;
					installLinkedBin(
						$scriptfile,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
			}
		}
		else {
			while (my ($scriptfile, $binfile) = each(%{$BINARY_FILES{'core'}})) {
				if (-f $binfile->{'name'}.$EXE_EXTENSION) {
					installExec(
						$binfile->{'name'}.$EXE_EXTENSION,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
				else {
					$need_pm_files = 1;
					installExec(
						$scriptfile,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
			}
		}
		install('AUTHORS', $INSTALLDIRECTORY);
		install('VERSION', $INSTALLDIRECTORY);
		if (($_[0]->{'create-links'})&&($_[0]->{'create-etc-links'})) {
			my $cfgFile = installCfg('default.ist');
			installLink($cfgFile,$INSTALLDIRECTORY);
			$cfgFile = installCfg('default.cfg','config');
			installLink($cfgFile,$INSTALLDIRECTORY,'default.cfg');
		}
		else {
			install('default.ist',$INSTALLDIRECTORY);
			install('default.cfg',$INSTALLDIRECTORY);
		}

		installInto(
			File::Spec->catfile($INSTALLDIRECTORY,'translators'),
			getFiles('translators','*'));

		if ($need_pm_files) {
			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'Core'),
				getFiles('pm','AutoLaTeX','Core','*.pm'));

			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'Interpreter'),
				getFiles('pm','AutoLaTeX','Interpreter','*.pm'));

			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'Make'),
				getFiles('pm','AutoLaTeX','Make','*.pm'));

			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX', 'TeX'),
				getFiles('pm','AutoLaTeX','TeX','*.pm'));
		}


		foreach my $lang (@po_directories) {
			install(
				File::Spec->catfile('po',"$lang",'LC_MESSAGES','autolatex.mo'),
				File::Spec->catfile($INSTALLDIRECTORY,'po',"$lang",'LC_MESSAGES'));
		}

		installInto(
			$DOCDIRECTORY,
			getFiles('doc','*.pod'));

		installMan(File::Spec->catfile('doc', 'autolatex.1.gz'));
		installMan(File::Spec->catfile('doc', 'autolatex.fr.1.gz'));
	}

	if ($MODULES{'gtk'}) {
		my $need_pm_files = 0;
		if (($_[0]->{'create-links'})&&($_[0]->{'create-bin-links'})) {
			while (my ($scriptfile, $binfile) = each(%{$BINARY_FILES{'gtk'}})) {
				if (-f $binfile->{'name'}.$EXE_EXTENSION) {
					installLinkedBin(
						$binfile->{'name'}.$EXE_EXTENSION,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
				else {
					$need_pm_files = 1;
					installLinkedBin(
						$scriptfile,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
			}
		}
		else {
			while (my ($scriptfile, $binfile) = each(%{$BINARY_FILES{'gtk'}})) {
				if (-f $binfile->{'name'}.$EXE_EXTENSION) {
					installExec(
						$binfile->{'name'}.$EXE_EXTENSION,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
				else {
					$need_pm_files = 1;
					installExec(
						$scriptfile,
						$INSTALLDIRECTORY,
						$binfile->{'name'}.$EXE_EXTENSION);
				}
			}
		}
		if ($need_pm_files) {
			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX','GUI'),
				getFiles('pm','AutoLaTeX','GUI','*.pm'));

			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX','GUI'),
				getFiles('pm','AutoLaTeX','GUI','*.png'));

			installInto(
				File::Spec->catfile($INSTALLDIRECTORY,'pm','AutoLaTeX','GUI','Gtk'),
				getFiles('pm','AutoLaTeX','GUI','Gtk','*.pm'));
		}
		foreach my $lang (@po_directories) {
			install(
				File::Spec->catfile('po',"$lang",'LC_MESSAGES','autolatexgtk.mo'),
				File::Spec->catfile($INSTALLDIRECTORY,'po',"$lang",'LC_MESSAGES'));
		}
	}

	if ($MODULES{'sty'}) {
		installInto(
			$STYDIRECTORY,
			getFiles('sty','*'));
	}
	
	if ($MODULES{'gedit'}) {
		installInto(
			$GEDITPLUGINDIRECTORY,
			getFiles('plugins', 'gedit','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex'),
			getFiles('plugins', 'gedit','autolatex','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','config'),
			getFiles('plugins', 'gedit','autolatex','config','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','config','cli'),
			getFiles('plugins', 'gedit','autolatex','config','cli','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','config','plugin'),
			getFiles('plugins', 'gedit','autolatex','config','plugin','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','ui'),
			getFiles('plugins', 'gedit','autolatex','ui','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','utils'),
			getFiles('python','utils','*'));
		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','utils'),
			getFiles('plugins', 'gedit','autolatex','utils','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','widgets'),
			getFiles('plugins', 'gedit','autolatex','widgets','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','icons','24'),
			getFiles('plugins', 'gedit','autolatex','icons','24','*'));

		installInto(
			File::Spec->catfile($GEDITPLUGINDIRECTORY,'autolatex','icons','16'),
			getFiles('plugins', 'gedit','autolatex','icons','16','*'));

		installInto(
			$GSETTINGSSCHEMADIRECTORY,
			getFiles('schemas', '*.gschema.xml'));

		installInto(
			$GSETTINGSSCHEMADIRECTORY,
			getFiles('schemas', '*.gschema.xml'));

		foreach my $lang (@po_directories) {
			install(
				File::Spec->catfile('po',"$lang",'LC_MESSAGES','geditautolatex.mo'),
				File::Spec->catfile($LOCALEDIRECTORY,"$lang",'LC_MESSAGES'));
		}

		install(
			File::Spec->catfile('icons','autolatex-icon.png'),
			$ICONDIRECTORY);
	}

	if ($MODULES{'sublime2'}) {
		print "***************\n*** CAUTION ***\n***************\n";
		print "Sublime Text 2 module will be installed in:\n$SUBLIME2PLUGINDIRECTORY\n";
		print "***************\n*** CAUTION ***\n***************\n";

		installInto(
			$SUBLIME2PLUGINDIRECTORY,
			File::Spec->catfile('build','sublime2','autolatex.sublime-package'));

		foreach my $lang (@po_directories) {
			install(
				File::Spec->catfile('po',"$lang",'LC_MESSAGES','sublime-text-2-autolatex.mo'),
				File::Spec->catfile($LOCALEDIRECTORY,"$lang",'LC_MESSAGES'));
		}
	}
}

#------------------------------------------------------------------------------------------
sub DO_clean(\%) {
	print "DO AUTOLATEX CLEANING...\n";
	#rm(File::Spec->catfile($_[0]->{'directory'},'README'));
	rm(File::Spec->catfile($_[0]->{'directory'},'README_FR'));
	rm(File::Spec->catfile($_[0]->{'directory'},'doc','autolatex.1.gz'));
	rm(File::Spec->catfile($_[0]->{'directory'},'doc','autolatex.fr.1.gz'));

	local *DIR;
	local *DIR2;
	my $directory = File::Spec->catdir($_[0]->{'directory'},'po');
	opendir(*DIR,"$directory") or die("$directory: $!\n");
	while (my $topdir = readdir(*DIR)) {
		if (($topdir ne File::Spec->curdir())&&($topdir ne File::Spec->updir())) {
			my $subdirectory = File::Spec->catdir($directory,$topdir,'LC_MESSAGES');
			opendir(*DIR2,"$subdirectory") or next;
			while (my $mofile = readdir(*DIR2)) {
				if ($mofile =~ /\.mo$/i) {
					rm(File::Spec->catfile("$subdirectory","$mofile"));
				}
			}
			closedir(*DIR2);
		}
	}
	closedir(*DIR);

	foreach my $module (values %BINARY_FILES) {
		foreach my $bin_file (values %{$module}) {
			rm(File::Spec->catfile(
				$_[0]->{'directory'},
				$bin_file->{'name'}.$EXE_EXTENSION));
		}
	}

	remove_tree('build');

	rm(File::Spec->catfile($_[0]->{'directory'},'Makefile'));
}

#------------------------------------------------------------------------------------------
sub DO_par(\%) {
	print "DO AUTOLATEX PACKAGING...\n";
	foreach my $module (values %BINARY_FILES) {
		while (my ($script_file, $bin_file) = each(%{$module})) {
			runPAR($script_file, $bin_file->{'name'}.$EXE_EXTENSION,
				undef, @{$bin_file->{'opts'}});
		}
	}
}

#------------------------------------------------------------------------------------------
sub DO_vars(\%) {
	printColumns('', '  ',
		'ALLOW_SYMBOLIC_LINK', $ALLOW_SYMBOLIC_LINK,
		'BINDIRECTORY', $BINDIRECTORY,
		'DOCDIRECTORY', $DOCDIRECTORY,
		'ETCDIRECTORY', $ETCDIRECTORY,
		'ICONDIRECTORY', $ICONDIRECTORY,
		'INSTALLDIRECTORY', $INSTALLDIRECTORY,
		'GEDITPLUGINDIRECTORY', $GEDITPLUGINDIRECTORY,
		'GSETTINGSSCHEMADIRECTORY', $GSETTINGSSCHEMADIRECTORY,
		'LOCALEDIRECTORY', $LOCALEDIRECTORY,
		'MANDIRECTORY', $MANDIRECTORY,
		'STYDIRECTORY', $STYDIRECTORY,
		'SUBLIME2PLUGINDIRECTORY', $SUBLIME2PLUGINDIRECTORY);
}

#------------------------------------------------------------------------------------------
sub DO_createMakefile(\%) {
	print "CREATING MAKEFILE...\n";
	local *OUT;

	my @options = ();
	if ($_[0]->{'version'}) {
		push @options, '"--version='.$_[0]->{'version'}.'"';
	}
	if ($_[0]->{'prefix'}) {
		push @options, '"--prefix='.$_[0]->{'prefix'}.'"';
	}
	if ($_[0]->{'man-prefix'}) {
		push @options, '"--manprefix='.$_[0]->{'man-prefix'}.'"';
	}
	if ($_[0]->{'doc-prefix'}) {
		push @options, '"--docprefix='.$_[0]->{'doc-prefix'}.'"';
	}
	if ($_[0]->{'etc-prefix'}) {
		push @options, '"--etcprefix='.$_[0]->{'etc-prefix'}.'"';
	}
	if ($_[0]->{'tex-prefix'}) {
		push @options, '"--texprefix='.$_[0]->{'tex-prefix'}.'"';
	}
	if ($_[0]->{'sublime2-prefix'}) {
		push @options, '"--sublime2prefix='.$_[0]->{'sublime2-prefix'}.'"';
	}
	if ($_[0]->{'create-links'}) {
		push @options, '"--link"';
	}
	else {
		push @options, '"--nolink"';
	}
	if ($_[0]->{'create-etc-links'}) {
		push @options, '"--etclink"';
	}
	else {
		push @options, '"--noetclink"';
	}
	if ($_[0]->{'create-bin-links'}) {
		push @options, '"--binlink"';
	}
	else {
		push @options, '"--nobinlink"';
	}

	while (my ($module,$enable) = each(%MODULES)) {
		if ($enable) {
			push @options, "\"--enable=$module\"";
		}
		else {
			push @options, "\"--disable=$module\"";
		}
	}

	my $options = join(' ',@options);

	my $filename = File::Spec->catfile($_[0]->{'directory'},"Makefile");
	open(*OUT, "> $filename") or die("$filename: $!\n");
	print OUT "all:\n";
	print OUT "\t@ perl ".__FILE__." $options compile\n\n";
	print OUT "par:\n";
	print OUT "\t@ perl ".__FILE__." $options par\n\n";
	print OUT "install:\n";
	print OUT "\t@ perl ".__FILE__." $options install\n\n";
	print OUT "clean:\n";
	print OUT "\t@ perl ".__FILE__." $options clean\n\n";
	close(*OUT);
}

#------------------------------------------------------------------------------------------
my %options = ();
$options{'directory'} = File::Spec->rel2abs(dirname(__FILE__));
$options{'create-links'} = 1;
$options{'create-bin-links'} = 1;
$options{'create-etc-links'} = 1;

# Detect the version number
local *FILE;
open(*FILE,"<".File::Spec->catfile($options{'directory'},'VERSION'))
	or die(File::Spec->catfile($options{'directory'},'VERSION').":$!\n");
while (my $line = <FILE>) {
	if ($line =~ /^\s*autolatex\s*([0-9\-a-z\.]+)\s*$/i) {
		$options{'version'} = "$1";
	}
}
close(*FILE);

# Read command line
if (!GetOptions(
		'sublime2prefix=s' => \$options{'sublime2-prefix'},
		'texprefix=s' => \$options{'tex-prefix'},
		'etcprefix=s' => \$options{'etc-prefix'},
		'manprefix=s' => \$options{'man-prefix'},
		'docprefix=s' => \$options{'doc-prefix'},
		'prefix=s' => \$options{'prefix'},
		'version=s' => \$options{'version'},
		'link!' => \$options{'create-links'},
		'binlink!' => \$options{'create-bin-links'},
		'etclink!' => \$options{'create-etc-links'},
		'enable=s' => sub { if (exists $MODULES{$_[1]}) { $MODULES{$_[1]} = 1; } },
		'disable=s' => sub { if (exists $MODULES{$_[1]}) { $MODULES{$_[1]} = 0; } },
		'modules' => sub {
					foreach my $module (keys %MODULES) {
						print STDOUT "$module\n";
					}
					exit(255);
				},
		'help' => sub {
				print basename($0)." <options> <action>\n";
				print "<action> is one of:\n";
				printColumns('   ', '  ',
					'compile', 'compile the software',
					'install', 'install the software',
					'clean', 'clean the directory',
					'par', 'create binary files');
				print "<options> are:\n";
				printColumns('   ', '  ',
					'--disable', 'disable module',
					'--docprefix=<path>', 'path to documentation directory',
					'--[no]etclink', 'enable/disable config\'s symbolic links',
					'--enable', 'enable module',
					'--etcprefix=<path>', 'path to config directory',
					'--[no]link', 'enable/disable symbolic links',
					'--manprefix=<path>', 'path to manual directory',
					'--modules', 'list the modules',
					'--prefix=<path>', 'path to root installation directory',
					'--sublime2prefix=<path>', 'path to the directory of Sublime Text 2',
					'--texprefix=<path>', 'path to TeX directory',
					'--version=<text>', 'set software version');
				exit(255);
			},
		)) {
	exit(1);
}

# Detect action
$options{'action'} = 'unknow';
foreach my $act (@ARGV) {
	if ($act eq 'compile') {
		$options{'action'} = 'compile';
	}
	elsif ($act eq 'install') {
		$options{'action'} = 'install';
	}
	elsif ($act eq 'clean') {
		$options{'action'} = 'clean';
	}
	elsif ($act eq 'par') {
		$options{'action'} = 'par';
	}
	elsif ($act eq 'vars') {
		$options{'action'} = 'vars';
	}
}

# Set the paths
if (("$^O" eq 'MSWin32')||
    ("$^O" eq 'NetWare')||
    ("$^O" eq 'symbian')) {
	# Win32 compatible platform
	$ALLOW_SYMBOLIC_LINK = 0;

	my $PREFIX = substShellPatterns($options{'prefix'}) || File::Spec->catfile('C:','Program Files');
	my $ETCPREFIX = "$PREFIX";
	my $MANPREFIX = substShellPatterns($options{'man-prefix'}) || File::Spec->catfile('C:','Documents and Settings','All Users','Application Data');
	my $DOCPREFIX = substShellPatterns($options{'doc-prefix'}) || File::Spec->catfile('C:','Documents and Settings','All Users','Application Data');
	my $TEXPREFIX = substShellPatterns($options{'tex-prefix'}) || File::Spec->catfile($PREFIX,'autolatex','sty');

	$EXE_EXTENSION = '.exe';
	$INSTALLDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex');
	$BINDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex');
	$ETCDIRECTORY = File::Spec->catfile("$ETCPREFIX",'autolatex');
	$MANDIRECTORY = File::Spec->catfile("$MANPREFIX",'autolatex','doc');
	$DOCDIRECTORY = File::Spec->catfile("$MANPREFIX",'autolatex','doc');
	$LOCALEDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex', 'locale');
	$ICONDIRECTORY = File::Spec->catfile("$PREFIX",'autolatex', 'icons');
	$STYDIRECTORY = File::Spec->catfile("$TEXPREFIX",'tex','latex','autolatex');
	$GEDITPLUGINDIRECTORY = File::Spec->catfile("$PREFIX",'gedit','plugins','autolatex');
	$GSETTINGSSCHEMADIRECTORY = File::Spec->catfile("$PREFIX",'glib-2.0','schemas');
	$SUBLIME2PLUGINDIRECTORY = File::Spec->catfile((substShellPatterns($options{'sublime2-prefix'}) || File::Spec->catfile("$PREFIX",'Sublime Text 2')), 'Pristine Packages');
}
else {
	# Unix compatible platform
	$ALLOW_SYMBOLIC_LINK = 1;

	my $PREFIX = substShellPatterns($options{'prefix'}) || File::Spec->catfile('','usr','local');
	my $end = File::Spec->catfile('usr','local');
	if ($PREFIX =~ /\Q$end\E$/) {
		$end = File::Spec->catfile("$PREFIX",'..','..','etc');
	}
	else {
		$end = File::Spec->catfile("$PREFIX",'..','etc');
	}
	my $ETCPREFIX = substShellPatterns($options{'etc-prefix'}) || $end;
	my $MANPREFIX = substShellPatterns($options{'man-prefix'}) || File::Spec->catfile($PREFIX,'share','man');
	my $DOCPREFIX = substShellPatterns($options{'doc-prefix'}) || File::Spec->catfile($PREFIX,'share','doc');
	my $TEXPREFIX = substShellPatterns($options{'tex-prefix'}) || File::Spec->catfile($PREFIX,'share','texmf');

	$EXE_EXTENSION = '';
	$INSTALLDIRECTORY = File::Spec->catfile("$PREFIX",'lib','autolatex');
	$BINDIRECTORY = File::Spec->catfile("$PREFIX",'bin');
	$ETCDIRECTORY = File::Spec->catfile("$ETCPREFIX",'autolatex');
	$MANDIRECTORY = File::Spec->catfile("$MANPREFIX",'man1');
	$DOCDIRECTORY = File::Spec->catfile("$DOCPREFIX",'autolatex');
	$LOCALEDIRECTORY = File::Spec->catfile("$PREFIX",'share', 'locale');
	$ICONDIRECTORY = File::Spec->catfile("$PREFIX",'share', 'icons');
	$STYDIRECTORY = File::Spec->catfile("$TEXPREFIX",'tex','latex','autolatex');
	$GEDITPLUGINDIRECTORY = File::Spec->catfile("$PREFIX",'lib','gedit','plugins','autolatex');
	$GSETTINGSSCHEMADIRECTORY = File::Spec->catfile("$PREFIX",'share','glib-2.0','schemas');

	if ("$^O" eq "rhapsody") {
		$SUBLIME2PLUGINDIRECTORY = File::Spec->catfile((substShellPatterns($options{'sublime2-prefix'})  || File::Spec->catfile($ENV{'HOME'}, 'Library', 'Application Support', 'Sublime Text 2' )), 'Pristine Packages');
	}
	else {
		$SUBLIME2PLUGINDIRECTORY = File::Spec->catfile((substShellPatterns($options{'sublime2-prefix'})  || File::Spec->catfile($ENV{'HOME'}, '.config', 'sublime-text-2')), 'Pristine Packages');
	}
}

# Run the action
if ($options{'action'} ne 'unknow') {
	eval("DO_".$options{'action'}.'(%options);');
	die"$@\n" if ($@);
}
else {
	DO_createMakefile(%options);
}

exit(0);

__END__

