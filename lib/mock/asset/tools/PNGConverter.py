#!/usr/bin/python
import argparse

from PIL import Image
import PIL.PsdImagePlugin

import sys
import sys
import os.path

##----------------------------------------------------------------##
def buildTexStrip( path ):
	files = os.listdir( path )
	images = []
	w0 = 0 #dim for horizontal layout
	h0 = 0 
	w1 = 0 #dim for vertical layout
	h1 = 0
	alpha = False
	for i, f in enumerate( sorted( files ) ):
		name, ext = os.path.splitext( f )
		if ext.lower() in [ '.png', '.psd', '.jpg', '.bmp', '.jpeg' ]:
			img = loadOneImage( path + '/' + f )
			if img:
				if img.mode == 'RGBA': alpha = True
				images.append( img )
				iw,ih = img.size
				w0 += iw
				h0 = max( h0, ih )
				h1 += ih
				w1 = max( w1, iw )
			else:
				print 'failed open file %s' % f
	layout = ( w0*w0 + h0*h0 ) > ( w1*w1 + h1*h1 ) and 'v' or 'h'
	if layout == 'h':
		outputImg = Image.new( alpha and 'RGBA' or 'RGB' , ( w0, h0 ), (0,0,0,0) )
		x,y = 0,0
		for img in images:
			if img.mode != outputImg.mode:
				img.convert( outputImg.mode )
			w,h = img.size
			outputImg.paste( img, ( x, y, x+w, y+h ) )
			x += w
		return outputImg

	else:
		outputImg = Image.new( alpha and 'RGBA' or 'RGB' , ( w1, h1 ), (0,0,0,0) )
		x,y = 0,0		
		for img in images:
			if img.mode != outputImg.mode:
				img.convert( outputImg.mode )
			w,h = img.size
			outputImg.paste( img, ( x, y, x+w, y+h ) )
			y += h
		return outputImg

def loadOneImage( path, **option ):
	img = None
	name, ext = os.path.splitext( path )
	if ext.lower() == '.psd':
		from psd_tools import PSDImage
		pimage = PSDImage.load( path )
		if pimage: img = pimage.as_PIL()
	else:
		img = Image.open( path )
	return img


##----------------------------------------------------------------##
inputPath  = sys.argv[1]
outputPath = sys.argv[2]

##----------------------------------------------------------------##
# print 'converting image:', inputPath

img = None

##----------------------------------------------------------------##
name, ext = os.path.splitext( inputPath )
##----------------------------------------------------------------##
if os.path.isfile( inputPath ):
	img = loadOneImage( inputPath )
elif os.path.isdir( inputPath ):
	if ext.lower() == '.texstrip':
		img = buildTexStrip( inputPath )

if not img:
	print( 'cannot open texture file' )
	sys.exit(2)

if not img.mode in [ 'RGB', 'RGBA' ]:
	img = img.convert("RGB")

##----------------------------------------------------------------##
# pixdata = img.load()
# # Clean the background noise, if color != white, then set to black.
# # change with your color
# for y in xrange(img.size[1]):
#     for x in xrange(img.size[0]):
#         if pixdata[x, y] == (255, 0, 255, 255):
#             pixdata[x, y] = (255, 0, 255, 0)


format = 'PNG'
if len(sys.argv) >= 4:
	format = sys.argv[3].upper()
try:
	img.save( outputPath, format )
except Exception, e:
	print e 
	print 'failed saving file'
	sys.exit( 1 )

sys.exit( 0 )
