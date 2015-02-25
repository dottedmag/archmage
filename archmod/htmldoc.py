# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 Basil Shubin <bashu@users.sourceforge.net>

"""Generic converter function"""

import os
import string
import tempfile
import subprocess
import archmod


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
        f.write('#HTMLDOC 1.8.27' + archmod.LF)
        f.write(options + archmod.LF)
        f.write(string.join(input, archmod.LF))
        f.close()
        # Prepare command line to execute
        command = '%s --batch %s' % (cmd, f.name)
        subprocess.call(command, shell=True)
        # Unlink temporary htmldoc file
        os.unlink(f.name)
