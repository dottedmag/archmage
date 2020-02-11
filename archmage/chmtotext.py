# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
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

"""CHM to Text converter (using external tool: lynx or elinks)"""

import sys
import signal
from subprocess import Popen, PIPE

if sys.platform != "win32":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def chmtotext(input, cmd, output=sys.stdout):
    """CHM to Text converter"""
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, shell=True)
    proc.stdin.write(input)
    print(proc.communicate()[0], file=output)
