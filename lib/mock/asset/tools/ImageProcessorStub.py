#---------------------------------------------------------------##
import ctypes
import os
import sys
import sys,imp

os.environ['MAGICK_HOME'] = '/opt/local'

##----------------------------------------------------------------##
from wand.image import Image, CHANNELS
from wand.api   import library
from wand.display import display

##----------------------------------------------------------------##
library.MagickGaussianBlurImageChannel.argtypes = [
	ctypes.c_void_p,
	ctypes.c_int,
	ctypes.c_double,
	ctypes.c_double
	]

def GaussianBlur( img, radius ):
	k = max( 1, radius/3 )
	w, h = img.width, img.height
	w1,h1 = int(w/k), int(h/k)
	img.resize( w1, h1 )
	tmpImg = Image( width = w1+radius*2, height = h1+radius*2 )
	tmpImg.composite( img, radius, radius )
	library.MagickGaussianBlurImageChannel( tmpImg.wand, CHANNELS['all_channels'], radius, radius/3 )
	tmpImg.resize( w, h )
	tmpImg.format = img.format
	return tmpImg

##----------------------------------------------------------------##
procPath  = sys.argv[1]
imgPath   = sys.argv[2]

procModule = imp.new_module( procPath.replace( '.', '_' ) )
f = file( procPath, 'r' )
code = f.read()
f.close()

exec code
img = Image( filename = imgPath )
output = onProcess( img )
if output:
	output.save( filename = imgPath )
	sys.exit( 0 )
else:
	sys.exit( 1 )


