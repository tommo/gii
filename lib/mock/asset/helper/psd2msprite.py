from os.path import basename, splitext
import StringIO
from psd_tools import PSDImage, Group, Layer
from psd_tools.decoder.actions import Boolean, Integer, List, Descriptor
from psd_tools.constants import ImageResourceID
from psd_tools.utils import read_fmt, read_unicode_string, read_pascal_string
from atlas2 import AtlasGenerator, Img

import re

import logging
import json


def saveJSON( data, path, **option ):
	outputString = json.dumps( data , 
			indent    = option.get( 'indent' ,2 ),
			sort_keys = option.get( 'sort_keys', True ),
			ensure_ascii=False
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

def namedTupleToValue( t ):
	tt = type( t )
	if   tt == Descriptor:
		r = {}
		for entry in t.items:
			key, data = entry
			r[ key ] = namedTupleToValue( data )
		return r

	elif tt == List:
		r = []
		for entry in t.items:
			r.append( namedTupleToValue( entry ) )
		return r

	else: #Boolean/Integer/String/...
		return t.value


def get_mlst( layer ):
	for md in layer._tagged_blocks['shmd']:
		if md.key == 'mlst':
			return namedTupleToValue( md.data )
	return None


def _parse_feature_meta( s ):
	lines = s.split( '||' )
	maxId = int( lines[ 1 ] );
	count = int( lines[ 2 ] );
	result = {}
	for i in range( count ):
		ss = lines[ i + 3 ]
		f = _str_to_feature( ss )
		result[ f['id'] ] = f
	return result

def _ITB( k ):
	if k == 1:
		return True
	else:
		return False

def _str_to_feature( s ):
	lines = s.split( ']/[' )
	return {
		'id'   : int( lines[0] ),
		'name' : lines[1],
		'active' :_ITB( int( lines[2] ) ),
		'visible' :_ITB( int( lines[3] ) ),
	}


def get_psd_features( image ):
	for r in image.decoded_data.image_resource_blocks:
		if r.resource_id == ImageResourceID.XMP_METADATA:
			m = re.search( '<photoshop:Source>(.+)</photoshop:Source>', r.data )
			if m:
				return _parse_feature_meta( m.group( 1 ) )
			return None

def get_mani( image ):
	for r in image.decoded_data.image_resource_blocks:
		if r.resource_id >= ImageResourceID.PLUGIN_RESOURCES_0 and r.resource_id < ImageResourceID.PLUGIN_RESOURCES_LAST:
			f = StringIO.StringIO( r.data )
			pluginName = f.read(4)
			if pluginName == 'mani':
				f.seek( 24, 1 )
				desc = read_psd_obj( f, 'Objc' )
				return desc
	return None

def get_layer_feature( layer ):
	for md in layer._tagged_blocks['shmd']:
		if md.key == 'cust':
			data = namedTupleToValue( md.data )
			xmp = data.get( 'layerXMP', None )
			if not xmp: return False
			m = re.search( '<exif:feature>(\w+)', xmp )
			return int( m.group( 1 ) )
	return -1

def extractLeafLayers( image ):
	def extractGroup( layers, result ):
		for l in layers:
			if isinstance( l, Group ):
				extractGroup( l.layers, result )
			else:
				result.append( l )
	result = []
	extractGroup( image.layers, result )
	return result

##----------------------------------------------------------------##
class LayerImg(Img): #	
	def getImage(self, imgSet = None):
		return self.src.getImage()

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

class AnimFrame(object):
	def __init__( self ):
		self.parts = []
		self.name = "null"

	def addModule( self, m, offsetX, offsetY ):
		self.parts.append( { 'module':m, 'offset': (offsetX, offsetY) } )

class AnimModule(object):
	def __init__( self, subImg ):
		self.subImg = subImg
		self.feature = None

class SubImg(object):
	def __init__( self, psdLayer ):
		self._layer = psdLayer
		self.img = None
		x1,y1,x2,y2 = psdLayer.bbox
		self.w = x2-x1
		self.h = y2-y1
		self.imgInfo = None

	def getSize( self ):
		return (self.w, self.h)

	def getImage( self ):
		if self.img: return self.img
		self.img = self._layer.as_PIL()
		return self.img

	def getImageRawData( self ):
		return self._layer

	def getAtlasNode( self ):
		return self.imgInfo.node


class Anim(object):
	def __init__(self):
		self.name = "null"
		self.frames = []

	def addFrame( self, frame, offsetX, offsetY ):
		self.frames.append( { 'frame':frame, 'offset': (offsetX, offsetY) } )
		pass

	def setOrigin( self, x, y ):
		self.ox = x
		self.oy = y

	def setBound( self, x, y, w, h ):
		self.bound = ( x,y,w,h )
 
class MSpriteProject(object):
	def __init__(self):		
		self.modules = []
		self.animations = []
		self.frames = []
		self.moduleCache = {}
		self.subImgCache = {}
		self.featureNames = {}
		self.currentModuleId = 0
		self.currentFrameId = 0
		self.currentAnimId = 0
		self.currentFeatureId = 0

	def addAnim( self, anim ):
		self.animations.append( anim )
		anim.id = self.currentAnimId + 0x3000
		self.currentAnimId += 1

	def addFrame( self, frame ):
		self.frames.append( frame )
		frame.id = self.currentFrameId + 0x2000
		self.currentFrameId += 1

	def generateImagesInfo( self ):
		infos = []
		for subImg in self.subImgCache.itervalues():
			( w, h ) = subImg.getSize()
			img = LayerImg ( '', w, h, (0, 0, w, h) )	
			img.src = subImg
			infos.append( img )
			subImg.imgInfo = img
		return infos

	def generateAtlas( self, atlasPath, atlasSize, **kwargs ):
		#5. pack all bitmap in cache into atlas
		prefix='output' #TODO: use real output name
		kwargs['spacing'] = 1

		imageInfos = self.generateImagesInfo()

		atlasGen = AtlasGenerator( prefix, atlasSize, **kwargs )
		atlas = atlasGen.generateOneAtlas( imageInfos, [] )
		
		atlas.name = atlasPath
		atlasGen.paintAtlas( atlas, atlas.name )
		atlas.id = 0

		return atlas

	def addFeature( self, featureName ):
		if self.featureNames.get( featureName ): return
		self.currentFeatureId += 1
		self.featureNames[ featureName ] = self.currentFeatureId

	def getFeature( self, featureName ):
		if not featureName: return 0
		return self.featureNames.get( featureName, None )

	def save( self, atlasPath, jsonPath, atlasSize = (1024,1024) ):
		atlases = [ self.generateAtlas( atlasPath, atlasSize, bleeding = True ) ]
		atlasData  = {}
		moduleData = {}
		frameData  = {}
		animData   = {}
		featureData = []
		#atlas
		for atlas in atlases:
			atlasData[ str( atlas.id ) ] = atlas.name

		#modules
		for m in self.moduleCache.itervalues():
			node = m.subImg.getAtlasNode()			
			moduleData[ str( m.id ) ] = {
				'atlas' : str( node.root.id ),
				'rect'  : node.getRect(),
				'feature' : m.feature
			}
			
		#frames
		for frame in self.frames:
			parts = []
			for part in frame.parts:
				moduleId = part['module'].id
				( offsetX, offsetY ) = part['offset']
				parts.append( [ str(moduleId), offsetX, offsetY  ] )
			frameData[ str( frame.id ) ] = {
				'name' : frame.name,
				'parts' : parts
			}
		
		#anims
		for anim in self.animations:
			seq = []
			for entry in anim.frames:
				frame = entry['frame']
				( offsetX, offsetY ) = entry['offset']
				seq.append(
					[ str( frame.id ), frame.delay / 10, offsetX, offsetY ]
				)
			animData[ str( anim.id ) ] = {
				'name' :anim.name,
				'seq'  :seq
			}

		for name, id in self.featureNames.items():
			featureData.append( {
				'id': id,
				'name': name,
				} )

		output = {
			'atlases' : atlasData,
			'modules' : moduleData,
			'frames'  : frameData,
			'anims'   : animData,
			'features' : featureData
		}

		saveJSON( output, jsonPath )

	def getModule( self, psdLayer ):
		m = self.moduleCache.get( psdLayer )		
		if m: return m
		subImg = None
		for l1, img1 in self.subImgCache.items():
			if compare_layer_image( psdLayer, l1 ):
				subImg = img1
				break
		if not subImg:
			subImg = SubImg( psdLayer )
			self.subImgCache[ psdLayer ] = subImg
		m = AnimModule( subImg )
		m.id = self.currentModuleId + 0x1000
		m.feature = psdLayer._featureId

		self.currentModuleId += 1
		self.moduleCache[ psdLayer ] = m
		return m

	def loadFolder( self, path ):
		pass

	def loadPSD( self, path ):
		image = PSDImage.load( path )
		#meta data
		ox = 0
		oy = 0
		bx0 ,	by0 ,	bx1 ,	by1 = image.bbox
		mani = get_mani( image )
		# print(mani)
		layers   = extractLeafLayers ( image )
		docFeatures = get_psd_features( image )
		if docFeatures:
			for entry in docFeatures.values():
				self.addFeature( entry['name'] )

		layerModifyDict = {}
		outputLayers = []
		layerFeatures = {}
		#1. extract meta data:  X/Y axis,  output bound box
		for l in layers:
			stat = get_mlst(l)
			# print(stat, l.name)
			layerModifyDict[ l ] = stat
			name = l.name.encode( 'utf-8' )
			if name == '@axis-x': 
				x0, y0, x1, y1 = l.bbox
				oy = y0
			elif name == '@axis-y': 
				x0, y0, x1, y1 = l.bbox
				ox = x0
			elif name == '@output': 
				bx0 ,	by0 ,	bx1 ,	by1 = l.bbox
			elif not ( name and name[0] == '@' ):
				outputLayers.append( l )
		#2. foreach frame: 
		#      find valid layer (visible & inside output bbox)
		#      find in cache ( using hash/ direct comparison )
		#      if not in cache, add new one
		# for l in layers:
		# print 'layer count:', len( outputLayers )
		anim = Anim()
		# print(mani)
		frameDelays = {}
		for data in mani['FrIn']:
			# frameDelays[ data['FrID'] ] = data[ 'FrDl' ]
			frameDelays[ data['FrID'] ] = 0.1

		frameList = mani['FSts'][0]['FsFr']
		index = 0
		layerStates = {}
		outputLayers.reverse()
		for l in outputLayers:
			x0 = 0
			y0 = 0
			visible = l.visible
			states = {}
			modData = layerModifyDict[l]
			if modData:
				for mod in modData['LaSt']:
					fid =  mod['FrLs'][0]
					ofst = mod.get('Ofst', None)
					if ofst:
						x0 = ofst['Hrzn']
						y0 = ofst['Vrtc']
					visible = mod.get('enab', visible)
					states[ fid ] = ( visible, x0, y0 )
			layerStates[ l ] = states
			l._featureId = 0
			if docFeatures:
				localFeatureId = get_layer_feature( l )
				if localFeatureId >= 0:
					fname = docFeatures[ localFeatureId ].get( 'name', None )
					l._featureId = self.getFeature( fname )

		for fid in frameList:
			frame = AnimFrame()
			frame.delay = frameDelays.get( fid, 0 )
			frame._fid = fid
			for l in outputLayers:
				#find modify state
				layerModify = None
				modData = layerModifyDict[l]
				if modData:
					for mod in modData['LaSt']:
						if mod['FrLs'][0] == fid: 
							layerModify = mod
							break				
				states = layerStates[l]

				#check enabled
				defaultState = ( l.visible, 0, 0 ) 
				fstate = states.get( fid, defaultState )
				visible, offx, offy = fstate
				if not visible: continue
				#check inside bbox				
					
				x0, y0 ,x1 ,y1 = l.bbox
				if x0 + offx < bx0: continue
				if y0 + offy < by0: continue
				if x1 + offx > bx1: continue
				if y1 + offy > by1: continue
				m = self.getModule( l )
				x = x0 - ox + offx 
				y = y0 - oy + offy
				frame.addModule( m, x, y )
			anim.addFrame( frame, 0, 0 )
			self.addFrame( frame )
		self.addAnim( anim )
		n,ext = splitext( basename( path ) )
		anim.name = n

# proj = MSpriteProject()
# proj.loadPSD( 'zombie-1/attack-f.psd' )
# proj.loadPSD( 'zombie-1/hurt-f.psd' )
# proj.loadPSD( 'zombie-1/stand-f.psd' )
# proj.loadPSD( 'zombie-1/move-f.psd' )

# proj.loadPSD( 'zombie-1/attack-b.psd' )
# proj.loadPSD( 'zombie-1/hurt-b.psd' )
# proj.loadPSD( 'zombie-1/stand-b.psd' )
# proj.loadPSD( 'zombie-1/move-b.psd' )

# proj.saveJSON( 'zombie', (256, 128 ) )



