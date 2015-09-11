from psd_tools import PSDImage, Group, Layer
from psd_tools_helper import extract_leaf_layers

from PSDDeckPackProject import *
from NormalMapHelper import makeNormalMap
from MetaTag import parseMetaTag

##----------------------------------------------------------------##
class TilePart( DeckPart ):
	def __init__( self, psdLayer ):
		super( TilePart, self ).__init__( psdLayer )
		self.imgNormal = None
		self.alt = 0
		self.deckOffset = ( 0,0,0 )
		self.meshes = []

	def getImage( self, imageSet ):
		if imageSet == 'normal':
			return self.imgNormal
		else:
			if self.img: return self.img
			self.img = self._layer.as_PIL()
			return self.img

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
		( dx0, dy0, dx1,dy1 ) = self.getDeckRect()
		# w = dx1 - dx0
		# h = dy1 - dy0
		w = self.w
		h = self.h
		
		ox, oy, oz = self.getDeckOffset()
		localGuideTopFace = self.h - ( self.alt - oy )
		oy = oy + oz
		oz = - oz
		# print self.fullName, w, h, '|', ox, oy, oz, '|', localGuideTopFace
		#build mesh
		#format: x,y,z/ u,v /color
		if localGuideTopFace < h:
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
			quadFront = {
				'verts' : [
					[ x0 + ox, y0 +oy, z0 + oz ], 
					[ x1 + ox, y0 +oy, z0 + oz ], 
					[ x1 + ox, y1 +oy, z1 + oz ], 
					[ x0 + ox, y1 +oy, z1 + oz ]
				],
				'uv' : [
					[ u0,v0 ],
					[ u1,v0 ],
					[ u1,v1 ],
					[ u0,v1 ],
				]
			}
			self.meshes.append( quadFront )

		if localGuideTopFace > 0:
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
					[ x0 + ox, y0 + oy, z0 + oz ], 
					[ x1 + ox, y0 + oy, z0 + oz ], 
					[ x1 + ox, y1 + oy, z1 + oz ], 
					[ x0 + ox, y1 + oy, z1 + oz ]
				],
				'uv' : [
					[ u0,v0 ],
					[ u1,v0 ],
					[ u1,v1 ],
					[ u0,v1 ],
				]
			}
			self.meshes.append( quadTop )
		normalOption = {
			'guide-top-face' : localGuideTopFace
		}
		self.imgNormal = makeNormalMap( self.getTextureMap(), normalOption )

	def postBuild( self, project ):
		self.buildAtlasUV()

	def buildAtlasUV( self ):
		node = self.getAtlasNode()
		if not node:
			print( 'no atlas node for deck', self.name )
		uvrect = node.getUVRect()
		u0, v0, u1 ,v1 = uvrect
		du = u1 - u0
		dv = v1 - v0
		for mesh in self.meshes:
			for uv in mesh['uv']:
				uv[0] = uv[0] * du + u0
				uv[1] = uv[1] * dv + v0

	def getMeshes( self ):
		return self.meshes

##----------------------------------------------------------------##
class TileGroup(object):
	def __init__( self ):
		self.tiles = []
		self.name  = None
		self.rawName = None
		self.tileType   = 'T'
		self.tileWidth  = 0
		self.tileHeight = 0
		self.tileAlt    = 0
		self.tileset = None

	def addTile( self, tile ):
		self.tiles.append( tile )

	def getDim( self ):
		return self.tileset.tileWidth, self.tileset.tileHeight, self.tileAlt

	def onBuild( self, project ):
		#pass name
		mo = re.search( '([\w_-]+)\s*:\s*(\w*)\(\s*(\d+)\s*\)', self.rawName )
		if mo:
			self.name = mo.group( 1 )
			self.tileType = mo.group( 2 ) or 'C'
			self.tileAlt  = int( mo.group( 3 ) )
		else:
			raise Exception( 'invalid tileset name format: %s' % self.rawName )
		self.fullname = self.tileset.name + ':' + self.name
		if self.tileType == 'C':
			self.buildCommonTiles( project )
		elif self.tileType == 'T':
			self.buildTerrainTiles( project )

	def postBuild( self, project ):
		for tile in self.tiles:
			tile.postBuild( project )

	def buildCommonTiles( self, project ):
		tw, td, alt = self.getDim()
		for tile in self.tiles:
			k = tile.name
			w, h = tile.w, tile.h
			ox, oy = 0, alt
			tile.itemName = '%s.%s' % ( self.name, k )
			tile.fullName = '%s.%s' % ( self.fullname, k )
			tile.deckRect = ( ox, oy, ox + w, oy + h )
			tile.alt = alt
			tile.deckOffset = ( 0,alt,0 )
			tile.onBuild( project )

	def buildTerrainTiles( self, project ):
		tw, th, alt = self.getDim()
		for tile in self.tiles:
			tile.alt = alt
			k = tile.name
			w, h = tile.w, tile.h
			ox, oy = 0, 0
			oz = 0
			tile.itemName = '%s.%s' % ( self.name, k )
			tile.fullName = '%s.%s' % ( self.fullname, k )
			if k == 'n':
				ox = 0
				oy = alt
			elif k == 's':
				ox = 0
				oy = 0
				oz = alt + th - h
			elif k == 'w':
				ox = tw - w
				oy = alt
			elif k == 'e':
				ox = 0
				oy = alt
			elif k == 'ne':
				ox = 0
				oy = alt
			elif k == 'se':
				ox = 0
				oy = 0
				oz = alt + th - h
			elif k == 'nw':
				ox = tw - w
				oy = alt
			elif k == 'sw':
				ox = tw - w
				oy = 0
				oz = alt + th - h
			elif k == '-ne':
				ox = 0
				oy = 0
				oz = alt + th - h
			elif k == '-se':
				ox = 0
				oy = alt
			elif k == '-nw':
				ox = 0
				oy = 0
				oz = alt + th - h
			elif k == '-sw':
				ox = 0
				oy = alt
			elif k == 'we':
				ox = 0
				oy = 0
				oz = alt + th - h
			elif k == 'ew':
				ox = 0
				oy = 0
				oz = alt + th - h
			elif k == 'c':
				ox = 0
				oy = alt
			tile.deckRect   = ( ox, oy, ox+w, oy+oz+h )
			tile.deckOffset = ( ox, oy, oz )
			tile.onBuild( project )
	
	def __repr__( self ):
		return '%s: %s( %d, %d, %d )' % ( self.name, self.tileType, self.tileWidth, self.tileDepth, self.tileHeight )

	def getData( self ):
		data = {}
		tileDatas = []
		for t in self.tiles:
			node = t.getAtlasNode()
			assert node
			tileData = {
				'name'       : t.itemName,
				'basename'   : t.name,
				'fullname'   : t.fullName,
				'atlas'      : str( node.root.id ),
				'rect'       : node.getRect(),
				'deck_rect'  : t.getDeckRect(),
				'deck_offset': t.getDeckOffset(),
				'raw_rect'   : t.getRawRect(),
				'raw_index'  : t.getRawIndex(),
				'meshes'     : t.getMeshes()
			}
			tileDatas.append( tileData )
		data[ 'name'     ] = self.name
		data[ 'raw_name' ] = self.rawName
		data[ 'type'     ] = self.tileType
		data[ 'alt'      ] = self.tileAlt
		data[ 'tiles'    ] = tileDatas
		return data

##----------------------------------------------------------------##
class MTilesetDeckItem( DeckItem ):
	def __init__( self, name, psdLayer ):
		self.groups      = []
		self.wallTiles   = {}
		self.groundTiles = {}
		self.tiles       = []
		self.rawName     = psdLayer.name
		self.name        = name

		self.tileWidth  = 0
		self.tileDepth  = 0
		self.tileHeight = 0

		for subLayer in psdLayer.layers:
			if isinstance( subLayer, Group ):
				self.collectGroup( subLayer )

	def collectGroup( self, group ):
		tileGroup = TileGroup()
		tileGroup.rawName = group.name.encode( 'utf-8' )
		tileGroup.name    = tileGroup.rawName
		def _collectLayer( l, parentName = None ):
			for layer in l.layers:
				layerName = layer.name.encode( 'utf-8' )
				if layerName.startswith( '//' ): continue
				if parentName:
					fullName = parentName + '/' + layerName
				else:
					fullName = layerName
				
				if isinstance( layer, Group ):
					_collectLayer( layer, fullName )
				else:
					tile = TilePart( layer )
					tile.rawName = layerName
					tile.name    = fullName
					tileGroup.addTile( tile )
		_collectLayer( group )
		self.groups.append( tileGroup )
		tileGroup.tileset = self

	def onBuild( self, project ):
		#parse Name
		mo = re.search( '([\w_-]+)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', self.rawName )
		if mo:
			# self.name = mo.group( 1 )
			self.tileWidth  = int( mo.group( 2 ) )
			self.tileHeight = int( mo.group( 3 ) )
		else:
			raise Exception( 'tile size not specified: %s' % self.rawName )

		for group in self.groups:
			group.onBuild( project )

	def postBuild( self, projectContext = None ):
		for group in self.groups:
			group.postBuild( projectContext )

	def __repr__( self ):
		return '%s: ( %d, %d )' % ( self.name, self.tileWidth, self.tileHeight )

	def getAtlasImgInfos( self ):
		infos = []
		for group in self.groups:
			for tile in group.tiles:
				( w, h ) = tile.getSize()
				img = DeckPartImg ( '', w, h, (0, 0, w, h) )	
				img.src = tile
				tile.imgInfo = img
				infos.append( img )
		return infos

	def getData( self ):
		data = {}
		groupsData = []
		for g in self.groups:
			groupData = g.getData()
			groupsData.append( groupData )
		data[ 'name'     ] = self.name
		data[ 'raw_name' ] = self.rawName
		data[ 'size'     ] = ( self.tileWidth, self.tileHeight )
		data[ 'groups'   ] = groupsData
		data[ 'type'     ] = 'deck2d.mtileset'
		return data


##----------------------------------------------------------------##
class MTilesetDeckProcesser( DeckProcesser ):
	def onLoadImage( self, psdImage ):
		pass

	def acceptLayer( self, psdLayer, metaInfo ):
		if not isinstance( psdLayer, Group ): return False
		tags = metaInfo[ 'tags' ]
		return tags.has_key( 'TILESET' ) or tags.has_key( 'TS' )

	def processLayer( self, psdLayer, metaInfo ):
		name = metaInfo[ 'name' ]
		tileset = MTilesetDeckItem( name, psdLayer )
		self.project.addDeckItem( tileset )
		return True


##----------------------------------------------------------------##
registerDeckProcessor( MTilesetDeckProcesser )

##----------------------------------------------------------------##


if __name__ == '__main__':
	import PSDDeckPackTest
