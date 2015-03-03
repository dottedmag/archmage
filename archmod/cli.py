# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2003 Eugeny Korekin <aaaz@users.sourceforge.net>
# Copyright (c) 2005-2009 Basil Shubin <bashu@users.sourceforge.net>
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

    -p number
    --port=number
        Acts as HTTP server on specified port number, so you can read
        CHM file with your favorite browser. You can specify a directory
        with decompressed content.

    -d / --dump
        Dump HTML data from CHM file into standard output.

    -V / --version
        Print version number and exit.

    -h / --help
        Print this text and exit.
"""

import os, sys
import getopt

import archmod
from archmod.CHM import CHMFile, CHMDir
from archmod.CHMServer import CHMServer


program = sys.argv[0]

def usage(code=archmod.OK, msg=''):
    """Show application usage and quit"""
    archmod.message(code, __doc__ % globals())
    archmod.message(code, msg)
    sys.exit(code)


def parseargs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'xc:dp:Vh',
                                ['extract', 'convert=', 'dump', 'port=', 'version', 'help'])
    except getopt.error, msg:
        usage(archmod.ERROR, msg)

    class Options:
        mode = None        # EXTRACT or HTTPSERVER or other
        port = None        # HTTP port number
        chmfile = None     # CHM File to view/extract
        output = None      # Output file or directory

    options = Options()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-V', '--version'):
            archmod.message(archmod.OK, archmod.__version__)
            sys.exit(archmod.OK)
        elif opt in ('-p', '--port'):
            if options.mode is not None:
                sys.exit('-x and -p or -c are mutually exclusive')
            options.mode = archmod.HTTPSERVER
            try:
                options.port = int(arg)
            except ValueError, msg:
                sys.exit('Invalid port number: %s' % msg)
        elif opt in ('-c', '--convert'):
            if options.mode is not None:
                sys.exit('-x and -p or -c are mutually exclusive')
            options.mode = archmod.output_format(str(arg))
        elif opt in ('-x', '--extract'):
            if options.mode is not None:
                sys.exit('-x and -p or -c are mutually exclusive')
            options.mode = archmod.EXTRACT
        elif opt in ('-d', '--dump'):
            if options.mode is not None:
                sys.exit('-d should be used without any other options')
            options.mode = archmod.DUMPHTML
        else:
            assert False, (opt, arg)

    # Sanity checks
    if options.mode is None:
        # Set default option
        options.mode = archmod.EXTRACT

    if not args:
        sys.exit('No CHM file was specified!')
    else:
        # Get CHM file name from command line
        options.chmfile = args.pop(0)

    # if CHM content should be extracted
    if options.mode == archmod.EXTRACT:
        if not args:
            options.output = archmod.file2dir(options.chmfile)
        else:
            # get output directory from command line
            options.output = args.pop(0)
    # or converted into another file format
    elif options.mode in (archmod.CHM2TXT, archmod.CHM2HTML, archmod.CHM2PDF):
        if not args:
            options.output = archmod.output_file(options.chmfile, options.mode)
        else:
            # get output filename from command line
            options.output = args.pop(0)

    # Any other arguments are invalid
    if args:
        sys.exit('Invalid arguments: ' + archmod.COMMASPACE.join(args))

    return options


def main():
    options = parseargs()
    if not os.path.exists(options.chmfile):
        sys.exit('No such file: %s' % options.chmfile)

    # Check where is argument a CHM file or directory with decompressed
    # content. Depending on results make 'source' instance of CHMFile or
    # CHMDir class.
    source = os.path.isfile(options.chmfile) and \
        CHMFile(options.chmfile) or CHMDir(options.chmfile)

    if options.mode == archmod.HTTPSERVER:
        CHMServer(source, port=options.port).run()
    elif options.mode == archmod.DUMPHTML:
        source.dump_html()
    elif options.mode == archmod.CHM2TXT:
        if os.path.exists(options.output):
            sys.exit('%s is already exists' % options.output)
        source.chm2text(open(options.output, 'w'))
    elif options.mode in (archmod.CHM2HTML, archmod.CHM2PDF):
        source.htmldoc(options.output, options.mode)
    elif options.mode == archmod.EXTRACT:
        source.extract(options.output)
