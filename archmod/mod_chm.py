# -*- coding: utf-8 -*-

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
