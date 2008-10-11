# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 Basil Shubin <bashu@users.sourceforge.net>

'''Converting CHM into single HTML file'''

import sys
import string
import subprocess


def chmtohtml(input, cmd, toclevels, output):
    """ CHM to single HTML file convertor """
    command = cmd
    if toclevels is not None:
            command += (" --toclevels %s" % (toclevels))
    command += (" --outfile %s" % (output))
    files = string.join(input)
    if len(files):
        command = command + " " + files
        subprocess.call(command, shell=True)
