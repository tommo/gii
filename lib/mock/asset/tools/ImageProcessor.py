#---------------------------------------------------------------##
import ctypes
import os
# os.environ['MAGICK_HOME'] = '/opt/local'
os.environ['MAGICK_HOME'] = '/Users/tommo/prj/gii/support/ImageMagick'

##----------------------------------------------------------------##
from wand.image import Image, CHANNELS
from wand.api   import library
from wand.display import display

##----------------------------------------------------------------##
def GaussianBlur( img, radius ):
	k = max( 1, radius/3 )
	w, h = img.width, img.height
	img.resize( int(w/k), int(h/k) )
	library.MagickGaussianBlurImageChannel( img.wand, CHANNELS['all_channels'], radius, radius/3 )
	img.resize( w, h )
