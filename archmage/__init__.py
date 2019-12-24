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
__all__ = ['CHM']
__version__ = '0.4.1'

import sys, os, pkg_resources

# what config file to use - local or a system wide?
user_config = os.path.join(os.path.expanduser('~'), '.arch.conf')
if os.path.exists(user_config):
    config = user_config
else:
    config = pkg_resources.resource_filename('archmage', 'arch.conf')

def file2dir(filename):
    """Convert file filename.chm to filename_html directory"""
    dirname = filename.rsplit('.', 1)[0] + '_' + 'html'
    return dirname
