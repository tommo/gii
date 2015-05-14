from PIL import Image
import math

def calcHeight( r,g,b, a ):
	if a <5: return 0
	h1 = (r * 1.2 + g * 1.2  + b * 0.6)/3/255.0
	# return math.sqrt( h1 )
	return h1 * h1
	# return h1

def calcNormal( pix, x, y, w, h ):
	r,g,b,a = pix[ x, y ]
	if a == 0:
		return 0, 0, 0
	
	h0 = calcHeight( r,g,b,a )
	if h0 < 0.03:
		return 0, 0, 0.5

	h1 = 0
	#left
	fx, fy = 0, 0
	for r in range( 1, 2 ):
		if x > r:
			r1,g1,b1,a1 = pix[ x - r, y ]
			h1 = calcHeight( r1, g1, b1, a1 )
			fx = fx + ( h1 - h0 ) * 1

		if x < w - r:
			r1,g1,b1,a1 = pix[ x + r, y ]
			h1 = calcHeight( r1, g1, b1, a1 )
			fx = fx + ( h1 - h0 ) * -1

		if y > r:
			r1,g1,b1,a1 = pix[ x, y  - r ]
			h1 = calcHeight( r1, g1, b1, a1 )
			fy = fy + ( h1 - h0 ) * -.5
	
	for r in range( 1, 3 ):
		if y < h - r:
			r1,g1,b1,a1 = pix[ x, y + r ]
			h1 = calcHeight( r1, g1, b1, a1 )
			fy = fy + ( h1 - h0 ) * ( 1 - r/3 ) * 0.5

	# if y < h - 2:
	# 	r1,g1,b1,a1 = pix[ x, y + 2 ]
	# 	h1 = calcHeight( r1, g1, b1, a1 )
	# 	fy = fy + ( h1 - h0 ) * 1
	
	return fx, fy + h0 / 2.0, 1

# img = Image.open( 'tile.tileset.png' )
# w,h = img.size
# imgOut = Image.new( 'RGBA', ( w,h ), (0,0,0,0 ) )
# pixIn = img.load()
# pixOut= imgOut.load()
# for y in range( h ):
# 	for x in range( w ):
# 		mx,my,mz = calcNormal( pixIn, x, y, w, h )
# 		l = math.sqrt( mx*mx + my*my + mz*mz )
# 		if l > 0:
# 			nx,ny,nz = mx/l, my/l, mz/l
# 		else:
# 			nx,ny,nz = 0,0,0
# 		pixOut[ x, y ] = ( 
# 			int(nx*255), int(ny*255), int(nz*255), 255 
# 			)
# imgOut.save( 'output.png', 'PNG' )


PI4 = -math.pi/4
PI2 = -math.pi/4
CosPI2 = math.cos( PI2 )
SinPI2 = math.sin( PI2 )
CosPI4 = math.cos( PI4 )
SinPI4 = math.sin( PI4 )
CosPI4H = math.cos( PI4/4 )
SinPI4H = math.sin( PI4/4 )
CosPI4N = math.cos( -PI4 )
SinPI4N = math.sin( -PI4 )

def rotateTopDouble( ny, nz ):
	nny = ny * CosPI2 - nz * SinPI2
	nnz = ny * SinPI2 + nz * CosPI2
	return nny, nnz

def rotateTop( ny, nz ):
	nny = ny * CosPI4 - nz * SinPI4
	nnz = ny * SinPI4 + nz * CosPI4
	return nny, nnz

def rotateTopHalf( ny, nz ):
	nny = ny * CosPI4H - nz * SinPI4H
	nnz = ny * SinPI4H + nz * CosPI4H
	return nny, nnz

def rotateFront( ny, nz ):
	nny = ny * CosPI4N - nz * SinPI4N
	nnz = ny * SinPI4N + nz * CosPI4N
	return nny, nnz

def makeNormalMap( img, option ):
	w,h = img.size
	imgOut = Image.new( 'RGBA', ( w,h ), (0,0,0,0 ) )
	pixIn = img.load()
	pixOut= imgOut.load()
	guideTopFace = option.get( 'guide-top-face', 0 )
	for y in range( h ):
		for x in range( w ):
			mx,my,mz = calcNormal( pixIn, x, y, w, h )
			l = math.sqrt( mx*mx + my*my + mz*mz )
			if l > 0:
				nx,ny,nz = mx/l, my/l, mz/l
			else:
				nx,ny,nz = 0,0,0

			nx = nx/2.0 + 0.5
			ny = ny/2.0 + 0.5
			nz = nz/2.0 + 0.5
			pixOut[ x, y ] = ( 
				int(nx*255), int(ny*255), int(nz*255), 255
				)
	#shape pass
	for y in range( h ):
		for x in range( w ):
			nx,ny,nz, a = pixOut[ x, y ]
			nx= ( nx/255.0 - 0.5 ) * 2.0
			ny= ( ny/255.0 - 0.5 ) * 2.0
			nz= ( nz/255.0 - 0.5 ) * 2.0
			if y < guideTopFace - 1:
				ny, nz = rotateTop( ny, nz )
			elif guideTopFace > 0 and y < guideTopFace:
				ny, nz = rotateTopHalf( ny, nz )
			# else:
			# 	ny, nz = rotateFront( ny, nz )
			nx = nx/2.0 + 0.5
			ny = ny/2.0 + 0.5
			nz = nz/2.0 + 0.5
			pixOut[ x, y ] = ( 
				int(nx*255), int(ny*255), int(nz*255), a 
				)
	
	return imgOut


if __name__ == '__main__':
	import psd2deckpack