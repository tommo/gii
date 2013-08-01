#!/usr/bin/python
import argparse

from PIL import Image
import PIL.PsdImagePlugin

import sys
import sys
import os.path

filepath = sys.argv[1]
# print 'converting image:', filepath
img = None

name, ext = os.path.splitext( filepath )
if ext.lower() == '.psd':
	from psd_tools import PSDImage
	pimage = PSDImage.load( filepath )
	if not pimage: sys.exit( 'failed loading file' )
	img = pimage.as_PIL()
else:
	img = Image.open(filepath)

img = img.convert("RGBA")

# pixdata = img.load()
# # Clean the background noise, if color != white, then set to black.
# # change with your color
# for y in xrange(img.size[1]):
#     for x in xrange(img.size[0]):
#         if pixdata[x, y] == (255, 0, 255, 255):
#             pixdata[x, y] = (255, 0, 255, 0)


output = sys.argv[2]
format = 'PNG'
if len(sys.argv) >= 4:
	format = sys.argv[3].upper()
try:
	img.save( output, format )
except Exception, e:
	print e 
	sys.exit( 'failed saving file' )
