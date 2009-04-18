# -*- coding: utf-8 -*-

from HTMLTags import HTMLTags
from HTMLParser import HTMLParser, HTMLParseError, piclose

import archmod


class SitemapFile(object):
	"""Sitemap file class"""

	def __init__(self, lines):
		self.lines = lines

	def parse(self):
		p = SitemapParser()
		p.feed(self.lines)
		return (p.parsed + archmod.LF + archmod.SQUARE_BRACKETS[1], p.deftopic)


class TagStack(list):
	"""from book of David Mertz 'Text Processing in Python'"""
	
	tags = HTMLTags()

	def append(self, tag):
		# Remove every paragraph-level tag if this is one
		if tag.lower() in (self.tags.p, self.tags.blockquote):
			self = TagStack([ t for t in super
							if t not in (self.tags.p, self.tags.blockquote) ])
		super(TagStack, self).append(tag)

	def pop(self, tag):
		# 'Pop' by tag from nearest position, not only last item
		self.reverse()
		try:
			pos = self.index(tag)
		except ValueError:
			raise HTMLParseError, 'Tag not on stack'
		self[:] = self[pos + 1:]
		self.reverse()


class SitemapParser(HTMLParser):
	"""Class for parsing files in SiteMap format, such as .hhc"""
	
	tags = HTMLTags()

	def __init__(self, maxtoclvl=4):
		self.tagstack = TagStack()
		self.params = {}
		self.parsed = ''
		self.deftopic = ''
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		# first ul, start processing from here
		if tag == self.tags.ul and not self.tagstack:
			self.tagstack.append(tag)
			self.parsed += archmod.LF + archmod.SQUARE_BRACKETS[0]
		# if inside ul
		elif self.tagstack:
			if tag == self.tags.li:
				if self.tagstack[-1] != self.tags.ul:
					self.parsed += archmod.SQUARE_BRACKETS[1]
					self.tagstack.pop(self.tags.li)
				indent = ' ' * len(self.tagstack)
				if self.parsed != archmod.LF + archmod.SQUARE_BRACKETS[0]:
					self.parsed += archmod.COMMASPACE
				self.parsed += archmod.LF + indent + archmod.SQUARE_BRACKETS[0]
			if tag == 'param':
				self.params[str(dict(attrs)['name']).lower()] = dict(attrs)['value']
			self.tagstack.append(tag)

	def handle_endtag(self, tag):
		# if inside ul
		if self.tagstack:
			if tag == self.tags.ul:
				self.parsed += archmod.SQUARE_BRACKETS[1]
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

				# Fixing new line sign
				self.params['name'] = self.params['name'].replace(archmod.CR + archmod.LF, archmod.BACKSLASH + 'n').replace(archmod.LF, archmod.BACKSLASH + 'n')
				self.params['local'] = self.params['local'].replace('..' + archmod.BACKSLASH, '')

				# TODO: Do something with this...
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

				# TODO: Refactore this code...
#				# Create a list of ordered files
#				if len(self.params['local'].strip()) != 0:
#					if self.params['local'].lower() not in self.files:
#						self.files.append("/" + re.sub("#.*$", '', self.params['local'].lower()))
#
#				# Count ToC Levels
#				if self.toclevels < self.tagstack.count('param'):
#					if self.tagstack.count('param') > self.maxtoclvl:
#						self.toclevels = self.maxtoclvl
#					else:
#						self.toclevels = self.tagstack.count('param')

				fstr = nstr + archmod.COMMASPACE + lstr + archmod.COMMASPACE + '"%s"'
				self.parsed += fstr % (
					self.params['name'],
					self.params['local'].lower(),
					self.params['imagenumber'])
				self.params = {}
			if tag != self.tags.li:
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
