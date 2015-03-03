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

import urllib
import mimetypes

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import archmod


class CHMServer(HTTPServer):
    """HTTP Server that handle Compressed HTML"""

    def __init__(self, CHM, name='', port=8000):
        self.address = (name, port)
        self.httpd = HTTPServer(self.address, CHMRequestHandler)
        self.httpd.CHM = CHM
        self.address = (name, port)

    def run(self):
        self.httpd.serve_forever()


class CHMRequestHandler(BaseHTTPRequestHandler):
    """This class handle HTTP request for CHMServer"""

    def do_GET(self):
        pagename = urllib.unquote(self.path.split('?')[0])
        if pagename == '/':
            mimetype = 'text/html'
        else:
            mimetype = mimetypes.guess_type(pagename)[0]

        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

        # get html data from CHM instance and write it into output
        try:
            self.wfile.write(self.server.CHM.get_entry(pagename))
        except NameError, msg:
            archmod.message(archmod.ERROR, 'NameError: %s' % msg)
