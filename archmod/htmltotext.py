#!/usr/bin/env python
#
# Html to Text convertor (using external tool: lynx or elinks)

import sys
import signal
from subprocess import Popen, PIPE

signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def htmltotext(input, cmd, output=sys.stdout):
	""" Html to Text convertor """
	proc = Popen(cmd, stdin=PIPE, stdout=PIPE, shell=True)
	proc.stdin.write(input)
	print >> output, proc.communicate()[0]
