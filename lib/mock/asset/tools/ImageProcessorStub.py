#---------------------------------------------------------------##
import ctypes
import os
import sys
import sys,imp

from PIL import Image, ImageFilter, ImageEnhance

##----------------------------------------------------------------##
#BUILTIN-functions
##----------------------------------------------------------------##
def GaussianBlur( img, radius ):
	blurFilter = ImageFilter.GaussianBlur( radius )
	#todo: de-premulitple alpha
	preAlpha = img.convert( 'RGBa' )
	preAlpha.mode = 'RGBA' #hacking
	return preAlpha.filter( blurFilter )

def ResizeRelative( img, sx, sy=-1 ):
	w, h = img.size
	if sy<0: sy = sx
	newSize = ( int(w*sx), int(h*sy) )
	return img.resize( newSize, Image.BILINEAR )

##----------------------------------------------------------------##
# STUB
##----------------------------------------------------------------##
procPath  = sys.argv[1]
imgPath   = sys.argv[2]

procModule = imp.new_module( procPath.replace( '.', '_' ) )
f = file( procPath, 'r' )
code = f.read()
f.close()

exec code
img = Image.open( imgPath )
output = onProcess( img )
if output:
	output.save( imgPath, 'PNG' )
	sys.exit( 0 )
else:
	sys.exit( 1 )

