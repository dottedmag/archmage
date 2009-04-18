# -*- coding: utf-8 -*-

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
			self.wfile.write(self.server.CHM.get_entry_by_name(pagename))
		except NameError, msg:
			archmod.message(archmod.ERROR, 'NameError: %s' % msg)
