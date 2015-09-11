from os.path import basename, splitext
import math
import StringIO
import copy
import logging
import json
import re

from psd_tools import PSDImage, Group, Layer
from atlas2 import AtlasGenerator, Img
from MetaTag import parseMetaTag

##----------------------------------------------------------------##
def saveJSON( data, path, **option ):
	outputString = json.dumps( data , 
			indent    = option.get( 'indent' ,2 ),
			sort_keys = option.get( 'sort_keys', True ),
			ensure_ascii=True
		).encode('utf-8')
	fp = open( path, 'w' )
	fp.write( outputString )
	fp.close()
	return True

def trySaveJSON( data, path, dataName = None, **option ):
	try:
		saveJSON( data, path, **option )
		return True
	except Exception, e:
		logging.warn( 'failed to save %s: %s' % ( dataName or 'JSON', path ) )
		logging.exception( e )
		return False

##----------------------------------------------------------------##
class DeckPartImg(Img): #	
	def getImage(self, imgSet = None ):
		return self.src.getImage( imgSet )

##----------------------------------------------------------------##
class DeckPart( object ):
	def __init__( self, psdLayer ):
		self._layer = psdLayer
		layerName = psdLayer.name.encode( 'utf-8' )
		self.rawName = layerName
		self.name    = layerName
		self.img = None
		x1,y1,x2,y2 = psdLayer.bbox
		self.w = x2-x1
		self.h = y2-y1
		self.x = x1
		self.y = y1
		self.deckRect = ( 0,0,1,1 )
		self.deckOffset = ( 0,0 )
		self.rawRect  = ( x1,y1,x2,y2 )
		self.imgInfo = None
		self.rawIndex = psdLayer._index
		self.options = {}

	def getSize( self ):
		return (self.w, self.h)

	def getOffset( self ):
		return self.x, self.y

	def getImageRawData( self ):
		return self._layer

	def getRawIndex( self ):
		return self.rawIndex

	def getRawRect( self ):
		return self.rawRect

	def getDeckRect( self ):
		return self.deckRect

	def getDeckSize( self ):
		x, y, x1, y1 = self.deckRect
		return x1-x, y1-y

	def getDeckOffset( self ):
		return self.deckOffset

	def setAtlasImgInfo( self, imgInfo ):
		self.imgInfo = imgInfo

	def getAtlasImgInfo( self ):
		return self.imgInfo

	def getAtlasNode( self ):
		return self.imgInfo.node

##----------------------------------------------------------------##
class DeckItem(object):
	def onBuild( self, project ):
		pass

	def postBuild( self, project ):
		pass

	def getAtlasImgInfos( self ):
		return []		

	def getData( self ):
		return None

##----------------------------------------------------------------##
class DeckProcesser(object):
	def __init__( self, project ):
		self.project = project 

	def onInit( self, project ):
		pass

	def onLoadImage( self, image ):
		pass

	def acceptLayer( self, layer ):
		return False

	def generateDecks( self, context ):
		pass

##----------------------------------------------------------------##
class DeckPackBuildContext(object):
	def pushAtlasItem( self, imgSet, img ):
		pass

##----------------------------------------------------------------##
_DeckProcessorClassRegistry = []
def registerDeckProcessor( clas ):
	_DeckProcessorClassRegistry.append( clas )


##----------------------------------------------------------------##
class PSDDeckPackProject(object):
	"""docstring for PSDDeckPackProject"""
	def __init__(self):
		#for building
		self.atlasImgInfos = []
		self.deckItems     = []
		self.imageSets     = [ 'color' ]
		self.dirty = True

		self.options = {}
		#init
		self.processors = []
		for clas in _DeckProcessorClassRegistry:
			processor = clas( self )
			processor.onInit( self )
			self.processors.append( processor )

	##for building context
	def getOption( self, key, default = None ):
		return self.options.get( key, default )

	def setOption( self, key, value ):
		self.options[ key ] = value

	def hasOption( self, key ):
		return self.options.has_key( key )

	def addAtlasImgInfo( self, info ):
		self.atlasImgInfos.append( info )

	def addDeckItem( self, deckItem ):
		self.deckItems.append( deckItem )

	def affirmImageSet( self, imgSet ):
		if imgSet in self.imageSets: return True
		self.imageSets.append( imgSet )

	##API
	def loadPSD( self, path ):
		image = PSDImage.load( path )
		for processor in self.processors:
			processor.onLoadImage( image ) 

		self.processGroup( image.layers )
		self.dirty = True

	def processGroup( self, layers ):
		for layer in layers:
			layerName = layer.name.encode( 'utf-8' )
			if layerName.startswith( '//' ): continue
			#category
			if isinstance( layer, Group ) and layerName.endswith( ':GROUP' ):
				self.processGroup( layer.layers )
			else:
				self.processLayer( layer )
		
	def processLayer( self, layer ):
		metaInfo = parseMetaTag( layer.name )
		for processor in self.processors:
			if processor.acceptLayer( layer, metaInfo ):
				processor.processLayer( layer, metaInfo )
				return True
		return False

	def generateAtlas( self, path, prefix, size ):
		infos = []
		for deck in self.deckItems:
			infos += deck.getAtlasImgInfos()

		option = {
			'spacing' : 1
		}
		atlasGen = AtlasGenerator( prefix, size, **option )
		atlas = atlasGen.generateOneAtlas( infos, [] )

		atlas.name = prefix + '.png'
		atlas.nameNormal = prefix + '_n' + '.png'
		atlasGen.paintAtlas( atlas, path+atlas.name,       format = 'PNG' )
		atlasGen.paintAtlas( atlas, path+atlas.nameNormal, format = 'PNG', imgSet = 'normal' )
		atlas.id = 0

		return atlas

	def build( self, path, prefix, size ):
		if not self.dirty: return

		for deck in self.deckItems:
			deck.onBuild( self )

		atlas = self.generateAtlas( path, prefix, size )
		self.generatedAtlas = atlas

		for deck in self.deckItems:
			deck.postBuild( self )

		self.dirty = False

	def save( self, path, prefix, size ):
		self.build( path, prefix, size )
		#save
		deckDatas = []
		for deck in self.deckItems:
			deckData = deck.getData()
			if deckData: deckDatas.append( deckData )

		#atlas info
		atlas = self.generatedAtlas
		atlasInfo = {
			'w' : atlas.w,
			'h' : atlas.h
		}

		#output
		output = {
			'atlas' : atlasInfo,
			'decks' : deckDatas,
		}

		saveJSON( output, path + prefix + '.json' )

##----------------------------------------------------------------##

if __name__ == '__main__':
	import PSDDeckPackTest	
