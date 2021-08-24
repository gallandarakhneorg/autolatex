from setuptools import setup, find_packages
import re
import os

# Read the program information
with open(os.path.join('src', 'autolatex2', 'VERSION'), 'r', encoding='utf-8') as fh:
    line = fh.read()
    m = re.match('^([^ ]+)\\s+(.*?)\\s*$', line)
    if m:
    	name = m.group(1)
    	version = m.group(2)
    else:
    	raise Exception("Cannot read VERSION file")

# Setup
setup(
    name=name,
    version=version,
    author="Stephane Galland",
    author_email="galland@arakhne.org",
    description="AutoLaTeX is a tool for managing LaTeX documents",
    url="https://github.com/gallandarakhneorg/autolatex",
    license='GPL',
    project_urls={
        "Bug Tracker": "https://github.com/gallandarakhneorg/autolatex/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
	"abc",
	"argparse",
	"base64",
	"configparser",
	"Crypto",
	"dataclasses",
	"enum",
	"fnmatch",
	"gettext",
	"importlib",
	"inspect",
	"io",
	"json",
	"logging",
	"os",
	"platform",
	"pprint",
	"re",
	"setuptools>=42",
	"shlex",
	"shutil",
	"subprocess",
	"sys",
	"textwrap",
	"yaml",
    ],
    package_dir={"":"src"},
    packages=find_packages(where='src', exclude=("tests")),
    entry_points=dict(
        console_scripts=['autolatex=autolatex2.cli.autolatex:main']
    ),
    include_package_data = True,
    package_data={
        "": ["VERSION", "*.ist", "*.cfg", "translators/*.transdef2"],
    }
)
