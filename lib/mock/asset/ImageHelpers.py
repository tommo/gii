import sys
import os.path
import logging

from gii.core import app
from PIL import Image
import PIL.PsdImagePlugin
import subprocess


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

def getImageSize( path ):
	img = Image.open( path )
	return img.size



##----------------------------------------------------------------##
def convertToPNG( inputPath, outputPath, **options ):
	##----------------------------------------------------------------##
	if not outputPath: outputPath = inputPath
	logging.info( u'converting image: {0} -> {1}'.format( inputPath, outputPath ) ) 

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
		logging.warn( 'cannot open texture file' )
		return False

	if not img.mode in [ 'RGB', 'RGBA' ]:
		img = img.convert("RGB")

	format = 'PNG'
	try:
		img.save( outputPath, format )
	except Exception, e:
		logging.exception( e )
		return False
	return True

##----------------------------------------------------------------##
def convertToWebP( src, dst = None, **option ):
	if app.getPlatformName() == 'osx':
		cwebp = app.getPath( 'support/osx/webp/cwebp' )
	elif app.getPlatformName() == 'win':
		cwebp = app.getPath( 'support/win/webp/cwebp.exe' )

	arglist = [
		cwebp,
		'-quiet'
		# '-hint', 'photo'
	]
	quality = option.get( 'quality', 100 )
	if quality == 'lossless':
		arglist += ['-lossless']
	else:
		arglist += [ '-q', str(quality) ]
	if not dst:
		dst = src
	arglist += [
		src,
		'-o',
		dst
	 ]

	# print 'convert to webp %s -> %s' % ( src, dst )
	# if src == dst: return #SKIP
	return subprocess.call( arglist )


##----------------------------------------------------------------##
#texturetool -e PVRTC --channel-weighting-linear --bits-per-pixel-4 -o ImageL4.pvrtc Image.png
def convertToPVR( src, dst = None, **option ):
	if app.getPlatformName() == 'osx':
		app.getPath( 'support/osx/pvrtc/texturetool' ),
		arglist = [
			'-e', 'PVRTC',
			'-f', 'PVR',
			'--channel-weighting-linear',
		]

		bbp = option.get( 'bbp', 4 )
		if bbp == 4 :
			arglist += ['--bits-per-pixel-4']
		else:
			arglist += ['--bits-per-pixel-2']
		
		if not dst:
			dst = src
		arglist += [
			'-o',
			dst,
			src,
		 ]
		print 'convert to pvr %s -> %s' % ( src, dst )
		return subprocess.call( arglist )
	else:
		logging.error( 'not supported!' )

##----------------------------------------------------------------##
def quantize( src, dst = None, **option ):
	pass


##----------------------------------------------------------------##
def buildThumbnail( inputPath, outputPath, size ):
		##----------------------------------------------------------------##
	if not outputPath: outputPath = inputPath
	logging.info( u'generating thumbnail: {0} -> {1}'.format( inputPath, outputPath ) ) 

	img = None

	##----------------------------------------------------------------##
	name, ext = os.path.splitext( inputPath )
	##----------------------------------------------------------------##
	if os.path.isfile( inputPath ):
		img = loadOneImage( inputPath )
	
	if not img:
		logging.warn( 'cannot open texture file' )
		return False

	if not img.mode in [ 'RGB', 'RGBA' ]:
		img = img.convert("RGB")
	
	img.thumbnail( size )
	format = 'PNG'
	w1,h1 = img.size
	w,h = size
	if h1 != h:
		# img = img.resize( ( w2, h2 ) )
		tmp = Image.new( "RGBA", size, color=(255, 255, 255, 0) )
		x0 = ( w - w1 ) / 2
		y0 = ( h - h1 ) / 2
		tmp.paste( img, ( x0,y0,x0+w1,y0+h1) )
		img = tmp

	try:
		img.save( outputPath, format )
	except Exception, e:
		logging.exception( e )
		return False
	return True
