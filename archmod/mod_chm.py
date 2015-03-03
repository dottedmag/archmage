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

from mod_python import apache
from mimetypes import guess_type
from archmod.CHM import CHMFile

chmfile = None
chmname = None


def handler(req):
    source = req.filename
    pagename = req.path_info

    global chmfile, chmname

    if chmname != source:
        chmfile = CHMFile(source)

    chmname = source

    if pagename:
        try:
            page = chmfile.get_entry(pagename)
        except:
            return apache.HTTP_NOT_FOUND

        if pagename == '/':
            mimetype = 'text/html'
        else:
            mimetype = guess_type(pagename)[0] or 'application/octet-stream'

        req.content_type = mimetype
        req.send_http_header()

        req.write(page)
    else:
        mimetype = 'application/chm'
        req.content_type = mimetype
        req.send_http_header()
        file = open(source, 'rb')
        while 1:
            tmp = file.read(4096)
            if len(tmp) == 0:
                break
            req.write(tmp)
    return apache.OK
