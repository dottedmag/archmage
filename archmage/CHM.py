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

import os
import sys
import re
import shutil
import errno
import string
import tempfile
from enum import Enum, auto

import archmage

from archmage.CHMParser import SitemapFile, PageLister, ImageCatcher, TOCCounter#, HeadersCounter

# import PyCHM bindings
try:
    from chm import chmlib
except ImportError as msg:
    sys.exit('ImportError: %s\nPlease check README file for system requirements.' % msg)

# External file converters
from archmage.chmtotext import chmtotext
from archmage.htmldoc import htmldoc

class Action(Enum):
    EXTRACT = auto()
    DUMPHTML = auto()
    CHM2TXT = auto()
    CHM2HTML = auto()
    CHM2PDF = auto()

PARENT_RE = re.compile(r'(^|/|\\)\.\.(/|\\|$)')

class CHMFile:
    """Class that represent CHM content from directory"""

    def __init__(self, name):
        self.cache = {}
        # Name of source directory with CHM content
        self.sourcename = name
        self._chm = chmlib.chm_open(name)
        # Import variables from config file into namespace
        exec(compile(open(archmage.config, "rb").read(), archmage.config, 'exec'), self.__dict__)

        # build regexp from the list of auxiliary files
        self.aux_re = '|'.join([ re.escape(s) for s in self.auxes ])

        # Get and parse 'Table of Contents'
        try:
            self.topicstree = self.topics()
        except AttributeError:
            self.topicstree = None
        self.contents = SitemapFile(self.topicstree).parse()

    def close(self):
        chmlib.chm_close(self._chm)

    def entries(self):
        if 'entries' not in self.cache:
            self.cache['entries'] = self._entries()
        return self.cache['entries']

    def _entries(self):
        def get_name(chmfile, ui, out):
            path = ui.path.decode('utf-8')
            if path != '/':
                out.append(path)
            return chmlib.CHM_ENUMERATOR_CONTINUE

        out = []
        if chmlib.chm_enumerate(self._chm, chmlib.CHM_ENUMERATE_ALL, get_name, out) == 0:
            sys.exit('UnknownError: CHMLIB or PyCHM bug?')
        return out

    # retrieves the list of HTML files contained into the CHM file, **in order**
    # (that's the important bit).
    # (actually performed by the PageLister class)
    def html_files(self):
        if 'html_files' not in self.cache:
            self.cache['html_files'] = self._html_files()
        return self.cache['html_files']

    def _html_files(self):
        lister = PageLister()
        lister.feed(self.topicstree)
        return lister.pages

    # retrieves the list of images urls contained into the CHM file.
    # (actually performed by the ImageCatcher class)
    def image_urls(self):
        if 'image_urls' not in self.cache:
            self.cache['image_urls'] = self._image_urls()
        return self.cache['image_urls']

    def _image_urls(self):
        out = []
        image_catcher = ImageCatcher()
        for file in self.html_files():
            image_catcher.feed(CHMEntry(self, file).correct())
            for image_url in image_catcher.imgurls:
                if not out.count(image_url):
                    out.append(image_url)
        return out

    # retrieves a dictionary of actual file entries and corresponding urls into the CHM file
    def image_files(self):
        if 'image_files' not in self.cache:
            self.cache['image_files'] = self._image_files()
        return self.cache['image_files']

    def _image_files(self):
        out = {}
        for image_url in self.image_urls():
            for entry in self.entries():
                if re.search(image_url, entry.lower()) and entry.lower() not in out:
                    out.update({entry : image_url})
        return out

    # Get topics file
    def topics(self):
        if 'topics' not in self.cache:
            self.cache['topics'] = self._topics()
        return self.cache['topics']

    def _topics(self):
        for e in self.entries():
            if e.lower().endswith('.hhc'):
                return CHMEntry(self, e, frontpage=self.frontpage()).get()

    # use first page as deftopic. Note: without heading slash
    def deftopic(self):
        if 'deftopic' not in self.cache:
            self.cache['deftopic'] = self._deftopic()
        return self.cache['deftopic']

    def _deftopic(self):
        if self.html_files()[0].startswith('/'):
            return self.html_files()[0].replace('/', '', 1).lower()
        return self.html_files()[0].lower()

    # Get frontpage name
    def frontpage(self):
        if 'frontpage' not in self.cache:
            self.cache['frontpage'] = self._frontpage()
        return self.cache['frontpage']

    def _frontpage(self):
        frontpage = os.path.join('/', 'index.html')
        index = 2 # index2.html and etc.
        for filename in self.entries():
            if frontpage == filename:
                frontpage = os.path.join('/', ('index%s.html' % index))
                index += 1
        return frontpage

    # Get all templates files
    def templates(self):
        if 'templates' not in self.cache:
            self.cache['templates'] = self._templates()
        return self.cache['templates']

    def _templates(self):
        out = []
        for file in os.listdir(self.templates_dir):
            if os.path.isfile(os.path.join(self.templates_dir, file)):
                if os.path.join('/', file) not in self.entries():
                    out.append(os.path.join('/', file))
        return out

    # Get ToC levels
    def toclevels(self):
        if 'toclevels' not in self.cache:
            self.cache['toclevels'] = self._toclevels()
        return self.cache['toclevels']

    def _toclevels(self):
        counter = TOCCounter()
        counter.feed(self.topicstree)
        if counter.count > self.maxtoclvl:
            return self.maxtoclvl
        else:
            return counter.count

    def get_template(self, name):
        """Get template file by its name"""
        if name == self.frontpage():
            tpl = open(os.path.join(self.templates_dir, 'index.html')).read()
        else:
            tpl = open(os.path.join(self.templates_dir, os.path.basename(name))).read()
        params = {
            'title': self.title,
            'contents': self.contents,
            'deftopic': self.deftopic(),
            'bcolor': self.bcolor,
            'fcolor': self.fcolor,
        }
        return string.Template(tpl).substitute(params)

    def process_templates(self, destdir="."):
        """Process templates"""
        for template in self.templates():
            open(os.path.join(destdir, os.path.basename(template)), 'w').write(self.get_template(template))
        if self.frontpage() not in self.templates():
            open(os.path.join(destdir, os.path.basename(self.frontpage())), 'w').write(self.get_template('index.html'))
        if not os.path.exists(os.path.join(destdir, 'icons/')):
            shutil.copytree(os.path.join(self.icons_dir), os.path.join(destdir, 'icons/'))

    def extract_entry(self, entry, output_file, destdir=".", correct=False):
        # process output entry, remove first '/' in entry name
        fname = output_file.lower().replace('/', '', 1)
        # get directory name for file fname if any
        dname = os.path.dirname(os.path.join(destdir, fname))
        # if dname is a directory and it's not exist, than create it
        if dname and not os.path.exists(dname):
            os.makedirs(dname)
        # otherwise write a file from CHM entry
        if not os.path.isdir(os.path.join(destdir, fname)):
            # write CHM entry content into the file, corrected or as is
            if correct:
                open(os.path.join(destdir, fname), 'wb').write(CHMEntry(self, entry).correct())
            else:
                open(os.path.join(destdir, fname), 'wb').write(CHMEntry(self, entry).get())

    def extract_entries(self, entries=[], destdir=".", correct=False):
        """Extract raw CHM entries into the files"""
        for e in entries:
            # if entry is auxiliary file, than skip it
            if re.match(self.aux_re, e):
                continue
            if PARENT_RE.search(e):
                raise RuntimeError('Giving up on malicious name: %s' % e)
            self.extract_entry(e, output_file=e, destdir=destdir, correct=correct)

    def extract(self, destdir):
        """Extract CHM file content into FS"""
        try:
            # Create destination directory
            os.mkdir(destdir)
            # make raw content extraction
            self.extract_entries(entries=self.entries(), destdir=destdir)
            # process templates
            self.process_templates(destdir=destdir)
        except OSError as error:
            if error.errno == errno.EEXIST:
                sys.exit('%s is already exists' % destdir)

    def dump_html(self, output=sys.stdout):
        """Dump HTML data from CHM file into standard output"""
        for e in self.html_files():
            # if entry is auxiliary file, than skip it
            if re.match(self.aux_re, e):
                continue
            print(CHMEntry(self, e).get(), file=output)

    def chm2text(self, output=sys.stdout):
        """Convert CHM into Single Text file"""
        for e in self.html_files():
            # if entry is auxiliary file, than skip it
            if re.match(self.aux_re, e):
                continue
            # to use this function you should have 'lynx' or 'elinks' installed
            chmtotext(input=CHMEntry(self, e).get(), cmd=self.chmtotext, output=output)

    def htmldoc(self, output, format=Action.CHM2HTML):
        """CHM to other file formats converter using htmldoc"""
        # Extract CHM content into temporary directory
        output = output.replace(' ', '_')
        tempdir = tempfile.mkdtemp(prefix=output.rsplit('.', 1)[0])
        self.extract_entries(entries=self.html_files(), destdir=tempdir, correct=True)
        # List of temporary files
        files = [ os.path.abspath(tempdir + file.lower()) for file in self.html_files() ]
        if format == Action.CHM2HTML:
            options = self.chmtohtml
            # change output from single html file to a directory with html file and images
            if self.image_files():
                dirname = archmage.file2dir(output)
                if os.path.exists(dirname):
                    sys.exit('%s is already exists' % dirname)
                # Extract image files
                os.mkdir(dirname)
                # Extract all images
                for key, value in list(self.image_files().items()):
                    self.extract_entry(entry=key, output_file=value, destdir=dirname)
                # Fix output file name
                output = os.path.join(dirname, output)
        elif format == Action.CHM2PDF:
            options = self.chmtopdf
            if self.image_files():
                # Extract all images
                for key, value in list(self.image_files().items()):
                    self.extract_entry(entry=key, output_file=key.lower(), destdir=tempdir)
        htmldoc(files, self.htmldoc_exec, options, self.toclevels, output)
        # Remove temporary files
        shutil.rmtree(path=tempdir)

class CHMEntry(object):
    """Class for CHM file entry"""

    def __init__(self, parent, name, frontpage='index.html'):
        # parent CHM file
        self.parent = parent
        # object inside CHM file
        self.name = name
        # frontpage name to substitute
        self.frontpage = os.path.basename(frontpage)

    def read(self):
        """Read CHM entry content"""
        result, ui = chmlib.chm_resolve_object(self.parent._chm, self.name.encode('utf-8'))
        if result != chmlib.CHM_RESOLVE_SUCCESS:
            return None

        size, content = chmlib.chm_retrieve_object(self.parent._chm, ui, 0, ui.length)
        if size == 0:
            return None
        return content

    def lower_links(self, text):
        """Links to lower case"""
        return re.sub(b'(?i)(href|src)\s*=\s*([^\s|>]+)', lambda m:m.group(0).lower(), text)

    def add_restoreframing_js(self, name, text):
        name = re.sub('/+', '/', name)
        depth = name.count('/')

        js = b"""<body><script language="javascript">
        if (window.name != "content")
        document.write("<center><a href='%s%s?page=%s'>show framing</a></center>")
        </script>""" % ( b'../' * depth, self.frontpage.encode('utf8'), name.encode('utf8') )

        return re.sub(b'(?i)<\s*body\s*>', js, text)

    def correct(self):
        """Get correct CHM entry content"""
        data = self.read()
        # If entry is a html page?
        if re.search('(?i)\.html?$', self.name) and data is not None:
            # lower-casing links if needed
            if self.parent.filename_case:
                data = self.lower_links(data)

            # Delete unwanted HTML elements.
            data = re.sub('<div .*teamlib\.gif.*\/div>', '', data)
            data = re.sub('<a href.*>\[ Team LiB \]<\/a>', '', data)
            data = re.sub('<table.*larrow\.gif.*rarrow\.gif.*<\/table>', '', data)
            data = re.sub('<a href.*next\.gif[^>]*><\/a>', '' ,data)
            data = re.sub('<a href.*previous\.gif[^>]*><\/a>', '', data)
            data = re.sub('<a href.*prev\.gif[^>]*><\/a>', '', data)
            data = re.sub('"[^"]*previous\.gif"', '""', data)
            data = re.sub('"[^"]*prev\.gif"', '""', data)
            data = re.sub('"[^"]*next\.gif"', '""', data)
        if data is not None:
            return data
        else:
            return ''

    def get(self):
        """Get CHM entry content"""
        # read entry content
        data = self.read()
        # If entry is a html page?
        if re.search('(?i)\.html?$', self.name) and data is not None:
            # lower-casing links if needed
            if self.parent.filename_case:
                data = self.lower_links(data)
            # restore framing if that option is set in config file
            if self.parent.restore_framing:
                data = self.add_restoreframing_js(self.name[1:], data)
        if data is not None:
            return data
        else:
            return ''
