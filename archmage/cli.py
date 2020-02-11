# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2003 Eugeny Korekin <aaaz@users.sourceforge.net>
# Copyright (c) 2005-2009 Basil Shubin <bashu@users.sourceforge.net>
# Copyright (c) 2015,2019 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

"""arCHMage -- extensible reader and decompiler for files in the CHM format.

Usage: %(program)s [options] <chmfile> [destdir|destfile]
Where:

    -x / --extract
        Extracts CHM file into specified directory. If destination
        directory is omitted, than the new one will be created based
        on name of CHM file. This options is by default.

    -c format
    --convert=format
        Convert CHM file into specified file format. If destination
        file is omitted, than the new one will be created based
        on name of CHM file. Available formats:

            html - Single HTML file
            text - Plain Text file
            pdf - Adobe PDF file format

    -d / --dump
        Dump HTML data from CHM file into standard output.

    -V / --version
        Print version number and exit.

    -h / --help
        Print this text and exit.
"""

import os, sys
import getopt

import archmage
from archmage.CHM import CHM, Action

# Return codes
OK = 0
ERROR = 1

program = sys.argv[0]


# Miscellaneous auxiliary functions
def message(code=OK, msg=""):
    outfp = sys.stdout
    if code == ERROR:
        outfp = sys.stderr
    if msg:
        print(msg, file=outfp)


def usage(code=OK, msg=""):
    """Show application usage and quit"""
    message(code, __doc__ % globals())
    message(code, msg)
    sys.exit(code)


def output_format(mode):
    if mode == "text":
        return Action.CHM2TXT
    elif mode == "html":
        return Action.CHM2HTML
    elif mode == "pdf":
        return Action.CHM2PDF
    else:
        sys.exit("Invalid output file format: %s" % mode)


def output_file(filename, mode):
    """Convert filename.chm to filename.output"""
    if mode == Action.CHM2TXT:
        file_ext = "txt"
    elif mode == Action.CHM2HTML:
        file_ext = "html"
    elif mode == Action.CHM2PDF:
        file_ext = "pdf"
    else:
        file_ext = "output"
    output_filename = filename.rsplit(".", 1)[0] + "." + file_ext
    return output_filename


def parseargs():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "xc:dp:Vh",
            ["extract", "convert=", "dump", "port=", "version", "help"],
        )
    except getopt.error as msg:
        usage(ERROR, msg)

    class Options:
        mode = None  # EXTRACT or other
        chmfile = None  # CHM File to view/extract
        output = None  # Output file or directory

    options = Options()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-V", "--version"):
            message(OK, archmage.__version__)
            sys.exit(OK)
        elif opt in ("-c", "--convert"):
            if options.mode is not None:
                sys.exit("-x and -c are mutually exclusive")
            options.mode = output_format(str(arg))
        elif opt in ("-x", "--extract"):
            if options.mode is not None:
                sys.exit("-x and -c are mutually exclusive")
            options.mode = Action.EXTRACT
        elif opt in ("-d", "--dump"):
            if options.mode is not None:
                sys.exit("-d should be used without any other options")
            options.mode = Action.DUMPHTML
        else:
            assert False, (opt, arg)

    # Sanity checks
    if options.mode is None:
        # Set default option
        options.mode = Action.EXTRACT

    if not args:
        sys.exit("No CHM file was specified!")
    else:
        # Get CHM file name from command line
        options.chmfile = args.pop(0)

    # if CHM content should be extracted
    if options.mode == Action.EXTRACT:
        if not args:
            options.output = archmage.file2dir(options.chmfile)
        else:
            # get output directory from command line
            options.output = args.pop(0)
    # or converted into another file format
    elif options.mode in (Action.CHM2TXT, Action.CHM2HTML, Action.CHM2PDF):
        if not args:
            options.output = output_file(options.chmfile, options.mode)
        else:
            # get output filename from command line
            options.output = args.pop(0)

    # Any other arguments are invalid
    if args:
        sys.exit("Invalid arguments: " + ", ".join(args))

    return options


def main():
    options = parseargs()
    if not os.path.exists(options.chmfile):
        sys.exit("No such file: %s" % options.chmfile)

    source = CHM(options.chmfile)

    if options.mode == Action.DUMPHTML:
        source.dump_html()
    elif options.mode == Action.CHM2TXT:
        if os.path.exists(options.output):
            sys.exit("%s is already exists" % options.output)
        source.chm2text(open(options.output, "w"))
    elif options.mode in (Action.CHM2HTML, Action.CHM2PDF):
        source.htmldoc(options.output, options.mode)
    elif options.mode == Action.EXTRACT:
        source.extract(str(options.output))

    source.close()
