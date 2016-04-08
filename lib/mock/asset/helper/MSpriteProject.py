# -*- coding: utf-8 -*-
import os.path
import StringIO
from psd_tools import PSDImage, Group, Layer
from psd_tools.decoder.actions import Boolean, Integer, List, Descriptor
from psd_tools.constants import ImageResourceID
from psd_tools.utils import read_fmt, read_unicode_string, read_pascal_string
from atlas2 import AtlasGenerator, Img

from psd_tools_helper import *
import re

from util.AsepriteFile import *

import logging
import json

# def compare_image( img1, img2 ):
# 	if img1.size != img2.size: return False
# 	if img1.

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
class LayerImg(Img): #	
	def getImage(self, imgSet = None):
		return self.src.getImage()

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
	def __init__( self ):
		self.w = 0
		self.h = 0
		self.img = None
		self.imgInfo = None

	def getSize( self ):
		return ( self.w, self.h )

	def getImage( self ):
		return self.img

	def getImageRawData( self ):
		return None

	def getAtlasNode( self ):
		return self.imgInfo.node


class SubImgPsdLayer(object):
	def __init__( self, psdLayer ):
		super( SubImgPsdLayer, self ).__init__()
		self._layer = psdLayer
		x1,y1,x2,y2 = psdLayer.bbox
		self.w = x2-x1
		self.h = y2-y1

	def getImage( self ):
		if self.img: return self.img
		self.img = self._layer.as_PIL()
		return self.img

	def getImageRawData( self ):
		return self._layer


class SubImgCel( SubImg ):
	def __init__( self, cel ):
		super( SubImgCel, self ).__init__()
		self._cel = cel
		x1,y1,x2,y2 = cel.bbox
		self.w = x2-x1
		self.h = y2-y1
		# print self.w, self.h

	def getImageRawData( sel ):
		return self._cel

	def getImage( self ):
		if self.img: return self.img
		self.img = self._cel.getImage()
		return self.img
		

class Anim(object):
	def __init__(self):
		self.name = "null"
		self.frames = []
		self.ox = 0
		self.oy = 0

	def addFrame( self, frame, offsetX, offsetY ):
		self.frames.append( { 'frame':frame, 'offset': (offsetX, offsetY) } )
		pass

	def setOrigin( self, x, y ):
		self.ox = x
		self.oy = y

	def getOrigin( self ):
		return self.ox, self.oy

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
		for subImg in self.subImgCache.values():
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
		return self.currentFeatureId

	def affirmFeature( self, featureName ):
		id = self.getFeature( featureName )
		if id != None: return id
		return self.addFeature( featureName )

	def getFeature( self, featureName ):
		if not featureName: return 0
		return self.featureNames.get( featureName, None )

	def save( self, atlasPath, jsonPath, atlasSize = (2048,2048) ):
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

	def addModule( self, subImg ):
		m = AnimModule( subImg )
		m.id = self.currentModuleId + 0x1000
		self.currentModuleId += 1
		return m

	def getModuleByPsdLayer( self, psdLayer ):
		m = self.moduleCache.get( psdLayer )		
		if m: return m
		subImg = None
		for l1, img1 in self.subImgCache.items():
			if not isinstance( l1, PSDLayer ): continue
			if compare_layer_image( psdLayer, l1 ):
				subImg = img1
				break
		if not subImg:
			subImg = SubImgPsdLayer( psdLayer )
			self.subImgCache[ psdLayer ] = subImg
		
		m = self.addModule( subImg )
		m.feature = psdLayer._featureId
		self.moduleCache[ psdLayer ] = m
		return m

	def getModuleByASECel( self, cel ):
		m = self.moduleCache.get( cel )
		if m : return m
		subImg = None
		# for c1, img1 in self.subImgCache.items():
		# 	if not isinstance( c1, ASECel ): continue
		# 	if compare_image( img1, c1.getImage() ):
		# 		subImg = img1
		# 		break
		if not subImg:
			subImg = SubImgCel( cel )
			self.subImgCache[ cel ] = subImg
		m = self.addModule( subImg )
		m.feature = 0
		self.moduleCache[ cel ] = m
		return m


	def loadFolder( self, path ):
		for fileName in os.listdir( path ):
			fullPath = path + '/' + fileName
			name, ext = os.path.splitext( fileName )
			if ext == '.psd':
				self.loadPSD( fullPath )
			elif ext == '.ase':
				self.loadASE( fullPath )

	def loadASE( self, path ):
		doc = ASEDocument()
		doc.load( path )
		if not doc.frames: return

		anim = Anim()
		#find origin
		for cel in doc.frames[0].cels:
			rcel = cel.getRealCel()
			if rcel.layer.name == '@origin':
				bx0, by0, bx1, by1 = rcel.bbox
				ox = ( bx0 + bx1 ) / 2
				oy = ( by0 + by1 ) / 2
				anim.setOrigin( ox, oy )
				continue
		ox, oy = anim.getOrigin()
		flist = []
		for frameData in doc.frames:
			frame = AnimFrame()
			flist.append( frame )
			frame.delay = float(frameData.duration)/1000.0
			for cel in frameData.cels:
				rcel = cel.getRealCel()
				m = self.getModuleByASECel( rcel )
				layer = rcel.layer
				if layer.isBackground():
					continue
				# if ( not layer.isVisible() ) 
				# 	continue
				layerName = layer.name.strip()
				if layerName.startswith( '@' ) or layerName.startswith( '//' ): continue
				if layerName.startswith( '#' ):
					mo = re.search( '#(\w+)', layerName )
					if mo:
						featureName = mo.group( 1 )
						m.feature = self.affirmFeature( featureName )
				bx0, by0, bx1, by1 = rcel.bbox
				frame.addModule( m, bx0+cel.x -ox, by0+cel.y -oy )
			anim.addFrame( frame, 0, 0 )
			self.addFrame( frame )

		self.addAnim( anim )
		animName,ext = os.path.splitext( os.path.basename( path ) )
		anim.name = animName

		#split tag into sub animations
		for tagData in doc.tags:
			f0, f1 = tagData.frameFrom, tagData.frameTo
			name = tagData.name
			subAnim = Anim()
			subAnim.setOrigin( ox, oy )
			subAnim.name = animName + ':' + name
			for sfid in range( f0, f1 + 1 ):
				frame = flist[ sfid ]
				subAnim.addFrame( frame, 0, 0 )
			self.addAnim( subAnim )


	def loadPSD( self, path ):
		image = PSDImage.load( path )
		#meta data
		ox = 0
		oy = 0
		bx0 ,	by0 ,	bx1 ,	by1 = image.bbox
		mani = get_mani( image )
		layers   = extract_leaf_layers ( image )
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
			elif not ( name and ( name[0] == '@' or name=='背景' ) ):
				outputLayers.append( l )
		#2. foreach frame: 
		#      find valid layer (visible & inside output bbox)
		#      find in cache ( using hash/ direct comparison )
		#      if not in cache, add new one
		# for l in layers:
		# print 'layer count:', len( outputLayers )
		anim = Anim()
		frameDelays = {}
		if mani: #single frame
			frameList = mani['FSts'][0]['FsFr']
			activeFrame = mani['FSts'][0]['AFrm']
			for data in mani['FrIn']:
				frameDelays[ data['FrID'] ] = 0.1
				# frameDelays[ data['FrID'] ] = data[ 'FrDl' ]
		else:
			frameList = [0]
			frameDelays[0] = 0.1
			activeFrame = 0


		index = 0
		layerStates = {}
		outputLayers.reverse()
		for l in outputLayers:
			# print 'L:', l.name.encode('utf-8'), l.visible
			x0 = 0
			y0 = 0
			visible = True
			states = {}
			modData = layerModifyDict[l]
			if modData:
				#find initial visiblity

				#calculate visiblity for each frame
				for mod in modData['LaSt']:
					fid =  mod['FrLs'][0]
					ofst = mod.get('Ofst', None)
					if ofst:
						x0 = ofst['Hrzn']
						y0 = ofst['Vrtc']
					visible = mod.get('enab', visible)
					states[ fid ] = ( visible, x0, y0 )
			else:
				states[0] = ( l.visible, 0, 0 )

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
				name = l.name
				if not visible: continue
				#check inside bbox				
					
				x0, y0 ,x1 ,y1 = l.bbox
				if x0 + offx < bx0:	continue
				if y0 + offy < by0:	continue
				if x1 + offx > bx1:	continue
				if y1 + offy > by1:	continue
				m = self.getModuleByPsdLayer( l )
				x = x0 - ox + offx 
				y = y0 - oy + offy
				frame.addModule( m, x, y )
			anim.addFrame( frame, 0, 0 )
			self.addFrame( frame )
		self.addAnim( anim )
		n,ext = os.path.splitext( os.path.basename( path ) )
		anim.name = n

if __name__ == '__main__':
	proj = MSpriteProject()
	# proj.loadFolder( 'test/InsectCrow.msprite' )
	# proj.save( 'test/InsectCrow_data.png', 'test/InsectCrow_data.json' )
	proj.loadFolder( 'test/solomon.msprite' )
	proj.save( 'test/solomon.png', 'test/solomon.json' )
