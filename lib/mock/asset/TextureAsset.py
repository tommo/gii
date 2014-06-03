import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *
from mock import _MOCK
from ImageHelpers import convertToPNG, convertToWebP, getImageSize
from TextureProcessor import applyTextureProcessor

##----------------------------------------------------------------##
signals.register( 'texture.add' )
signals.register( 'texture.remove' )
signals.register( 'texture.rebuild' )

##----------------------------------------------------------------##
_TEXTURE_LIBRARY_DATA_FILE = 'texture_library.json'
_ATLAS_JSON_NAME = 'atlas.json'

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


##----------------------------------------------------------------##
class TextureGroup( object ):	
	def __init__( self, name, config = None ):
		self.name   = name
		#default config
		self.filter             = 'nearest'
		self.compression        = None
		self.mipmap             = False
		self.wrapmode           = 'clamp'
		self.atlas_allowed      = True
		self.atlas_max_width    = 1024
		self.atlas_max_height   = 1024
		self.atlas_force_single = False
		self.cache              = None

	def copy( self, src ):
		self.filter             = src.filter
		self.compression        = src.compression
		self.mipmap             = src.mipmap
		self.wrapmode           = src.wrapmode
		self.atlas_allowed      = src.atlas_allowed
		self.atlas_max_width    = src.atlas_max_width
		self.atlas_max_height   = src.atlas_max_height
		self.atlas_force_single = src.atlas_force_single

	def toJson( self ):
		return {
				'name'               : self.name,
				'filter'             : self.filter ,
				'compression'        : self.compression ,
				'mipmap'             : self.mipmap ,
				'wrapmode'           : self.wrapmode ,
				'atlas_allowed'      : self.atlas_allowed ,
				'atlas_max_width'    : self.atlas_max_width ,
				'atlas_max_height'   : self.atlas_max_height ,
				'atlas_force_single' : self.atlas_force_single ,
				'cache'              : self.cache
			}

	def fromJson( self, gdata ):
		self.filter             = gdata[ 'filter' ]
		self.compression        = gdata[ 'compression' ]
		self.mipmap             = gdata[ 'mipmap' ]
		self.wrapmode           = gdata[ 'wrapmode' ]
		self.atlas_allowed      = gdata[ 'atlas_allowed' ]
		self.atlas_max_width    = gdata[ 'atlas_max_width' ]
		self.atlas_max_height   = gdata[ 'atlas_max_height' ]
		self.atlas_force_single = gdata[ 'atlas_force_single' ]
		if not self.atlas_allowed:
			self.cache = None
		else:
			self.cache = gdata.get( 'cache', None )

##----------------------------------------------------------------##
def groupToJson( group ):
	return {
				'name'               : group.name,
				'filter'             : group.filter,
				'mipmap'             : group.mipmap,
				'wrap'               : group.wrap ,
				'atlas_mode'         : group.atlasMode ,
				'cache'              : group.cache
			}

def _fixPath( path ):
		path = path.replace( '\\', '/' ) #for windows
		if path.startswith('./'): path = path[2:]
		return path	
		

##----------------------------------------------------------------##
def _convertAtlas( inputfile,  srcToAssetDict ):
	f = open( inputfile, 'r' )
	items      = []
	atlasNames = []
	atlasInfos = []
	readingMode = 'sprite'

	for line in f.readlines():
		if line.startswith( '[atlas]' ):
			readingMode = 'atlas'
			continue
		if line.startswith( '[sprite]' ):
			readingMode = 'sprite'
			continue
		if readingMode == 'atlas':
			parts       = line.split('\t')
			name        = parts[ 0 ]
			atlasNames.append( name )
			atlasInfos.append( {
					'name': os.path.basename(name),
					'size':[ int(parts[1]), int(parts[2]) ]
				} )
		else:
			parts       = line.split('\t')
			sourcePath  = _fixPath( parts[1] )
			if sourcePath.startswith('\"'):
				sourcePath = sourcePath[1:-1]		
			# name = os.path.basename( sourcePath )
			assetPath = srcToAssetDict[ sourcePath ]
			atlasName = parts[0]		
			atlasId = atlasNames.index( atlasName )
			data = {
				'atlas'  : atlasId,
				'name'   : assetPath,
				'source' : sourcePath,
				'rect'   : [ int(x) for x in parts[2:] ]
			}
			items.append(data)

	output = {
		'atlases' : atlasInfos,
		'items'   : items,
	}

	return output

##----------------------------------------------------------------##
class TextureAssetManager( AssetManager ):
	def getName(self):
		return 'asset_manager.texture'

	def acceptAssetFile(self, filepath):
		name,ext = os.path.splitext(filepath)
		if os.path.isfile(filepath):
			return ext in [ '.png', '.psd', '.jpg', '.bmp', '.jpeg' ]
		else:
			return ext in ['.texstrip' ]

	def importAsset(self, node, reload = False ):
		node.assetType = 'texture'
		group = node.getMetaData( 'group' )
		if not group:
			group = 'default'
			node.setNewMetaData( 'group', group )
		if os.path.isdir( node.getAbsFilePath() ):
			node.setBundle()
		TextureLibrary.get().scheduleImport( node ) #let texture library handle real import
		return True

	def deployAsset( self, node, context ):
		super( TextureAssetManager, self ).deployAsset( node, context )
		texNode = app.getModule( 'texture_library' ).findTextureNode( node )
		if not texNode:
			logging.warn( 'texture node not found:' + node.getNodePath() )
			return
		group = texNode.parent
		if group.cache and group.atlasMode:
			if not context.hasFile( group.cache ):
				newPath = context.addFile( group.cache )
				atlasData = jsonHelper.tryLoadJSON( context.getPath( newPath ) + '/' + _ATLAS_JSON_NAME )
				if atlasData:
					#convert webp
					for atlasEntry in atlasData['atlases']:
						texName = atlasEntry['name']
						fn = context.getPath( newPath ) + '/' + texName
						if context.isNewFile( fn ):
							convertToWebP( fn )
			else:
				newPath = context.getFile( group.cache )

			mappedConfigFile = context.getFile( node.getObjectFile('config') )
			context.replaceInFile( context.getPath( mappedConfigFile ), group.cache, newPath )			
		else:			
			#convert webp
			fn = context.getAbsFile( node.getObjectFile( 'pixmap' ) )
			if context.isNewFile( fn ):				
				convertToWebP( fn )

##----------------------------------------------------------------##
class PrebuiltAtlasAssetManager( AssetManager ):
	def getName(self):
		return 'asset_manager.prebuilt_atlas'

	def importAsset(self, node, reload = False ):
		print 'importing', node, reload
		return True

##----------------------------------------------------------------##
class TextureLibrary( EditorModule ):
	_singleton = None
	@staticmethod
	def get():
		return TextureLibrary._singleton

	def __init__( self ):
		assert not TextureLibrary._singleton
		TextureLibrary._singleton = self
		self.lib = None
		self.pendingImportGroups = {}
		self.pendingImportTextures = {}

	def getName( self ):
		return 'texture_library'

	def getDependency( self ):
		return ['mock']

	def onLoad( self ):
		self.dataPath  = self.getProject().getConfigPath( _TEXTURE_LIBRARY_DATA_FILE )		
		self.delegate  = app.getModule('moai').loadLuaDelegate( _getModulePath('TextureLibrary.lua') )

		signals.connect( 'asset.post_import_all', self.postAssetImportAll )
		signals.connect( 'asset.unregister',      self.onAssetUnregister )

		signals.connect( 'project.post_deploy', self.postDeploy )
		signals.connect( 'project.save', self.onSaveProject )

	def onStart( self ):		
		self.loadIndex()		

	def getLibrary( self ):
		return self.lib

	def loadIndex( self ):
		self.lib = _MOCK.loadTextureLibrary( self.dataPath )
		for group in self.lib.groups.values():
			if group.atlasCachePath:
				CacheManager.get().touchCacheFile( group.atlasCachePath )
			
	def saveIndex( self ):
		logging.info( 'saving texture library index' )
		self.lib.save( self.lib, self.dataPath )

	def findTextureNode( self, assetNode ):
		lib = self.lib
		t = lib.findTexture( lib, assetNode.getNodePath() )
		return t

	def scheduleImport( self, node ):
		lib = self.lib
		t = lib.findTexture( lib, node.getNodePath() )
		if not t:
			t = lib.addTexture( lib, node.getNodePath() )
			assert t
			signals.emit( 'texture.add', t )

		self.pendingImportTextures[ node ] = t		
		
	def doPendingImports( self ):
		pendingImportTextures = self.pendingImportTextures
		self.pendingImportTextures = {}
		lib = self.lib
		pendingAtlasGroups = set()
		for node, t in pendingImportTextures.items():			
			group = t.parent
			if group.isAtlas( group ):
				self.processTextureNode( t, node )
				pendingAtlasGroups.add( group )
			elif node.isType( 'prebuilt_atlas' ):
				self.buildPrebuiltAtlas( t, node )
			else:
				self.processTextureNode( t, node )
				self.buildSingleTexture( t, node )

		for group in pendingAtlasGroups:
			self.buildAtlas( group )	
			
		self.saveIndex()

	def processTextureNode( self, texture, assetNode ):
		logging.info( 'processing texture: %s' % assetNode.getNodePath() )
		assetNode.clearCacheFiles()
		src = assetNode.getAbsFilePath()
		dst = assetNode.getAbsCacheFile( 'pixmap' ) 
		return self._processTexture( src, dst, texture )

	def _processTexture( self, src, dst, texture ):
		#convert single image
		result = convertToPNG( src, dst )		
		#apply processor on dst file
		group = texture.parent
		if group:
			groupProcessor = group.processor
			if groupProcessor:
				applyTextureProcessor( groupProcessor, dst )
			nodeProcessor = texture.processor
			if nodeProcessor:
				applyTextureProcessor( nodeProcessor, dst )				

	def explodePrebuiltAtlas( self, texItem ):
		return []

	def buildAtlas( self, group ):
		logging.info( '' )
		logging.info( 'building atlas texture:' + group.name )

		#packing atlas
		assetLib = self.getAssetLibrary()
		nodes = [] 
		for t in group.textures.values():
			node = assetLib.getAssetNode( t.path )
			if node:
				nodes.append( node )
			else:
				logging.warn( 'node not found: %s' % t.path )

		sourceList     = []
		srcToAssetDict = {}
		prebuiltAtlases = []
		for node in nodes:
			if not node.isType( 'prebuilt_atlas' ):
				path = node.getAbsCacheFile( 'pixmap' )
				srcToAssetDict[ path ] = node.getNodePath()
				sourceList.append( path )
			else:
				prebuiltAtlases.append( node )
		
		if group.repackPrebuiltAtlas:
			pass
			#TODO
			# explodedAtlas = {}
			# for t in prebuiltAtlases.values():
			# 	explodedAtlas[ t ] = self.explodePrebuiltAtlas( t )
		else:
			for t in prebuiltAtlases.values():
				pass

		#use external packer
		atlasName = 'atlas_' + group.name

		tmpDir = CacheManager.get().getTempDir()
		prefix = tmpDir( atlasName )

		outputDir = CacheManager.get().getCacheDir( '<texture_group>/' + group.name  )
		for name in os.listdir( outputDir ): #clear target path
			try:
				os.remove( outputDir + '/' + name )
			except Exception, e:
				pass

		arglist = [ 'python', _getModulePath('tools/AtlasGenerator.py'), '--prefix', prefix ]
		arglist += [ str( group.maxAtlasWidth ) , str( group.maxAtlasHeight ) ]
		arglist += sourceList
		try:
			ex = subprocess.call( arglist ) #run packer
			#conversion
			srcFile = prefix + '.txt'
			data    = _convertAtlas( srcFile,  srcToAssetDict )
			dstPath = outputDir
			#copy generated atlas
			for i, entry in enumerate( data['atlases'] ):
				src = entry['name']
				dstName = 'tex_%d' % i
				# dst = '%s/%s%d' % ( dstPath, atlasName, i )
				entry['name'] = dstName
				shutil.copy( tmpDir( src ), dstPath +'/' + dstName )
			#update texpack
			data[ 'sources' ] = sourceList
			cfgPath = outputDir + '/' + _ATLAS_JSON_NAME
			fp = open( cfgPath, 'w' )
			json.dump( data, fp, sort_keys=True, indent=2 )
			fp.close()

		except Exception,e:
			logging.exception( e )
			return False

		group._loadBuiltAtlas( group, outputDir )
		self.delegate.call( 'releaseTexPack', outputDir )

		#redirect asset node to sub_textures
		for node in nodes:
			self.buildSubTexture( group, node )
	
		return True

	def buildSingleTexture( self, tex, node ):
		group = tex.parent
		logging.info( 'building single texture: %s<%s>' % ( node.getPath(), group.name ) )
		node.clearObjectFiles()
		dst = node.getCacheFile( 'pixmap' )
		node.setObjectFile( 'pixmap', dst )
		w, h = getImageSize( dst )
		tex._loadSingleTexture( tex, dst, w, h )
		signals.emit( 'texture.rebuild', node )
		#todo: check process result!

	def buildPrebuiltAtlas( self, tex, node ):
		group = tex.parent
		logging.info( 'building prebuilt atlas: %s<%s>' % ( node.getPath(), group.name ) )
		atlasPath = node.getCacheFile( 'atlas' )
		atlas = self.delegate.call( 'loadPrebuiltAtlas', atlasPath )
		pageId = 0
		for page in atlas.pages.values():
			pageId += 1
			src = self.getAssetLibrary().getAbsProjectPath( page.source )
			dst = node.getCacheFile( 'pixmap_%d' % pageId )
			node.setObjectFile( 'pixmap_%d' % pageId, dst )
			self._processTexture( src, dst, tex )
			if page.w < 0:
				w, h = getImageSize( dst )
				page.w = w
				page.h = h
		atlas.save( atlas, atlasPath )
		signals.emit( 'texture.rebuild', node )

	def buildSubTexture( self, group, node ):
		node.clearObjectFiles()
		logging.info( 'building sub texture: %s<%s>' % ( node.getPath(), group.name ) )
		node.setObjectFile( 'pixmap', None ) #remove single texture if any
		node.setObjectFile( 'config', node.getCacheFile( 'config' ) )
		jsonHelper.trySaveJSON( groupToJson( group ), node.getAbsObjectFile( 'config' ) )
		signals.emit( 'texture.rebuild', node )	
		
	def postAssetImportAll( self ):
		self.doPendingImports()

	def onAssetUnregister( self, node ):
		t = self.lib.removeTexture( self.lib, node.getNodePath() )
		if t:
			signals.emit( 'texture.remove', t )

	def forceRebuildAllTextures( self ):
		for node in self.getAssetLibrary().enumerateAsset( 'texture' ):
			self.scheduleImport( node )
		self.doPendingImports()

	def forceRebuildTexture( assetNode ):
		self.scheduleImport( assetNode )
		self.doPendingImports()

	def postDeploy( self, context ):
		self.saveIndex()
		context.addFile( self.dataPath, 'asset/texture_index' )
		context.meta['mock_texture_library'] = 'asset/texture_index'

	def onSaveProject( self, prj ):
		self.saveIndex()

##----------------------------------------------------------------##
TextureAssetManager().register()
PrebuiltAtlasAssetManager().register()

TextureLibrary().register()

AssetLibrary.get().setAssetIcon( 'prebuilt_atlas', 'cell' )
