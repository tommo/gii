from psd_tools import PSDImage, Group, Layer
from psd_tools_helper import extract_leaf_layers

from PIL import Image

from PyAffineTransform import AffineTransform

from PSDDeckPackProject import *
from NormalMapHelper import makeNormalMap
from MetaTag import parseMetaTag

def clamp( x, a, b ):
	return max( a, min( b, x ) )

def getArray( l, idx, default = None ):
	if idx < 0: return default
	if idx >= len( l ): return default
	v = l[ idx ]
	if v is None: return default
	return v

def getArrayI( l, idx, default = None ):
	return int( getArray( l, idx, default ) )

def alphaPasted( im, mark, position ):
	if im.mode != 'RGBA':
		im = im.convert('RGBA')
	# create a transparent layer the size of the image and draw the
	# watermark in that layer.
	layer = Image.new('RGBA', im.size, (0,0,0,0))
	layer.paste(mark, position)
	# composite the watermark with the layer
	return Image.composite( layer, im, layer )

##----------------------------------------------------------------##
class MQuadDeckPart( DeckPart ):
	def __init__( self, parentItem, psdLayer ):
		super( MQuadDeckPart, self ).__init__( psdLayer )
		self.parentItem = parentItem
		self.meshes = []
		self.globalMeshes = []
		layerName = psdLayer.name
		meta = parseMetaTag( layerName )
		if meta:
			tags = meta[ 'tags' ]
		else:
			tags = {}

		self.foldMode = 'auto'
		self.altOffset = 0

		if tags.has_key( 'FOLD' ):
			self.foldMode = 'fold'
			args = tags[ 'FOLD' ]
			self.foldPos  = getArrayI( args, 0, 0 )
		
		elif tags.has_key( 'FLOOR' ) or tags.has_key( 'F' ):
			self.foldMode = 'floor'

		elif tags.has_key( 'WALL' ) or tags.has_key( 'W' ):
			self.foldMode = 'wall'

		if tags.has_key( 'OFF' ):
			args = tags[ 'OFF' ]
			self.rectOffset = ( getArrayI( args, 0, 0 ), getArrayI( args, 1, 0 ), getArrayI( args, 2, 0 ) )
		else:
			self.rectOffset = ( 0,0,0 )

	def getImage( self, imgSet ):
		if imgSet == 'normal':
			return self.getNormalMap()
		else:
			return self.getTextureMap()
	
	def getTextureMap( self ):
		if self.img: return self.img
		try:
			self.img = self._layer.as_PIL()
		except Exception, e:
			#FIXME: ignore empty layer?
			print self._layer.name.encode( 'utf-8' )
			print e
			return None
		return self.img

	def getNormalMap( self ):
		if self.imgNormal:
			return self.imgNormal
		else:
			return self.getTextureMap()

	def onBuild( self, project ):
		foldMode = self.foldMode
		concave  = False
		
		( w, h ) = self.getSize()
		( x, y ) = self.getOffset()
		(rectOffX, rectOffY, rectOffZ) = self.rectOffset

		localGuideTopFace = h
		if foldMode == 'auto':
			concave = False
			guideTopFace = project.getOption( 'global-guide-top-face', 0 )
			localGuideTopFace = clamp( guideTopFace - y, 0, h )

		elif foldMode == 'fold':
			foldPos = self.foldPos
			if foldPos < 0: 
				concave = True
				localGuideTopFace = clamp( - foldPos , 0, h )
			else:
				concave = False
				localGuideTopFace = clamp( h - foldPos , 0, h )

		elif foldMode == 'wall':
			concave = False
			localGuideTopFace = 0

		elif foldMode == 'floor':
			concave = False
			localGuideTopFace = h

		img = DeckPartImg ( '', w, h, (0, 0, w, h) )	
		img.node = None
		img.src = self
		self.imgInfo = img

		#build normal
		px0, py0, px1, py1 = self.parentItem.aabb
		offx = self.getLeft() - px0
		offy = self.getTop()  - py0
		tex = self.getTextureMap()
		normalOption = {
			'guide-top-face'      : localGuideTopFace,
			'concave'             : concave,
			'height_guide'        : self.parentItem.heightGuideImage,
			'height_guide_offset' : ( offx, offy ),
			'height_guide_opacity': 1.0
		}
		self.imgNormal    = makeNormalMap( tex, normalOption )
		self.guideTopFace = localGuideTopFace

		#build mesh
		#format: x,y,z/ u,v /color
		if concave:
			if localGuideTopFace < h: #TOP
				x0 = 0 + rectOffX
				y0 = 0 + rectOffY
				z0 = 0 + rectOffZ
				x1 = w + rectOffX
				y1 = h - localGuideTopFace + rectOffY
				z1 = -( y1 - y0 ) + rectOffZ
				u0 = float(x0) / w
				v0 = float(y0) / h
				u1 = float(x1) / w
				v1 = float(y1) / h
				quadWall = {
					'verts' : [
						[ x0,y0,z0 ], 
						[ x1,y0,z0 ], 
						[ x1,y1,z1 ], 
						[ x0,y1,z1 ]
					],
					'uv' : [
						[ u0,v0 ],
						[ u1,v0 ],
						[ u1,v1 ],
						[ u0,v1 ],
					]
				}
				self.meshes.append( quadWall )

			if localGuideTopFace > 0: #WALL
				x0 = 0 + rectOffX
				y0 = h - localGuideTopFace + rectOffY
				z0 = -y0 + rectOffZ
				x1 = w + rectOffX
				y1 = h + rectOffY
				z1 = -y0 + rectOffZ
				u0 = float(x0) / w
				v0 = float(y0) / h
				u1 = float(x1) / w
				v1 = float(y1) / h
				quadTop = {
					'verts' : [
						[ x0,y0,z0 ], 
						[ x1,y0,z0 ], 
						[ x1,y1,z1 ], 
						[ x0,y1,z1 ]
					],
					'uv' : [
						[ u0,v0 ],
						[ u1,v0 ],
						[ u1,v1 ],
						[ u0,v1 ],
					]
				}
				self.meshes.append( quadTop )

		else:
			if localGuideTopFace < h: #WALL
				x0 = 0 + rectOffX
				y0 = 0 + rectOffY
				z0 = 0 + rectOffZ
				x1 = w + rectOffX
				y1 = h - localGuideTopFace + rectOffY
				z1 = 0 + rectOffZ
				u0 = float(x0) / w
				v0 = float(y0) / h
				u1 = float(x1) / w
				v1 = float(y1) / h
				quadWall = {
					'verts' : [
						[ x0,y0,z0 ], 
						[ x1,y0,z0 ], 
						[ x1,y1,z1 ], 
						[ x0,y1,z1 ]
					],
					'uv' : [
						[ u0,v0 ],
						[ u1,v0 ],
						[ u1,v1 ],
						[ u0,v1 ],
					]
				}
				self.meshes.append( quadWall )

			if localGuideTopFace > 0: #TOP
				x0 = 0 + rectOffX
				y0 = h - localGuideTopFace + rectOffY
				z0 = 0 + rectOffZ
				x1 = w + rectOffX
				y1 = h + rectOffY
				z1 = -( y1 - y0 ) + rectOffZ
				u0 = float(x0) / w
				v0 = float(y0) / h
				u1 = float(x1) / w
				v1 = float(y1) / h
				quadTop = {
					'verts' : [
						[ x0,y0,z0 ], 
						[ x1,y0,z0 ], 
						[ x1,y1,z1 ], 
						[ x0,y1,z1 ]
					],
					'uv' : [
						[ u0,v0 ],
						[ u1,v0 ],
						[ u1,v1 ],
						[ u0,v1 ],
					]
				}
				self.meshes.append( quadTop )


	def postBuild( self ):
		self.buildAtlasUV()

	def getBottom( self ):
		return self.y + self.h

	def getLeft( self ):
		return self.x

	def getRight( self ):
		return self.x + self.w

	def getTop( self ):
		return self.y

	def updateGlobalMeshOffset( self, globalLeft, globalBottom ):
		offy = globalBottom - self.getBottom()
		offx = globalLeft   - self.getLeft()
		self.globalMeshes = []
		for mesh in self.meshes:
			gmesh = copy.deepcopy( mesh )
			for vert in gmesh['verts']:
				vert[ 0 ] -= offx
				vert[ 1 ] += offy
			self.globalMeshes.append( gmesh )

	def updateLocalMeshOffset( self, dx, dy, dz ):
		for mesh in self.meshes:
			for vert in gmesh['verts']:
				vert[ 0 ] -= dx
				vert[ 1 ] += dy
				vert[ 2 ] += dz

	def buildAtlasUV( self ):
		node = self.getAtlasNode()
		if not node:
			print( 'no atlas node for deck', self.name )
		uvrect = node.getUVRect()
		u0, v0, u1 ,v1 = uvrect
		du = u1 - u0
		dv = v1 - v0
		for mesh in self.globalMeshes:
			for uv in mesh['uv']:
				uv[0] = uv[0] * du + u0
				uv[1] = uv[1] * dv + v0

	def getGlobalMeshes( self ):
		return self.globalMeshes


##----------------------------------------------------------------##
class MQuadDeckItem(DeckItem):
	def __init__( self, name, partLayers ):
		self.name = name
		self.rawName = name
		self.parts = []
		self.heightGuides = []
		self.heightGuideImage = None
		for layer in partLayers:
			layerName = layer.name.encode( 'utf-8' )
			if layerName.startswith( '//' ): continue
			if layerName.startswith( '@' ) :
				if layerName.startswith( '@hmap' ):
					#normal guide
					self.heightGuides.append( layer )
				continue
			part = MQuadDeckPart( self, layer )
			self.parts.append( part )

	def getData( self ):
		meshes = []
		for part in self.parts:
			meshes += part.getGlobalMeshes()
		return {
			'name'  : self.name,
			'meshes': meshes,
			'type'  : 'deck2d.mquad'
		}

	def buildAABB( self ):
		bottom = 0
		right  = 0
		top    = 0xffffffff #huge number
		left   = 0xffffffff #huge number
		for part in self.parts:
			bottom = max( bottom, part.getBottom() )
			left   = min( left,   part.getLeft()   )
			right  = max( right,  part.getRight()  )
			top    = min( top,    part.getTop()    )
		self.aabb = ( left, top, right, bottom )

	def onBuild( self, project ):
		self.buildAABB()
		left, top, right, bottom = self.aabb		
		self.buildHeightGuide( left, top, right, bottom )
		
		for part in self.parts:
			part.onBuild( project )

		#move mesh
		for part in self.parts:
			part.updateGlobalMeshOffset( left, bottom )


	def buildHeightGuide( self, x0, y0, x1, y1 ):
		if not self.heightGuides: return
		w, h = x1-x0, y1-y0
		self.heightGuideImage = None
		targetImage = Image.new( "RGBA", (w,h), (0,0,0,0) )
		for layer in reversed(self.heightGuides):
			lx0, ly0, lx1, ly1 = layer.bbox
			if lx0 == lx1 and ly0 == ly1: continue
			image = layer.as_PIL()
			px, py = lx0 - x0, ly0 - y0
			tmpLayer = Image.new( "RGBA", (w,h), (0,0,0,0) )
			tmpLayer.paste( image, (px, py) )
			targetImage = Image.blend( targetImage, tmpLayer, layer.opacity/255.0 )

		self.heightGuideImage = targetImage


	def postBuild( self, project ):
		for part in self.parts:
			part.postBuild()

	def getAtlasImgInfos( self ):
		infos = []
		for part in self.parts:
			infos.append( part.getAtlasImgInfo() )
		return infos

##----------------------------------------------------------------##
class MQuadDeckProcessor( DeckProcessor ):
	def onLoadImage( self, psdImage ):
		#root layers
		for layer in psdImage.layers:
			if not isinstance( layer, Group ):
				layerName = layer.name.encode( 'utf-8' )
				if layerName == '@guide-top-face':
					x1,y1,x2,y2 = layer.bbox
					self.project.setOption ( 'global-guide-top-face', y1 )
					return

	def acceptLayer( self, psdLayer, metaInfo, fallback ):
		tags = metaInfo[ 'tags' ]
		if fallback:
			return True
		else:
			return tags.has_key( 'MQ' )

	def processLayer( self, psdLayer, metaInfo ):
		project = self.project
		tags = metaInfo[ 'tags' ]
		partLayers = []
		if isinstance( psdLayer, Group ):
			partLayers = extract_leaf_layers( psdLayer )
		else:
			partLayers = [ psdLayer ]

		deck = MQuadDeckItem( psdLayer.name, partLayers )
		project.addDeckItem( deck )

##----------------------------------------------------------------##
registerDeckProcessor( 'mquad', MQuadDeckProcessor )


##----------------------------------------------------------------##
if __name__ == '__main__':
	import PSDDeckPackTest
	