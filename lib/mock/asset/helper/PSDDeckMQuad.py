from psd_tools import PSDImage, Group, Layer
from psd_tools_helper import extract_leaf_layers

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

##----------------------------------------------------------------##
class MQuadDeckPart( DeckPart ):
	def __init__( self, psdLayer ):
		super( MQuadDeckPart, self ).__init__( psdLayer )
		self.meshes = []
		self.globalMeshes = []
		layerName = psdLayer.name
		meta = parseMetaTag( layerName )
		tags = meta[ 'tags' ]
		self.foldMode = 'auto'

		if tags.has_key( 'FOLD' ):
			self.foldMode = 'fold'
			args = tags[ 'FOLD' ]
			self.foldPos  = int( getArray( args, 0, 0 ) )
		
		elif tags.has_key( 'FLOOR' ):
			self.foldMode = 'floor'

		elif tags.has_key( 'WALL' ):
			self.foldMode = 'wall'

	def getImage( self, imgSet ):
		if imgSet == 'normal':
			return self.getNormalMap()
		else:
			return self.getTextureMap()
	
	def getTextureMap( self ):
		if self.img: return self.img
		self.img = self._layer.as_PIL()
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

		localGuideTopFace = h
		if foldMode == 'auto':
			concave = False
			guideTopFace = project.getOption( 'guide-top-face', 0 )
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
		tex = self.getTextureMap()
		normalOption = {
			'guide-top-face' : localGuideTopFace,
			'concave'        : concave,
		}
		self.imgNormal    = makeNormalMap( tex, normalOption )
		self.guideTopFace = localGuideTopFace

		#build mesh
		#format: x,y,z/ u,v /color
		if concave:
			if localGuideTopFace < h: #TOP
				x0 = 0
				y0 = 0
				z0 = 0
				x1 = w
				y1 = h - localGuideTopFace
				z1 = -( y1 - y0 )
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
				x0 = 0
				y0 = h - localGuideTopFace
				z0 = -y0
				x1 = w
				y1 = h
				z1 = -y0
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
				x0 = 0
				y0 = 0
				z0 = 0
				x1 = w
				y1 = h - localGuideTopFace
				z1 = 0
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
				x0 = 0
				y0 = h - localGuideTopFace
				z0 = 0
				x1 = w
				y1 = h
				z1 = -( y1 - y0 )
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


	def getBottom( self ):
		return self.y + self.h

	def getLeft( self ):
		return self.x

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
		for layer in partLayers:
			layerName = layer.name.encode( 'utf-8' )
			if layerName.startswith( '//' ): continue
			if layerName.startswith( '@' ) : continue
			part = MQuadDeckPart( layer )
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

	def onBuild( self, project ):
		meshDatas = []
		bottom = 0
		left   = 0xffffffff #huge number
		for part in self.parts:
			part.onBuild( project )
			bottom = max( bottom, part.getBottom() )
			left   = min( left, part.getLeft() )

		#move mesh
		for part in self.parts:
			part.updateGlobalMeshOffset( left, bottom )

	def postBuild( self, project ):
		for part in self.parts:
			part.buildAtlasUV()

	def getAtlasImgInfos( self ):
		infos = []
		for part in self.parts:
			infos.append( part.getAtlasImgInfo() )
		return infos

##----------------------------------------------------------------##
class MQuadDeckProcesser( DeckProcesser ):
	def onLoadImage( self, psdImage ):
		#root layers
		for layer in psdImage.layers:
			if not isinstance( layer, Group ):
				layerName = layer.name.encode( 'utf-8' )
				if layerName == '@guide-top-face':
					x1,y1,x2,y2 = layer.bbox
					self.project.setOption ( 'global-guide-top-face', y1 )
					return

	def acceptLayer( self, psdLayer, metaInfo ):
		tags = metaInfo[ 'tags' ]
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
registerDeckProcessor( MQuadDeckProcesser )


##----------------------------------------------------------------##
if __name__ == '__main__':
	import PSDDeckPackTest
	