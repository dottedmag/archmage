# -*- coding: utf-8 -*-
#
# Copyright (c) 2003 Eugeny Korekin <aaaz@users.sourceforge.net>
# Copyright (c) 2005-2007 Basil Shubin <bashu@users.sourceforge.net>

import os
import sys
import re
import shutil
import urllib
import errno
import string
import mimetypes

from HTMLParser import HTMLParser, HTMLParseError, piclose
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler 

from archmod import message, error_msg

# import PyCHM bindings
try:
	from chm import chmlib
except ImportError:
	error_msg("ImportError: Cannot import module: python-chm")
	sys.exit(1)


from archmod.htmltotext import htmltotext

# what config file to use - local or a system wide?
user_config = os.path.join(os.path.expanduser('~'), '.arch.conf')
if os.path.exists(user_config):
	config = user_config
else:
	config = '/etc/archmage/arch.conf'

def listdir_r(dir):
	def f(res, dir, files):
		for e in files:
			d = '/'.join(dir.split('/')[1:])
			if d: d += '/'
			res.append(d + e)
	res = []
	os.path.walk(dir, f, res)
	return res


class CHMDir(object):
	""" Class that represent CHM content from directory """

	def __init__(self, name):
		# Name of source directory with CHM content
		self.sourcename = name
		# Import variables from config file into namespace
		execfile(config, self.__dict__)
        
		# Get all entries
		self.entries = self.get_entries(name)
		# Get template files
		self.templates = self.get_templates()
		# Get 'Table of Contents'
		for e in self.entries:
			if e.lower().endswith('.hhc'):
				self.hhc = e
			if e.lower().endswith('.hhk'):
				self.hhk = e
		hhclines = self.get_entry_by_name(self.hhc)
		self.contents, self.deftopic = SitemapFile(hhclines).parse()

	def get_entries(self, name):
		""" Get all entries """
		entries = []
		for fname in listdir_r(name):
			name = '/' + fname
			if os.path.isdir(self.sourcename + name):
				name += '/'
			entries.append(name)
		return entries

	def get_entry_by_name(self, name):
		""" Get CHM entry by it's name """
		# show index page or any other substitute
		if name == '/':
			name = '/index.html'
		if name in self.templates:
			return self.get_template_by_name(name)
		if name.lower() in [ os.path.join('/icons', icon.lower())
							 for icon in os.listdir(self.icons_dir) ]:
			return open(os.path.join(self.icons_dir, os.path.basename(name))).read()
		for e in self.entries:
			if e.lower() == name.lower():
				return CHMEntry(self, e).get()
		else:
			raise NameError, 'There is no %s' % name

	def sub_mytag(self,re):
		"""docstring should be here"""
		try:
			res = eval('self.' + re.group(1))
		except:
			res = eval(re.group(1))
		return res

	def get_templates(self):
		""" Get list of all template files """
		return [ os.path.join('/', file) for file in os.listdir(self.templates_dir)
				 if os.path.isfile(os.path.join(self.templates_dir, file)) ]

	def get_template_by_name(self, name):
		""" Get template file by it's name """
		tpl = open(os.path.join(self.templates_dir, os.path.basename(name))).read()
		return re.sub('\<%(.+?)%\>', self.sub_mytag, tpl)

	def process_templ(self):
		""" Process templates """
		for template in self.templates:
			open(os.path.basename(template), 'w').write(self.get_template_by_name(template))
		if not os.path.exists('icons/'):
			shutil.copytree(os.path.join(self.icons_dir), 'icons/')

	def raw_extract(self):
		""" Extract raw CHM entries into the files """
		# build regex from the list of auxillary files
		aux_re = '|'.join([ re.escape(s) for s in self.auxes ])
		for e in self.entries:
			# if entry is auxillary file, than skip it
			if re.match(aux_re, e):
				continue
			# process entry
			fname = string.lower(e[1:])
			# get dirname for file fname if any
			dname = os.path.dirname(fname)
			# if dname is a directory and it's not exist, than build it
			if dname and not os.path.exists(dname):
				os.makedirs(dname)
			# otherwise write a file from CHM entry
			else:
				# filename enconding conversion
				if self.fs_encoding:
					fname = fname.decode('utf-8').encode(self.fs_encoding)
				# write CHM entry content into the file
				open(fname, 'w').writelines(CHMEntry(self, e).get())

	def extract(self, dir):
		""" Extract CHM file content into FS """
		try:
			# directory to extract CHM file content
			os.mkdir(dir)
			os.chdir(dir)
			# make raw content extraction
			self.raw_extract()
			# process templates
			self.process_templ()
		except OSError, error:
			if error[0] == errno.EEXIST:
				error_msg("OSError: Directory '%s' is already exists!" % dir)
				sys.exit(1)    

	def raw_dump(self, ext=['*']):
		""" Dump CHM entries into the stdout """
		# build regex from the list of auxillary files
		aux_re = '|'.join([ re.escape(s) for s in self.auxes ])
		ext_re = '|'.join([ '.*' + '\.' + s + '$' for s in ext])
		for e in self.entries:
			# if entry is auxillary file, than skip it
			if re.match(aux_re, e) or not re.match(ext_re, e):
				continue
			# to use this function you should have 'lynx' or 'elinks' installed
			htmltotext(input=CHMEntry(self, e).get(), cmd=self.htmltotext)

	def dump_html(self):
		""" Dump HTML content from CHM file into stdout """
		# make html content dumping
		self.raw_dump(['html', 'htm'])


class CHMFile(CHMDir):
	""" CHM file class derived from CHMDir """
    
	def get_entries(self, name):
		""" Overrided CHMDir.get_entries() method """
		entries = []
		# open CHM file and get handler
		self._handler = chmlib.chm_open(name)
		# get CHM file content and process it
		for name in self.get_names(self._handler):
			if (name == '/'):
				continue
			entries.append(name)
		return entries
    
	def get_names(self, chmfile):
		""" Get object's names inside CHM file """
		def _get_name(chmfile, ui, content):
			content.append(ui.path)
			return chmlib.CHM_ENUMERATOR_CONTINUE
		
		chmdir = []
		if (chmlib.chm_enumerate(chmfile, chmlib.CHM_ENUMERATE_ALL, _get_name, chmdir)) == 0:
			error_msg('UnknownError: CHMLIB or PyCHM issue')
			sys.exit(1)
		return chmdir

	def __del__(self):
		""" Closes CHM file handler on class destroing """
		chmlib.chm_close(self._handler)


class CHMEntry(object):
	""" Class for CHM file entry """

	def __init__(self, parent, name):
		# parent CHM file
		self.parent = parent
		# object inside CHM file
		self.name = name

	def read(self):
		""" Read CHM entry content """
		# Check where parent instance is CHMFile or CHMDir
		if isinstance(self.parent, CHMFile):
			result, ui = chmlib.chm_resolve_object(self.parent._handler, self.name)
			if (result != chmlib.CHM_RESOLVE_SUCCESS):
				return None

			size, content = chmlib.chm_retrieve_object(self.parent._handler,
													   ui, 0L, ui.length)
			if (size == 0):
				return None
			return content
		else:
			return open(self.parent.sourcename + self.name).read()

	def lower_links(self, text):
		""" Links to lower case """
		return re.sub('(?i)(href|src)\s*=\s*([^\s|>]+)', lambda m:m.group(0).lower(), text)

	def add_restoreframing_js(self, name, text):
		name = re.sub('/+', '/', name)
		depth = name.count('/')

		js = """<body><script language="javascript">
		if ((window.name != "content") && (navigator.userAgent.indexOf("Opera") <= -1) )
		document.write("<center><a href='%sindex.html?page=%s'>show framing</a></center>")
		</script>""" % ( '../'*depth, name )
		
		return re.sub('(?i)<\s*body\s*>', js, text)

	def get(self):
		""" Get CHM entry content"""
		# read entry content
		data = self.read()
		# If entry is a html page?
		if re.search('(?i)\.html?$', self.name):
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


class SitemapFile(object):
	""" Sitemap file class """
    
	def __init__(self, lines):
		self.lines = lines
        
	def parse(self):
		p = SitemapParser()
		p.feed(self.lines)
		return (p.parsed + '\n]', p.deftopic)


class TagStack(list):
	""" from book of David Mertz 'Text Processing in Python' """
    
	def append(self, tag):
		# Remove every paragraph-level tag if this is one
		if tag.lower() in ('p', 'blockquote'):
			self = TagStack([ t for t in super
							  if t not in ('p', 'blockquote') ])
		super(TagStack, self).append(tag)

	def pop(self, tag):
		# 'Pop' by tag from nearest pos, not only last item
		self.reverse()
		try:
			pos = self.index(tag)
		except ValueError:
			raise HTMLParser.HTMLParseError, 'Tag not on stack'
		self[:] = self[pos + 1:]
		self.reverse()
        

class SitemapParser(HTMLParser):
	""" Class for parsing files in SiteMap format, such as .hhc """

	def __init__(self):
		self.tagstack = TagStack()
		self.params = {}
		self.parsed = ''
		self.deftopic = ''
		HTMLParser.__init__(self)
        
	def handle_starttag(self, tag, attrs):
		# first ul, start processing from here
		if tag == 'ul' and not self.tagstack:
			self.tagstack.append(tag)
			self.parsed += '\n['
		# if inside ul
		elif self.tagstack:
			if tag == 'li':
				if self.tagstack[-1] != 'ul':
					self.parsed += ']'
					self.tagstack.pop('li')
				indent = ' ' * len(self.tagstack)
				if self.parsed != '\n[':
					self.parsed += ','
				self.parsed += '\n' + indent + '['
			if tag == 'param':
				self.params[str(dict(attrs)['name']).lower()] = dict(attrs)['value']
			self.tagstack.append(tag)

	def handle_endtag(self, tag):
		# if inside ul
		if self.tagstack:
			if tag == 'ul':
				self.parsed += ']'
			if tag == 'object':
				if not self.params.has_key('imagenumber'):
					self.params['imagenumber'] = 1
				if not self.params.has_key('local'):
					self.params['local'] = ''
				if not self.params.has_key('name'):
					self.params['name'] = ''
				# use first page as deftopic
				if not self.deftopic:
					self.deftopic = self.params['local'].lower()
 				# otherwise if there index.htm inside CHM file use it instead
 				#if 'index.htm' in self.params['Local'].lower():
 				#	self.deftopic = self.params['Local'].lower()

				self.params['name'] = self.params['name'].replace('\r\n', '\\n').replace('\n', '\\n')
				self.params['local'] = self.params['local'].replace('..\\', '')

				if '"' in self.params['local']:
					lstr = "'%s'"
					self.params['local'] = self.params['local'].replace("'", '\\\'')
				else:
					lstr = '"%s"'
					self.params['local'] = self.params['local'].replace('"', "\\\"")

				if '"' in self.params['name']:
					nstr = "'%s'"
					self.params['name'] = self.params['name'].replace("'", '\\\'')
				else:
					nstr = '"%s"'
					self.params['name'] = self.params['name'].replace('"', "\\\"")

				fstr = nstr + ',' + lstr + ',' + '"%s"'
				self.parsed += fstr % (
					self.params['name'],
					self.params['local'].lower(),
					self.params['imagenumber'])
				self.params = {}
			if tag != 'li':
				self.tagstack.pop(tag)

	def parse_starttag(self, i):
		try:
			return HTMLParser.parse_starttag(self, i)
		except HTMLParseError:
			try:
				return piclose.search(self.rawdata, i).end()
			except AttributeError:
				return -1

	def parse_endtag(self, i):
		try:
			return HTMLParser.parse_endtag(self, i)
		except HTMLParseError:
			try:
				return piclose.search(self.rawdata, i).end()
			except:
				return -1


class CHMServer(HTTPServer):
	""" HTTP Server that handle Compressed HTML """

	def __init__(self, CHM, name='', port=8000):
		self.address = (name, port)
		self.httpd = HTTPServer(self.address, CHMRequestHandler)
		self.httpd.CHM = CHM
		self.address = (name, port)

	def run(self):
		self.httpd.serve_forever()


class CHMRequestHandler(BaseHTTPRequestHandler):
	""" This class handle HTTP request for CHMServer """

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
			self.wfile.write(self.server.CHM.get_entry_by_name(pagename))
		except NameError, msg:
			error_msg("NameError: %s" % msg)
