__all__ = ['CHM', 'mod_chm', 'htmltotext']
__version__ = '0.1.9.1'

import sys

def message(code=0, msg=''):
	outfp = sys.stdout
	if code == 1:
		outfp = sys.stderr
	if msg:
		print >> outfp, msg

def error_msg(msg=''):
	message(1, msg)
	sys.exit(1)
