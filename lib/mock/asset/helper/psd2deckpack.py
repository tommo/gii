from os.path import basename, splitext
import math
import StringIO
from PIL import Image
from psd_tools import PSDImage, Group, Layer
from psd_tools.constants import ImageResourceID
from psd_tools.utils import read_fmt, read_unicode_string, read_pascal_string
from atlas2 import AtlasGenerator, Img
import copy

import logging
import json

import re

from NormalMapHelper import makeNormalMap

def clamp( x, a, b ):
	return max( a, min( b, x ) )

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
def read_psd_string ( f ):
	l, = read_fmt("I", f)
	if l==0: l = 4;
	return f.read( l )

def read_psd_obj( f, vt = None ):
	if not vt: vt = f.read( 4 )
	if vt == 'long':
		v, = read_fmt('l', f)
		return v

	elif vt == 'bool':
		result, = read_fmt('b', f)
		return result != 0

	elif vt == 'doub':
		result, = read_fmt('d', f)
		return result

	elif vt == 'VlLs':
		count, = read_fmt('I', f)
		result = []
		for i in range( 0, count ):
			v = read_psd_obj( f )
			result.append (v)
		return result

	elif vt == 'Objc':
		nameLen, = read_fmt("I", f)
		f.seek( nameLen * 2, 1 ) #skip name
		classId = read_psd_string( f )
		count, = read_fmt("I", f)
		result = {}
		for i in range( 0, count ):
			key = read_psd_string( f )
			value = read_psd_obj( f )
			result[key] = value
		return result

	elif vt == 'enum':
		typeId = read_psd_string( f )
		value = read_psd_string( f )
		return ( typeId, value )

	elif vt == 'UntF':
		unit = f.read(4)
		value, = read_fmt('d', f)
		return (value, unit)
	
	elif vt == 'TEXT':
		size, = read_fmt("I", f)
		text = f.read( size * 2 ) #TODO: unicode?
		return text

	else:
		raise Exception('not implement: %s ' % vt )

def get_mlst( layer ):
	for md in layer._tagged_blocks['shmd']:
		if md.key == 'mlst':
			f = StringIO.StringIO( md.data )
			f.read(4)
			desc = read_psd_obj( f, 'Objc' )
			return desc
	return None

def get_mani( image ):
	for r in image.decoded_data.image_resource_blocks:
		if r.resource_id == 4000:
			f = StringIO.StringIO( r.data )		
			pluginName = f.read(4)
			assert pluginName == 'mani', pluginName 
			f.seek( 24, 1 )
			desc = read_psd_obj( f, 'Objc' )
			return desc
	return None

def extractLeafLayers( image ):
	def extractGroup( layers, result, parent ):
		for l in layers:
			if isinstance( l, Group ):
				extractGroup( l.layers, result, l )
			else:
				l.parent = parent
				result.append( l )
	result = []
	extractGroup( image.layers, result, None )
	return result

def extract_layer_channel_data( l ):
	decoded_data = l._psd.decoded_data
	layer_index = l._index
	layers = decoded_data.layer_and_mask_data.layers
	layer = layers.layer_records[layer_index]
	channels_data = layers.channel_image_data[layer_index]
	return ( channels_data, layer.width(), layer.height() )

def compare_layer_image( l1, l2 ):
	d1 = extract_layer_channel_data(l1)
	d2 = extract_layer_channel_data(l2)
	#compare size
	if d1[1] != d2[1]: return False
	if d1[2] != d2[2]: return False
	#compare channel raw data
	chs1 = d1[0]
	chs2 = d2[0]
	if len(chs1) != len(chs2): return False
	for i in range(0, len(chs1)):
		ch1 = chs1[i]
		ch2 = chs2[i]
		if ch1.data != ch2.data: return False
	return True

##----------------------------------------------------------------##
class DeckPartImg(Img): #	
	def getImage(self, imgSet = None ):
		return self.src.getImage( imgSet )

##----------------------------------------------------------------##
class DeckPart(object):
	def __init__( self, project, psdLayer ):
		self._project = project
		self._layer = psdLayer
		self.img = None
		x1,y1,x2,y2 = psdLayer.bbox
		self.w = x2-x1
		self.h = y2-y1
		self.x = x1
		self.y = y1
		self.deckRect = ( 0,0,1,1 )
		self.imgInfo = None
		self.meshes = []
		self.globalMeshes = []

	def getSize( self ):
		return (self.w, self.h)

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

	def getOffset( self ):
		return self.x, self.y

	def getImageRawData( self ):
		return self._layer
	
	def getDeckRect( self ):
		return self.deckRect

	def getAtlasImgInfo( self ):
		return self.imgInfo

	def getAtlasNode( self ):
		return self.imgInfo.node

	def build( self, projContext ):
		guideTopFace = projContext.get( 'guide-top-face', 0 )
		( w, h ) = self.getSize()
		( x, y ) = self.getOffset()
		localGuideTopFace = clamp( guideTopFace - y, 0, h )
		img = DeckPartImg ( '', w, h, (0, 0, w, h) )	
		img.src = self
		self.imgInfo = img
		#build normal
		tex = self.getTextureMap()
		normalOption = {
			'guide-top-face' : localGuideTopFace
		}
		self.imgNormal = makeNormalMap( tex, normalOption )
		self.guideTopFace = localGuideTopFace

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

	def updateGlobalMeshOffset( self, globalBottom ):
		offy = globalBottom - self.getBottom()
		self.globalMeshes = []
		for mesh in self.meshes:
			gmesh = copy.deepcopy( mesh )
			for vert in gmesh['verts']:
				vert[ 1 ] += offy
			self.globalMeshes.append( gmesh )

	def buildAtlasUV( self ):
		node = self.getAtlasNode()
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
class DeckItem(object):
	def __init__( self ):
		self.parts = []

	def addPart( self, part ):
		self.parts.append( part )

	def save( self ):
		meshes = []
		for part in self.parts:
			meshes += part.getGlobalMeshes()
		return {
			'name'  : self.name,
			'meshes': meshes,
			'type'  : 'deck2d.mquad'
		}

	def build( self, projContext ):
		meshDatas = []
		bottom = 0
		for part in self.parts:
			part.build( projContext )
			bottom = max( bottom, part.getBottom() )
		#move mesh
		for part in self.parts:
			part.updateGlobalMeshOffset( bottom )

	def buildUV( self ):
		for part in self.parts:
			part.buildAtlasUV()

##----------------------------------------------------------------##
class DeckPackProject(object):
	"""docstring for DeckPackProject"""
	def __init__(self):
		self.tileSize = ( 50, 50 )
		self.columns = 4
		self.decks = []

	def loadPSD( self, path ):
		image = PSDImage.load( path )
		#meta data
		bx0 ,	by0 ,	bx1 ,	by1 = image.bbox
		self.bbox = ( bx0, by0, bx1, by1 )		
		self.tileSize = ( bx1, by1 )
		for layer in image.layers:
			deck = self.collectDeck( layer )
			if deck: self.decks.append( deck )
		#todo:get context settings
			
	def collectDeck( self, group ):
		if not isinstance( group, Group ): return
		deck = DeckItem()
		deck.rawName = group.name.encode( 'utf-8' )
		deck.name = deck.rawName
		def collectLayer( l ):
			for layer in l.layers:
				layerName = layer.name.encode( 'utf-8' )
				if layerName.startswith( '//' ): continue
				if layerName.startswith( '@' ):continue
				if isinstance( layer, Group ):
					collectLayer( layer )
				else:
					part = DeckPart( self, layer )
					part.rawName = layerName
					part.name = layerName
					deck.addPart( part )
		collectLayer( group )
		return deck

	def save( self, path, prefix, size ):
		projContext = {
			'guide-top-face' : 138
		}

		for deck in self.decks:
			deck.build( projContext )
		#calc row/columns
		atlas = self.generateAtlas( path, prefix, size )
		deckDatas = []
		for deck in self.decks:
			deck.buildUV()
			deckDatas.append( deck.save() )
		output = {
			'atlas' : {
				'w' : atlas.w,
				'h' : atlas.h
			},
			'decks' : deckDatas
		}
		saveJSON( output, path + prefix + '.json' )

	def generateAtlas( self, path, prefix, size ):
		infos = []
		for deck in self.decks:
			for part in deck.parts:
				infos.append( part.getAtlasImgInfo() )
		kwargs = {}
		kwargs['spacing'] = 1
		atlasGen = AtlasGenerator( prefix, size, **kwargs )
		atlas = atlasGen.generateOneAtlas( infos, [] )

		atlas.name = prefix + '.png'
		atlas.nameNormal = prefix + '_n' + '.png'
		atlasGen.paintAtlas( atlas, path+atlas.name, format = 'PNG' )
		atlasGen.paintAtlas( atlas, path+atlas.nameNormal, format = 'PNG', imgSet = 'normal' )
		atlas.id = 0

		return atlas
##----------------------------------------------------------------##

if __name__ == '__main__':
	proj = DeckPackProject()
	proj.loadPSD( 'deckpack.psd' )
	proj.save( 'deckpack', ( 1024, 1024 ) )
	# proj.save( 'chicago' )

	# proj.loadPSD( 'tmpnumber.psd' )
	# proj.save( 'numbers' )

	# proj.loadPSD( 'number2.psd' )
	# proj.save( 'numbers2' )
