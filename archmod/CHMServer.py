# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2003 Eugeny Korekin <aaaz@users.sourceforge.net>
# Copyright (c) 2005-2009 Basil Shubin <bashu@users.sourceforge.net>
# Copyright (c) 2015 Mikhail Gusarov <dottedmag@dottedmag.net>
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

import archmod.CHM
import BaseHTTPServer
import mimetypes
import os.path
import urlparse, urllib

class DirectoryTraversalError(Exception):
    pass

class ChmServer(BaseHTTPServer.HTTPServer, object):
    def __init__(self, basedir, bind_address, port):
        super(ChmServer, self).__init__((bind_address, port), ChmRequestHandler)
        self.basedir = basedir
        self.cache_open = {}

def find_file(f, path):
    path_parts = map(urllib.unquote, path.split('/')[1:])
    while True:
        if os.path.isfile(f):
            return f, ''.join('/'+p for p in path_parts)
        if not os.path.isdir(f) or not path_parts:
            return (None, None)
        part = path_parts.pop(0)
        if part == '..' or '/' in part:
            raise DirectoryTraversalError()
        f = os.path.join(f, part)

def get_mimetype(page_path):
    if page_path == '/':
        return 'text/html'
    guessed_type = mimetypes.guess_type(page_path)[0]
    if guessed_type:
        return guessed_type
    return 'application/octet-stream'

def get_chm(cache, filename):
    if filename not in cache:
        cache[filename] = archmod.CHM.CHMFile(filename)
    return cache[filename]

def send_file(wfile, filename):
    with open(filename, 'rb') as fh:
        buf = fh.read(4096)
        while buf:
            wfile.write(buf)
            buf = fh.read(4096)

class ChmRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def ok(self, mimetype):
        self.send_response(200)
        self.send_header('Content-Type', mimetype)
        self.end_headers()

    def err(self, code):
        self.send_response(code)
        self.end_headers()

    def send_plain(self, filename):
        self.ok('application/chm')
        send_file(self.wfile, filename)

    def send_page(self, filename, page_path):
        chm = get_chm(self.server.cache_open, filename)
        if not chm:
            return self.err(500)
        try:
            page = chm.get_entry(page_path)
            if page:
                self.ok(get_mimetype(page_path))
                self.wfile.write(page)
                return
        except NameError, e:
            pass
        self.err(404)

    def do_GET(self):
        url = urlparse.urlparse(self.path)
        try:
            (filename, path) = find_file(self.server.basedir, url.path)
        except DirectoryTraversalError, e:
            return self.err(500)
        if filename and path:
            return self.send_page(filename, path)
        if filename:
            return self.send_plain(filename)
        self.err(404)
