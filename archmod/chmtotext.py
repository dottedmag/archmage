# -*- coding: utf-8 -*-
#
# Copyright (c) 2005-2008 Basil Shubin <bashu@users.sourceforge.net>

''' CHM to Text convertor (using external tool: lynx or elinks)'''

import sys
import signal
from subprocess import Popen, PIPE

signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def chmtotext(input, cmd, output=sys.stdout):
	""" Html to Text convertor """
	proc = Popen(cmd, stdin=PIPE, stdout=PIPE, shell=True)
	proc.stdin.write(input)
	print >> output, proc.communicate()[0]
