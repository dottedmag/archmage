# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 Basil Shubin <bashu@users.sourceforge.net>

"""Generic converter function"""

import string
import subprocess


def htmldoc(input, cmd, toclevels, output):
	"""CHM to other format converter

		input - list of input html files
		cmd - htmldoc command with options
		toclevels - ToC levels as htmldoc option
		output - output file (single html, ps, pdf and etc)
	"""
	command = cmd
	if toclevels is not None:
		command += (' --toclevels %s' % (toclevels))
	command += (' --outfile %s' % (output))
	files = string.join(input)
	if len(files):
		command = command + ' ' + files
		subprocess.call(command, shell=True)
