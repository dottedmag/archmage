# -*- coding: utf-8 -*-

"""Class of all HTML tags"""

class HTMLTags(object):

	tags = [
		'ADDRESS',
		'APPLET',
		'AREA',
		'A',
		'BASE',
		'BASEFONT',
		'BIG',
		'BLOCKQUOTE',
		'BODY',
		'BR',
		'B',
		'CAPTION',
		'CENTER',
		'CITE',
		'CODE',
		'DD',
		'DFN',
		'DIR',
		'DIV',
		'DL',
		'DT',
		'EM',
		'FONT',
		'FORM',
		'H1',
		'H2',
		'H3',
		'H4',
		'H5',
		'H6',
		'HEAD',
		'HR',
		'HTML',
		'IMG',
		'INPUT',
		'ISINDEX',
		'I',
		'KBD',
		'LINK',
		'LI',
		'MAP',
		'MENU',
		'META',
		'OL',
		'OPTION',
		'PARAM',
		'PRE',
		'P',
		'SAMP',
		'SCRIPT',
		'SELECT',
		'SMALL',
		'STRIKE',
		'STRONG',
		'STYLE',
		'SUB',
		'SUP',
		'TABLE',
		'TD',
		'TEXTAREA',
		'TH',
		'TITLE',
		'TR',
		'TT',
		'UL',
		'U',
		'VAR'
	]
	
	def __getattr__(self, key):
		try:
			index = self.tags.index(key.upper())
		except:
			index = None
		if index:
			if key.islower():
				return self.tags[index].lower()
			else:
				return self.tags[index]
		raise AttributeError(key)