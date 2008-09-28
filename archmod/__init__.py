__all__ = ['CHM', 'mod_chm', 'chmtotext']
__version__ = '0.2'

import sys

def message(code=0, msg=''):
	outfp = sys.stdout
	if code == 1:
		outfp = sys.stderr
	if msg:
		print >> outfp, msg

def info_msg(msg=''):
	message(0, msg)

def error_msg(msg=''):
	message(1, msg)
