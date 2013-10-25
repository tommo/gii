import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *

from TextureProcessor import applyTextureProcessor

##----------------------------------------------------------------##
signals.register( 'texture.add' )
signals.register( 'texture.remove' )
signals.register( 'texture.rebuild' )

##----------------------------------------------------------------##
_TEXTURE_LIBRARY_INDEX_FILE = 'texture_library.json'
_TEXTURE_LIBRARY_DATA_FILE = 'texture_library.data'

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

##----------------------------------------------------------------##
class TextureAssetManager( AssetManager ):
	def getName(self):
		return 'asset_manager.texture'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		return ext in [ '.png', '.psd', '.jpg', '.bmp', '.jpeg' ]

	def importAsset(self, node, reload = False ):
		node.assetType = 'texture'
		group = node.getMetaData( 'group' )
		if not group:
			group = 'default'
			node.setNewMetaData( 'group', group )
		TextureLibrary.get().scheduleImport( node ) #let texture library handle real import
		return True

	def deployAsset( self, node, context ):
		super( TextureAssetManager, self ).deployAsset( node, context )
		texNode = app.getModule( 'texture_library' ).findTextureNode( node )
		group = texNode.parent
		if group.cache and group.atlasMode:
			newPath = context.addFile( group.cache )
			mappedConfigFile = context.getFile( node.getObjectFile('config') )
			context.replaceInFile( context.getPath( mappedConfigFile ), group.cache, newPath )

def _fixPath( path ):
		path = path.replace( '\\', '/' ) #for windows
		if path.startswith('./'): path = path[2:]
		return path	
		
##----------------------------------------------------------------##
def _convertAtlas( inputfile,  srcToAssetDict ):
	f = open( inputfile, 'r' )
	items   = []
	atlases = []
	for line in f.readlines():
		parts       = line.split('\t')
		sourcePath  = _fixPath( parts[1] )
		if sourcePath.startswith('\"'):
			sourcePath = sourcePath[1:-1]		
		# name = os.path.basename( sourcePath )
		assetPath = srcToAssetDict[ sourcePath ]
		atlasName = parts[0]
		if not atlasName in atlases:
			atlases.append( atlasName )
		atlasId = atlases.index( atlasName )
		data = {
			'atlas'  : atlasId,
			'name'   : assetPath,
			'source' : sourcePath,
			'rect'   : [ int(x) for x in parts[2:] ]
		}
		items.append(data)
	output = {
		'atlases' : [ os.path.basename(atlasPath) for atlasPath in atlases ],
		'items'   : items,
	}

	return output


##----------------------------------------------------------------##
class TextureLibrary( EditorModule ):
	_singleton = None
	@staticmethod
	def get():
		return TextureLibrary._singleton

	def __init__( self ):
		assert not TextureLibrary._singleton
		TextureLibrary._singleton = self
		self.groups   = {}
		self.pendingImportGroups = {}
		self.pendingImportTextures = {}

	def getName( self ):
		return 'texture_library'

	def getDependency( self ):
		return ['mock']

	def onLoad( self ):
		self.indexPath = self.getProject().getConfigPath( _TEXTURE_LIBRARY_INDEX_FILE )
		self.dataPath  = self.getProject().getConfigPath( _TEXTURE_LIBRARY_DATA_FILE )
		
		self.delegate  = app.getModule('moai').loadLuaDelegate( _getModulePath('TextureLibrary.lua') )

		if not self.groups.get( 'default' ):
			self.addGroup( 'default' )

		signals.connect( 'asset.post_import_all', self.postAssetImportAll )
		signals.connect( 'asset.unregister',      self.onAssetUnregister )

		signals.connect( 'project.save', self.onSaveProject )

	def onStart( self ):		
		self.loadIndex()		

	def getLibrary( self ):
		return self.lib

	def addGroup( self, name ):
		g = TextureGroup( name )
		if name != 'default':
			default = self.groups['default']
			if default: g.copy( default )
		self.groups[ name ] = g
		return g

	def removeGroup( self, name ):
		if self.groups.has_key( name ):
			del self.groups[ name ]

	def loadIndex( self ):		
		if os.path.exists( self.dataPath ):
			self.lib = self.delegate.call( 'loadLibrary', self.dataPath )
			for group in self.lib.groups.values():
				if group.cache:
					CacheManager.get().touchCacheFile( group.cache )
		else:
			self.lib = self.delegate.call( 'newLibrary' )
			
	def saveIndex( self ):
		logging.info( 'saving texture library index' )
		self.delegate.call( 'saveLibrary', self.dataPath )

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
		pendingImportGroups = set()
		for node, t in pendingImportTextures.items():
			group = t.parent
			self.processTexture( node, t )
			if group.atlasMode:
				pendingImportGroups.add( group )
			else:
				self.buildSingleTexture( t, node )

		for group in pendingImportGroups:
			self.buildAtlas( group )	

	def processTexture( self, assetNode, texNode ):
		logging.info( 'processing texture: %s' % assetNode.getNodePath() )
		assetNode.clearCacheFiles()
		src = assetNode.getAbsFilePath()
		dst = assetNode.getAbsCacheFile( 'pixmap' )
		arglist = [
			'python', 
			_getModulePath( 'tools/PNGConverter.py' ),
			src,
			dst,
			'png' #format
		 ]
		subprocess.call(arglist)
		#apply processor on dst file
		group = texNode.parent
		groupProcessor = group.processor
		if groupProcessor:
			applyTextureProcessor( groupProcessor, dst )
		nodeProcessor = texNode.processor
		if nodeProcessor:
			applyTextureProcessor( nodeProcessor, dst )


	def buildAtlas( self, group ):
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
		for node in nodes:
			path = node.getAbsCacheFile('pixmap')
			srcToAssetDict[ path ] = node.getNodePath()
			sourceList.append( path )

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
			for i in range( 0, len( data['atlases'] ) ):
				src = '%s%d.png' % ( prefix, i )
				dst = '%s/%s%d.png' % ( dstPath, atlasName, i )				
				shutil.copy( src, dst )
			#update texpack
			data[ 'sources' ] = sourceList
			cfgPath = outputDir + '/atlas.json'
			fp = open( cfgPath, 'w' )
			json.dump( data, fp, sort_keys=True, indent=2 )
			fp.close()

		except Exception,e:
			logging.exception( e )
			return False

		group.cache = outputDir
		self.delegate.call( 'releaseTexPack', outputDir )

		#redirect asset node to sub_textures
		for node in nodes:
			self.buildSubTexture( group, node )
		#TODO
		return True

	def buildSingleTexture( self, tex, node ):
		#conversion using external tool (PIL & psd_tools here)
		group = tex.parent
		logging.info( 'building single texture: %s<%s>' % ( node.getPath(), group.name ) )
		node.clearObjectFiles()
		node.setObjectFile( 'pixmap', node.getCacheFile( 'pixmap' ) )
		node.setObjectFile( 'config', node.getCacheFile( 'config' ) )
		jsonHelper.trySaveJSON( groupToJson( group ), node.getAbsObjectFile( 'config' ) )
		signals.emit( 'texture.rebuild', node )
		#todo: check process result!

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
		if node.isType( 'texture' ):
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

	def onSaveProject( self, prj ):
		self.saveIndex()

##----------------------------------------------------------------##
TextureAssetManager().register()
TextureLibrary().register()
