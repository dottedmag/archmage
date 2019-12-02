# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2009 Basil Shubin <bashu@users.sourceforge.net>
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

import re
import mimetypes
import sgmllib, urllib.request, urllib.error, urllib.parse

from bs4 import BeautifulSoup, UnicodeDammit
from html.parser import HTMLParser
from urllib.parse import urlparse

START_TAG = '['
END_TAG = ']'


class SitemapFile(object):
    """Sitemap file class"""

    def __init__(self, lines):
        # XXX: Cooking tasty beautiful soup ;-)
        if lines:
            soup = BeautifulSoup(lines, 'html.parser')
            lines = soup.prettify()
            # XXX: Removing empty tags
            lines = re.sub(re.compile(r'<ul>\s*</ul>', re.I | re.M), '', lines)
            lines = re.sub(re.compile(r'<li>\s*</li>', re.I | re.M), '', lines)
            self.lines = lines
        else:
            self.lines = None

    def parse(self):
        p = SitemapParser()
        if self.lines:
            p.feed(self.lines)
        # parsed text + last bracket
        return (p.parsed + '\n' + END_TAG)


class TagStack(list):
    """from book of David Mertz 'Text Processing in Python'"""

    def append(self, tag):
        # Remove every paragraph-level tag if this is one
        if tag.lower() in ('p', 'blockquote'):
            self = TagStack([ t for t in super if t not in ('p', 'blockquote') ])
        super(TagStack, self).append(tag)

    def pop(self, tag):
        # 'Pop' by tag from nearest position, not only last item
        self.reverse()
        try:
            pos = self.index(tag)
        except ValueError:
            raise Error('Tag not on stack')
        self[:] = self[pos + 1:]
        self.reverse()


class SitemapParser(sgmllib.SGMLParser):
    """Class for parsing files in SiteMap format, such as .hhc"""

    def __init__(self):
        self.tagstack = TagStack()
        self.in_obj = False
        self.name = self.local = self.param = ""
        self.imagenumber = 1
        self.parsed = ""
        sgmllib.SGMLParser.__init__(self)

    def unknown_starttag(self, tag, attrs):
        # first ul, start processing from here
        if tag == 'ul' and not self.tagstack:
            self.tagstack.append(tag)
            # First bracket
            self.parsed += '\n' + START_TAG

        # if inside ul
        elif self.tagstack:
            if tag == 'li':
                # append closing bracket if needed
                if self.tagstack[-1] != 'ul':
                    self.parsed += END_TAG
                    self.tagstack.pop('li')
                indent = ' ' * len(self.tagstack)

                if self.parsed != '\n' + START_TAG:
                    self.parsed += ', '

                self.parsed += '\n' + indent + START_TAG

            if tag == 'object':
                for x, y in attrs:
                    if x.lower() == 'type' and y.lower() == 'text/sitemap':
                        self.in_obj = True

            if tag.lower() == 'param' and self.in_obj:
                for x, y in attrs:
                    if x.lower() == 'name':
                        self.param = y.lower()
                    elif x.lower() == 'value':
                        if self.param == 'name' and not len(self.name):
                            # XXX: Remove LF and/or CR signs from name
                            self.name = y.replace('\n', '').replace('\r', '')
                            # XXX: Un-escaping double quotes :-)
                            self.name = self.name.replace('"', '\\"')
                        elif self.param == 'local':
                            # XXX: Change incorrect slashes in url
                            self.local = y.lower().replace('\\', '/').replace('..\\', '')
                        elif self.param == 'imagenumber':
                            self.imagenumber = y
            self.tagstack.append(tag)

    def unknown_endtag(self, tag):
        # if inside ul
        if self.tagstack:
            if tag == 'ul':
                self.parsed += END_TAG
            if tag == 'object' and self.in_obj:
                # "Link Name", "URL", "Icon"
                self.parsed += "\"%s\", \"%s\", \"%s\"" % (self.name, self.local, self.imagenumber)
                # Set to default values
                self.in_obj = False
                self.name = self.local = ""
                self.imagenumber = 1
            if tag != 'li':
                self.tagstack.pop(tag)


class PageLister(sgmllib.SGMLParser):
    """
    Parser of the chm.chm GetTopicsTree() method that retrieves the URL of the HTML
    page embedded in the CHM file.
    """

    def reset(self):
        sgmllib.SGMLParser.reset(self)
        self.pages = []

    def feed(self, data):
        sgmllib.SGMLParser.feed(self, UnicodeDammit(data).unicode_markup)

    def start_param(self, attrs):
        urlparam_flag = False
        for key, value in attrs:
            if key == 'name' and value.lower() == 'local':
                urlparam_flag = True
            if urlparam_flag and key == 'value':
                # Sometime url has incorrect slashes
                value = urllib.parse.unquote(urlparse(value.replace('\\', '/')).geturl())
                value = '/' + re.sub("#.*$", '', value)
                # Avoid duplicates
                if not self.pages.count(value):
                    self.pages.append(value)


class ImageCatcher(sgmllib.SGMLParser):
    """
    Finds image urls in the current html page, so to take them out from the chm file.
    """

    def reset(self):
        sgmllib.SGMLParser.reset(self)
        self.imgurls = []

    def start_img(self, attrs):
        for key, value in attrs:
            if key.lower() == 'src':
                # Avoid duplicates in the list of image URLs.
                if not self.imgurls.count('/' + value):
                    self.imgurls.append('/' + value)

    def start_a(self, attrs):
        for key, value in attrs:
            if key.lower() == 'href':
                url = urlparse(value)
                value = urllib.parse.unquote(url.geturl())
                # Remove unwanted crap
                value = '/' + re.sub("#.*$", '', value)
                # Check file's mimetype
                type = mimetypes.guess_type(value)[0]
                # Avoid duplicates in the list of image URLs.
                if not url.scheme and not self.imgurls.count(value) and \
                        type and re.search('image/.*', type):
                    self.imgurls.append(value)


class TOCCounter(HTMLParser):
    """Count Table of Contents levels"""

    count = 0

    def __init__(self):
        self.tagstack = TagStack()
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.tagstack.append(tag)

    def handle_endtag(self, tag):
        if self.tagstack:
            if tag.lower() == 'object':
                if self.count < self.tagstack.count('param'):
                    self.count = self.tagstack.count('param')
            if tag.lower() != 'li':
                self.tagstack.pop(tag)
