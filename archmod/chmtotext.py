# -*- coding: utf-8 -*-
#
# Copyright (c) 2005-2009 Basil Shubin <bashu@users.sourceforge.net>

"""CHM to Text converter (using external tool: lynx or elinks)"""

import sys
import signal
from subprocess import Popen, PIPE

signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def chmtotext(input, cmd, output=sys.stdout):
	"""CHM to Text converter"""
	proc = Popen(cmd, stdin=PIPE, stdout=PIPE, shell=True)
	proc.stdin.write(input)
	print >> output, proc.communicate()[0]
