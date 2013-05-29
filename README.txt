NAME
    autolatex - compile TeX documents

SYNOPSIS
    autolatex [options] target [target ...]

DESCRIPTION
    AutoLaTeX is a tool for managing small to large sized LaTeX documents.
    The user can easily perform all required steps to do such tasks as:
    preview the document, or produce a PDF file. AutoLaTeX will keep track
    of files that have changed and how to run the various programs that are
    needed to produce the output. One of the best feature of AutoLaTeX is to
    provide translator rules (aka. translators) to automatically generate
    the figures which will be included into the PDF.

    As a quick example, consider a project, which has a single LaTeX file
    "mydoc.tex", as its input. Without AutoLaTeX, to produce a ".pdf" file
    you might use the following sequence of commands:

         C<pdflatex mydoc.tex>
         C<bibtex mydoc.tex>
         C<pdflatex mydoc.tex>
         C<pdflatex mydoc.tex>
         C<pdflatex mydoc.tex>

    The triple invocation of LaTeX is to ensure that all references have
    been properly resolved and any page layout changes due to inserting the
    references have been accounted for. The sequence of commands isn't
    horrible, but it still is several commands. To use AutoLaTeX for this
    project, you would use one of the following the command lines:

         C<autolatex -f mydoc.tex>
         C<autolatex>

    For documents, which may need to run programs to create the PDF versions
    of the drawings, which are included into the PDF document, or run BibTeX
    to generate bibliographies, the generation of the ".pdf" (or other)
    files becomes increasingly complicated to run manually. With AutoLaTeX,
    such operations are still very simple: you have nothing to do. AutoLaTeX
    is calling the translators for you. Each translator is able to convert
    an picture source file (eps, svg, GNU plot...) into a PDF or PNG file.

    Hopefully this introduction has provided an adequate example for how
    AutoLaTeX can simplify the management of LaTeX-based documents. The
    AutoLaTeX system is simple enough for small projects and powerful enough
    for large projects. The remainder of this manual will provide complete
    documentation on the use of AutoLaTeX as well as configuration and
    installation instructions.

TARGETS
    AutoLaTeX provides a fixed set of targets, the arguments to pass to
    AutoLaTeX to run a module, for all projects. The default target is all.

    The targets provided by AutoLaTeX are:

    all Same as view, except that the viewer is launched only if the
        configuration or the CLI is enabling the viewer.

    bibtex
        Performs all processing that permits to generate the bibliography
        (bibtex).

    clean
        Cleans the current working directory by removing all LaTeX temp
        files and other temp files created during processing of the project.

    cleanall
        Same as clean. In addition, emacs ~ files and other backup files are
        removed. The generated figures and the produced PDF are also
        removed.

    commit
        Commit the changes into a SCM system (CVS, SVN, GIT).

    gen_doc
        Performs all processing required to produce the .pdf/.dvi/.ps file
        for the project.

    images
        Performs the automatic generation of the figures.

    makeflat
        Create a version of the document inside the subdirectory
        'flat_version' in which there is a single TeX file, and all the
        other files are inside the same directory of the TeX file. This
        action is helpful to create a version of the document that may be
        directly upload on online publication sites (such as Elsevier). This
        action use the CLI option "--bibtex" to determine if the
        bibliography must be put in a BibTeX file or inline inside the TeX
        file (default is inline).

    makeindex
        Performs all processing that permits to generate the index
        (makeindex).

    showimages
        Display the filenames of the figures.

    showpath
        Show the value of the environment variable PATH

    showvars
        DEPRECATED.

    update
        Update the local copy with the changes from a SCM system (CVS, SVN,
        GIT).

    view
        Same as gen_doc. In addition launch the document viewer.

OPTIONS
    --[no]auto
        Enable or disable the auto generation of the figures.

    --[no]bibtex
        Enable or disable the call to bibtex.

    --createconfig[=type]
        Do not compile the LaTeX document, but create a configuration file.
        The created configuration file depends on the type value. If the
        type is equal to project, AutoLaTeX will create the configuration
        file dedicated to a project. Otherwhise it will create the
        configuration file for the user level. The project configuration
        file is "path/to/project/.autolatex_project.cfg" on Unix platforms,
        and "path\to\project\autolatex_project.cfg" on other platforms. The
        default user configuration file is "$HOME/.autolatex" on Unix
        platforms, "C:\Documents and Settings\User\Local
        Settings\Application Data\autolatex.conf" on Windows platforms, and
        "$HOME/autolatex.conf" on other plateforms.

    --createist
        Create a default MakeIndex style file into the project directory.
        The created file will be named 'default.ist'. If a file with this
        name already is existing, it will be overwritten.

    --createmakefile
        DEPRECATED.

    --defaultist
        Allow AutoLaTeX to use MakeIndex with the default style (ist file).
        The default style is provided by AutoLaTeX.

        The options --index and --noindex also permit to change the behavior
        of AutoLaTeX against MakeIndex

    --dvi
        Do the compilation to produce a DVI or a XDV document.

    --exclude=name
        Avoid AutoLaTeX to load the translator called name. See bellow for
        the available translators.

        The option --include permits to include a translator; and the option
        -I permits to specify where to find translator scripts.

    -f=file
    --file=file
        Specify the main LaTeX file to compile. If this option is not
        specified, AutoLaTeX will search for a TeX file in the current
        directory.

    --fixconfig[=file]
        Fix the syntax of a configuration file. If the file is not specified
        on the command line, AutoLaTeX will try to fix the project
        configuration, or the user configuration if no project configuration
        file was found.

    -?
    --help
        Display this manual.

    -I=paths
        Notify AutoLaTeX that it could find translator scripts inside the
        specified directories. The specified path could be a list of paths
        separated by the operating system's path separator (':' on Unix, ';'
        for Windows for example).

        The option --exclude permits to exclude a translator; and the option
        --include permits to exclude a translator.

    --imgdirectory=directory
        Specify a directy inside which AutoLaTeX will find the pictures
        which must be processed by the translators. Each time this option is
        put on the command line, a directory is added inside the list of the
        directories to explore.

    --include=name
        Force AutoLaTeX to load the translator called name. See bellow for
        the available translators.

        The option --exclude permits to exclude a translator; and the option
        -I permits to specify where to find translator scripts.

    --index[=style_file]
        Allow AutoLaTeX to use MakeIndex.

        If this option was specified with a value, the style_file value will
        be assumed to be an .ist file to pass to MakeIndex.

        If this option was specified without a value, AutoLaTeX will use
        MakeIndex and tries to detect a MakeIndex style file (.ist file)
        inside the project directory. If no project's .ist file was found,
        AutoLaTeX will not pass a style to MakeIndex.

        The options --defaultist and --noindex also permit to change the
        behavior of AutoLaTeX against MakeIndex

    --latex
        Use the historical LaTeX command: "latex".

    --lualatex
        Use the LaTeX command: "lualatex".

    --noindex
        Avoid AutoLaTeX to use MakeIndex.

        The options --index and --defaultist also permit to change the
        behavior of AutoLaTeX against MakeIndex

    -o=directory
    --output=directory
        DEPRECATED.

    --pdf
        Do the compilation to produce a PDF document.

    --pdflatex
        Use the LaTeX command: "pdflatex".

    --ps
        Do the compilation to produce a Postscript document, when possible.

    -q =item --quiet
        AutoLaTeX should be not verbose (see -v for changing the verbose
        level).

    --set [translator.]name=value
        Set the internal value of AutoLaTeX named name with the specified
        value. Internal values are limited and corresponds to the "set"
        directives from the configuration file syntax.

        If translator is given, it is the name of the translator for which
        the value must ve overridden. If translator is not given then
        "generation" is the default prefix.

    -v  Each time this option was specified, AutoLaTeX is more verbose. Note
        that 1) if you put 5 times the -v option on the command line,
        AutoLaTeX will consider the Perl warnings as errors; 2) if you put 6
        times the -v option on the command line, AutoLaTeX is stopping
        immediately, and is displaying the current configuration in memory.

    --version
        Display the version of AutoLaTeX.

    --view[=file]
    --noview
        Enable or disable the document viewer at the end of the compilation.
        The path of the document viewer could be specify with file. If not
        specified, AutoLaTeX will check for the tools acroread, kpdf,
        evince, gv, and xpdf.

    --xelatex
        Use the LaTeX command: "xelatex".

AUTO GENERATION OF FIGURES
    A translator is used to convert a source figure into a target figure
    which is supported by LaTeX. This converter is an external program (eg.
    epstopdf) or an internal Perl script.

    Each supported translator is described inside a .transdef file. This
    file contains the definition of the variables for the shell command line
    to launch or the Perl code to use. To create a new translator, we
    recommend to copy/paste an existing ".transdef" file and change its
    content. Even if you excluded a translator from the the command line, it
    is automatically included by AutoLaTeX when it is invoked by an included
    translator.

    The provided translators are:

    Astah/Jude (asta) to Portable Document Format (pdf)

        Name: astah2pdf
        Use external converter: astah-uml, astah-pro
        Use translator: svg2pdf
        Input format: .asta .jude .juth
        Output format: .pdf

    Astah/Jude (asta) to Portable Network Graphic (png)

        Name: astah2png
        Use external converter: astah-com, astah-uml, astah-pro
        Use translator:
        Input format: .asta .jude .juth
        Output format: .png

    C/C++ Source Code (.cpp, .c, .hpp, .h) to TeX Source Code (tex): TeXify
    variante

        Name: cpp2tex_texify
        Use external converter: texifyc++
        Use translator:
        Input format: .cpp, .c, .hpp, .h, .c++, .h++
        Output format: .tex

    Compressed Bitmap to Uncompressed Bitmap
        based on zcat tool. This translator assumes that input files are
        compressed. The input filename extensions is '.gz'. This translator
        permits to store in the project compressed figures as raw material
        for the LaTeX compiler. The bitmaps are uncompressed in a file with
        the same name as the source, except that the '.gz' was removed from
        the name.

        Name: imggz2img
        Use external converter: zcat
        Use translator:
        Input format: XXX.gz
        Output format: XXX

    Diagram Editor (dia) to Portable Document Format (pdf)

        Name: dia2pdf
        Use external converter: dia
        Use translator: eps2pdf
        Input format: .dia
        Output format: .pdf

    Dot Graphviz (dot) to Portable Document Format (pdf)

        Name: dot2pdf
        Use external converter: dot
        Use translator:
        Input format: .dot
        Output format: .pdf

    Dot Graphviz (dot) to Portable Network Graphic (png)

        Name: dot2png
        Use external converter: dot
        Use translator:
        Input format: .dot
        Output format: .png

    Dot Graphviz (dot) to TeX (tex)

        Name: dot2tex
        Use external converter: dot
        Use translator:
        Input format: .dot
        Output format: .tex

    Encapsuled PostScript (eps) to Portable Document Format (pdf)

        Name: eps2pdf_epstopdf
        Use external converter: epstopdf
        Use translator:
        Input format: .eps
        Output format: .pdf

    Encapsuled PostScript (eps) to Portable Document Format (pdf)

        Name: eps2pdf_ps2pdf
        Use external converter: ps2pdf
        Use translator:
        Input format: .eps
        Output format: .pdf

    XFig document (fig) to Portable Document Format (pdf)

        Name: fig2pdf
        Use external converter: fig2dev
        Use translatr:
        Input format: .fig
        Output format: .pdf

    XFig document (fig) to TeX embedded in Portable Document Format
    (pdf+tex)
        PDF part:

        Name: fig2pdf+tex
        Use external converter: fig2dev
        Use translator:
        Input format: .fig_tex .figt .figtex .fig+tex
        Output format: .pdf

        TeX part:

        Name: fig2pdf+tex
        Use external converter: fig2dev
        Use translator:
        Input format: .fig_tex .figt .figtex .fig+tex
        Output format: .pdftex_t

    Graph eXchange Language (gxl) to Portable Document Format (pdf)

        Name: gxl2pdf
        Use external converter: gxl2dot
        Use translator: dot2pdf
        Input format: .gxl
        Output format: .pdf

    Graph eXchange Language (gxl) to Portable Network Graphic (png)

        Name: gxl2png
        Use external converter: gxl2dot
        Use translator: dot2png
        Input format: .gxl
        Output format: .png

    Java Source Code (java) to TeX Source Code (tex): TeXify variante

        Name: java2tex_texify
        Use external converter: texifyjava
        Use translator:
        Input format: .java
        Output format: .tex

    Lisp Script (lisp) to TeX Source Code (tex): TeXify variante

        Name: lisp2tex_texify
        Use external converter: texifylisp
        Use translator:
        Input format: .lisp
        Output format: .tex

    MatLab Script (m) to TeX Source Code (tex): TeXify variante

        Name: matlab2tex_texify
        Use external converter: texifymatlab
        Use translator:
        Input format: .m
        Output format: .tex

    ML Script (ml) to TeX Source Code (tex): TeXify variante

        Name: ml2tex_texify
        Use external converter: texifyml
        Use translator:
        Input format: .ml
        Output format: .tex

    Perl Script (perl) to TeX Source Code (tex): TeXify variante

        Name: perl2tex_texify
        Use external converter: texifyperl
        Use translator:
        Input format: .perl .pl
        Output format: .tex

    GNU plot (plot) to Portable Document Format (pdf)

        Name: plot2pdf
        Use external converter: gnuplot
        Use translator: eps2pdf
        Input format: .plot
        Output format: .pdf

    GNU plot (plot) to TeX embedded in Portable Document Format (pdf+tex)
        PDF part:

        Name: plot2pdf+tex
        Use external converter: gnuplot
        Use translator: eps2pdf
        Input format: .plot_tex .plottex .plott .plot+tex
        Output format: .pdf

        TeX part:

        Name: plot2pdf+tex
        Use external converter: gnuplot
        Use translator:
        Input format: .plot_tex .plottex .plott .plot+tex
        Output format: .pdftex_t

    Python Source Code (py) to TeX Source Code (tex): TeXify variante

        Name: python2tex_texify
        Use external converter: texifypython
        Use translator:
        Input format: .py
        Output format: .tex

    Ruby Source Code (rb) to TeX Source Code (tex): TeXify variante

        Name: ruby2tex_texify
        Use external converter: texifyruby
        Use translator:
        Input format: .rb
        Output format: .tex

    SQL Script (sql) to TeX Source Code (tex): TeXify variante

        Name: sql2tex_texify
        Use external converter: texifysql
        Use translator:
        Input format: .sql
        Output format: .tex

    Scalable Vector Graphic (svg) to Portable Document Format (pdf)

        Name: svg2pdf
        Use external converter: inkscape
        Use translator: eps2pdf
        Input format: .svg
        Output format: .pdf

    Scalable Vector Graphic (svg) to Portable Network Graphic (png)

        Name: svg2png
        Use external converter: inkscape
        Use translator:
        Input format: .svg
        Output format: .png

    UML Metadata Interchange (xmi) to Portable Document Format (pdf):
    Umbrello variante

        Name: xmi2pdf_umbrello
        Use external converter: umbrello
        Use translator: eps2pdf
        Input format: .xmi
        Output format: .pdf

    UML Metadata Interchange (xmi) to Portable Document Format (pdf):
    uml2svg variante

        Name: xmi2pdf_uml2svg
        Use external converter: uml2svg
        Use translator: svg2pdf
        Input format: .xmi
        Output format: .pdf

    UML Metadata Interchange (xmi) to Portable Document Format (pdf):
    xmi2svg variante

        Name: xmi2pdf_xmi2svg
        Use external converter: xmi2svg
        Use translator: svg2pdf
        Input format: .xmi
        Output format: .pdf

LATEX STYLE PACKAGE
    AutoLaTeX provides a LaTeX style called "autolatex.sty". It provides the
    following functions:

    \includefigurewtex{width}{filename}
        include a figure from a .pdftex_t file.

CONFIGURATION FILE
  Location of the Configuration Files
    The configuration files used by AutoLaTex could be a several places:

    *   System Configuration (for all users): inside the directory where
        AutoLaTeX was installed (usually /usr/lib/autolatex on Unix
        systems).

    *   User Configuration: two cases: the configuration directory named
        $HOME/.autolatex on Unix, or
        C:\Documents and Settings\<user>\Local Settings\Application Data\aut
        olatex on Windows exists; or not.

        In the first case, the configuration file is stored inside the
        directory and is named autolatex.conf.

        In the second case, the configuration file is inside the user
        directory and is named $HOME/.autolatex on Unix, and
        C:\Documents and Settings\<user>\Local Settings\Application Data\aut
        olatex.conf on Windows.

    *   Project Configuration: the configuration file in the same directory
        as the main TeX file of the project. It is named
        .autolatex_project.cfg on Unix and autolatex_project.cfg on Windows.

  Syntax of the Configuration Files
    The configuration files respect a syntax similar to the Windows .ini
    files.

    A comment starts with the characters '#' or ';' and it finishes at the
    end of the line.

    Each configuration directive must be inside a configuration section. A
    configuration section is declared by its name between brackets. Example:
    "[mysection]"

    Each directive must be declared as: "directive name = value"

    Several section names are reserved by AutoLaTeX, the others are assumed
    to be the configuration for the translators.

   [Viewer] section
    This section permits to configure the viewer used by AutoLaTeX. The
    recognized directives are:

    *view* : Indicates if AutoLaTeX must launch a viewer after LaTeX
    compilation. Accepted values: "yes" or "no".
    *viewer* : Is the path or the command line of the viewer to launch.
    Accepted value: any command line.

   [Generation] section
    This section permits to configure the generation process used by
    AutoLaTeX. The recognized directives are:

    *main file* : specifies the basename of the main TeX file to compile.
    This option is available only inside the project's configuration file.
    *generate images* : indicates if AutoLaTeX automatically generates the
    figures. Accepted values: "yes" or "no"
    *image directory* : Specify the directories inside which AutoLaTeX will
    find the pictures which must be processed by the translators. Each time
    this option is put on the command line, a directory is added inside the
    list of the directories to explore. The different paths are separated by
    the path-separator character (':' on Unix, ';' on Windows).
    *generation type* : indicates the type of generation. Accepted values:

        "pdf" - generate a PDF document
        "dvi" - generate a DVI or a XDV document
        "ps" - generate a PS document

    *tex compiler* : indicates the TeX compiler to use. Accepted values:

        "latex" - use "latex"
        "pdflatex" - use "pdflatex"
        "xelatex" - use "xelatex"
        "lualatex" - use "lualatex"

    *makeindex style* : specifies the style that must be used by makeindex.
    This is a list of values separated by comas. The values should be:

        "<filename>" - if a filename was specified, AutoLaTeX assumes that
        it is the .ist file;
        @system - AutoLaTeX uses the system default .ist file (in AutoLaTeX
        distribution);
        @detect - AutoLaTeX will tries to find a .ist file in the project's
        directory. If none was found, AutoLaTeX will not pass a style to
        makeindex;
        @none - AutoLaTeX assumes that no .ist file must be passed to
        MakeIndex;
        "<empty>" - AutoLaTeX assumes that no .ist file must be passed to
        MakeIndex.

        If the list contains more than one value, AutoLaTeX will do the
        corresponding behaviors in turn.

    *translator include path* : specifies additional directories from which
    translator scripts could be loaded. This is a list of paths separated by
    comas or the path separator of your operating system (: on Unix, ; on
    Windows). If a path contains a coma character, you must enclose it in
    quotes.
    *latex_cmd* : specifies the LaTeX tool command line. Accepted value: any
    command line.
    *bibtex_cmd* : specifies the BibTeX tool command line. Accepted value:
    any command line.
    *makeindex_cmd* : specifies the MakeIndex tool command line. Accepted
    value: any command line.
    *dvi2ps_cmd* : specifies the dvips tool command line. Accepted value:
    any command line.
    *latex_flags* : specifies the options to pass to the LaTeX tool.
    Accepted value: any command line.
    *bibtex_flags* : specifies the options to pass to the BibTeX tool.
    Accepted value: any command line.
    *makeindex_flags* : specifies the options to pass to the MakeIndex tool.
    Accepted value: any command line.
    *dvi2ps_flags* : specifies the options to pass to the dvips tool.
    Accepted value: any command line.

   [Clean] section
    This section permits to configure the cleaning features of AutoLaTeX
    (targets clean and cleanall). The recognized directives are:

    *files to clean* : is a list of files to remove when the target 'clean'
    is invoked. Shell wildcards are allowed.
    *files to desintegrate* : is a list of files to remove when the target
    'cleanall' is invoked. Shell wildcards are allowed.

   [Scm] section
    This section permits to configure the SCM support of AutoLaTeX (CVS, SVN
    or others). The recognized directives are:

    *scm commit* : specifies the command line to use when commit the
    changes.
    *scm update* : specified the command line to use when update the local
    copy.

   Translator section
    A translator section has the same name as the translator it configures.
    The recognized directives are:

    *include module* : indicates if the translator should be loaded by
    default. Accepted values: "yes" or "no".

GRAPHIC USER INTERFACE
    A graphical user interface is available since version 5.0 to configure
    and launch AutoLaTeX process.

    The available user interfaces are:

    autolatex-gtk : a GTK-based user interface.

BUG REPORT AND FEEDBACK
    To report bugs, provide feedback, suggest new features, etc. visit the
    AutoLaTeX Project management page at <http://www.arakhne.org/autolatex/>
    or send email to the author at galland@arakhne.org.

SYSTEM REQUIREMENTS
    AutoLaTeX may be directly used from any directory where it is
    uncompressed. But you may want to compile and install the additional
    files (manual...)

    To configure and install AutoLaTeX, you will need GNU make.

    You need to install the package Compress::Zlib to compile and install
    AutoLaTeX. This package is not required for the execution of AutoLaTeX.
    In addition, to compile AutoLaTeX, you need to install the 'msgfmt'
    command which is a part of 'gettext'.

    To use AutoLaTeX, you will require:

    latex. The development of AutoLaTeX was done using the TeX Live
    distribution.
    Either Perl version 5.004 or higher.
    Several Perl packages usually installed in your Perl distribution:
    Config::Simple, Locale::gettext, Spec::File...

INSTALLATION
    Installation of AutoLaTeX consists of launching the Makefile.PL script
    to generate a Makefile that permits to compile and install AutoLaTeX.
    The basic commands are:

    "cd path_to_autoloader_sources/"

    "perl ./Makefile.PL --prefix=/usr"

    "make"

    "make install"

    "make clean"

AUTOLATEX LICENSE
    GNU Public License (GPL)

    Copyright (c) 1998-2013 Stephane GALLAND <galland@arakhne.org>

    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License
    <http://www.gnu.org/copyleft/gpl.html> as published by the Free Software
    Foundation <http://www.fsf.org/>; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
    Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; see the file COPYING. If not, write to the Free
    Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
    02111-1307, USA.

MANUAL COPYRIGHT
    GNU Free Documentation License (FDL)

    Copyright (c) 1998-2013 Stephane Galland <galland@arakhne.org>.

    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License
    <http://www.gnu.org/licenses/fdl.txt>, Version 1.2 or any later version
    published by the Free Software Foundation <http://www.fsf.org/>; with
    the Invariant Sections being AUTOLATEX LICENSE and MANUAL COPYRIGHT, no
    Front-Cover Texts, and no Back-Cover Texts. A copy of the license is
    included in the file name GNU Free Documentation License.txt.

SEE ALSO
    pdflatex, latex, bibtex, epstopdf, fig2dev, gnuplot, inkscape, umbrello,
    zcat, texify

