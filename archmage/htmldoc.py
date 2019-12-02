# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2009 Basil Shubin <bashu@users.sourceforge.net>
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

"""Generic converter function"""

import os
import string
import tempfile
import subprocess
import archmage


def htmldoc(input, cmd, options, toclevels, output):
    """CHM to other format converter

        input - list of input html files
        cmd - full path to htmldoc command
        options - htmldoc options from arch.conf
        toclevels - number of ToC levels as htmldoc option
        output - output file (single html, ps, pdf and etc)
    """
    if toclevels:
        toc = ('--toclevels %s' % (toclevels))
    else:
        toc = ('--no-toc')
    options = options % {'output' : output, 'toc' : toc}
    if input:
        # Create a htmldoc file for batch processing
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('#HTMLDOC 1.8.27\n')
        f.write(options + '\n')
        f.write(string.join(input, '\n'))
        f.close()
        # Prepare command line to execute
        command = '%s --batch %s' % (cmd, f.name)
        subprocess.call(command, shell=True)
        # Unlink temporary htmldoc file
        os.unlink(f.name)
