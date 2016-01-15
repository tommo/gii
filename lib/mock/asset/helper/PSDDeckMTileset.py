from psd_tools import PSDImage, Group, Layer
from psd_tools_helper import extract_leaf_layers

from PSDDeckPackProject import *
from PSDDeckMQuad import MQuadDeckPart, MQuadDeckItem
from NormalMapHelper import makeNormalMap
from MetaTag import parseMetaTag

##----------------------------------------------------------------##
class TileItemPart( MQuadDeckPart ):
	def __init__( self, parentItem, psdLayer ):
		super( TileItemPart, self ).__init__( parentItem, psdLayer )
		self.imgNormal = None
		self.alt = 0
		self.deckOffset = ( 0,0,0 )
		self.meshes = []
		if self.foldMode == 'auto':
			self.foldMode = 'floor'

	def onBuild( self, project ):
		return super( TileItemPart, self ).onBuild( project )

class TileItem( MQuadDeckItem ):
	def createPart( self, layer ):
		return TileItemPart( self, layer )

	def onBuild( self, project ):
		super( TileItem, self ).onBuild( project )
		group = self.parentGroup
		self.itemName = '%s.%s' % ( group.name, self.name )
		self.fullName = '%s.%s' % ( group.fullname, self.name )
		if group.tileType == 'C':
			self.onBuildForCommon()
		elif group.tileType == 'T':
			self.onBuildForTerrain()

	def onBuildForCommon( self ):
		group = self.parentGroup
		tw, td, alt = group.getDim()
		self.alt = alt
		self.applyGlobalMeshOffset( 0, alt, 0 )
		self.deckOffset = [ 0, alt, 0 ]

	def onBuildForTerrain( self ):
		group = self.parentGroup
		tw, td, alt = group.getDim()
		self.alt = alt
		k = self.name
		x0,y0,z0, x1,y1,z1 = self.getMeshAABB()
		mw, mh, md = x1 - x0, y1 - y0, z1 - z0
		ox, oy, oz = 0, 0, 0
		w, h = self.getSize()
		# print( self.fullName, x0,y0,z0, x1,y1,z1, mh, md )
		self.applyGlobalMeshOffset( -x0, -y0, -z0-md )
		#align to top
		if k in [ 'n', 'c', 'ne', 'e', '-sw', 'we', 'ew' ] : #bottom left
			ox = 0
			oy = alt - mh
			oz = 0
		elif k in ['s', 'se', '-nw' ]: #top left
			ox = 0
			oy = alt - mh
			oz = -td + md
		elif k in [ 'w', 'nw', '-se' ] : #bottom right
			ox = tw - mw
			oy = alt - mh
			oz = 0
		elif k in [ 'sw', 'ne' ] : #top right
			ox = tw - mw
			oy = alt - mh
			oz = -td + md

		# if k in [ 'n', 'c', 'ne', 'e' ] :
		# 	ox = 0
		# 	oy = alt
		# 	oz = 0
		# elif k in [ 'nw', 'w' ]:
		# 	ox = tw - mw
		# 	oy = alt
		# 	oz = 0
		# elif k in [ 's', 'se' ]:
		# 	ox = 0
		# 	oy = 0
		# 	oz = -td/2
		# elif k in [ 'sw' ]:
		# 	ox = tw - mw
		# 	oy = 0
		# 	oz = -td/2
		# elif k == '-nw':
		# 	ox = 0
		# 	oy = 0
		# 	oz = -td/2
		# elif k == '-ne':
		# 	ox = 0
		# 	oy = 0
		# 	oz = 0
		# elif k == '-sw':
		# 	ox = 0
		# 	oy = alt
		# 	oz = 0
		# elif k == '-se':
		# 	ox = 0
		# 	oy = alt
		# 	oz = 0
		# else:
		# 	ox = 0
		# 	oy = 0
		# 	oz = 0

		# elif k == 'ne':
		# 	ox = 0
		# 	oy = alt
		# elif k == 'se':
		# 	ox = 0
		# 	oy = 0
		# 	oz = alt + th - h
		# elif k == 'nw':
		# 	ox = tw - w
		# 	oy = alt
		# elif k == 'sw':
		# 	ox = tw - w
		# 	oy = 0
		# 	oz = alt + th - h
		# elif k == '-ne':
		# 	ox = 0
		# 	oy = 0
		# 	oz = alt + th - h
		# elif k == '-se':
		# 	ox = 0
		# 	oy = alt
		# elif k == '-nw':
		# 	ox = 0
		# 	oy = 0
		# 	oz = alt + th - h
		# elif k == '-sw':
		# 	ox = 0
		# 	oy = alt
		# elif k == 'we':
		# 	ox = 0
		# 	oy = 0
		# 	oz = alt + th - h
		# elif k == 'ew':
		# 	ox = 0
		# 	oy = 0
		# 	oz = alt + th - h
		self.applyGlobalMeshOffset( ox, oy, oz )
		self.deckOffset = [ ox, oy, oz ]

	def getData( self ):
		data = super( TileItem, self ).getData()
		data[ 'name' ] = self.itemName
		data[ 'basename' ] = self.name
		data[ 'fullname' ] = self.fullName
		data[ 'deck_offset' ] = self.deckOffset
		data[ 'raw_rect'    ] = self.aabb
		if self.parts:
			data[ 'raw_index' ] = self.parts[0].getRawIndex()
		else:
			data[ 'raw_index' ] = 0
		return data
		
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
		tile.parentGroup = self

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

		for tile in self.tiles:
			tile.onBuild( project )

	def postBuild( self, project ):
		for tile in self.tiles:
			tile.postBuild( project )

	def __repr__( self ):
		return '%s: %s( %d, %d, %d )' % ( self.name, self.tileType, self.tileWidth, self.tileDepth, self.tileHeight )

	def getData( self ):
		data = {}
		tileDatas = []
		for t in self.tiles:
			tileData = t.getData()
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

	def processItemLayer( self, psdLayer, metaInfo ):
		project = self.project
		tags = metaInfo[ 'tags' ]
		
	def collectGroup( self, group ):
		tileGroup = TileGroup()
		tileGroup.rawName = group.name.encode( 'utf-8' )
		tileGroup.name    = tileGroup.rawName
		def _collectLayer( l, parentName = None ):
			for layer in l.layers:
				layerName = layer.name.encode( 'utf-8' )
				if layerName.startswith( '//' ): continue
				isGroup = isinstance( layer, Group )
				if isGroup:
					#if namespace
					mo = re.match( '\s*\[\s*([\w_-]+\s*\]\s*)', layerName )
					if mo:
						layerName = mo.group(0)
						fullName = parentName and (parentName + '/' + layerName) or layerName
						_collectLayer( layer, fullName )
						continue

				#common
				fullName = parentName and (parentName + '/' + layerName) or layerName
				partLayers = []
				if isinstance( layer, Group ):
					partLayers = extract_leaf_layers( layer )
				else:
					partLayers = [ layer ]

				tile = TileItem( fullName, partLayers )
				tile.rawName = layerName
				tile.name = fullName
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
				infos += tile.getAtlasImgInfos()
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
class MTilesetDeckProcessor( DeckProcessor ):
	def onLoadImage( self, psdImage ):
		pass

	def acceptLayer( self, psdLayer, metaInfo, fallback ):
		if not isinstance( psdLayer, Group ): return False
		tags = metaInfo[ 'tags' ]
		return tags.has_key( 'TILESET' ) or tags.has_key( 'TS' )

	def processLayer( self, psdLayer, metaInfo ):
		name = metaInfo[ 'name' ]
		tileset = MTilesetDeckItem( name, psdLayer )
		self.project.addDeckItem( tileset )
		return True


##----------------------------------------------------------------##
registerDeckProcessor( 'mtileset', MTilesetDeckProcessor )

##----------------------------------------------------------------##


if __name__ == '__main__':
	import PSDDeckPackTest
