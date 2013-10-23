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
	img.resize( int(w/k), int(h/k) )
	library.MagickGaussianBlurImageChannel( img.wand, CHANNELS['all_channels'], radius, radius/3 )
	img.resize( w, h )

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


