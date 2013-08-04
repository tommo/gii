import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *

##----------------------------------------------------------------##
_TEXTURE_LIBRARY_INDEX_FILE = 'texture_library.json'

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
class TextureAssetManager( AssetManager ):
	def getName(self):
		return 'asset_manager.texture'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		return ext in ( '.png', '.psd', '.jpg', '.bmp', '.jpeg' )

	def importAsset(self, node, option=None):
		node.assetType = 'texture'
		group = node.getMetaData( 'group' )
		if not group:
			group = 'default'
			node.setNewMetaData( 'group', group )
		TextureLibrary.get().pendImport( node ) #let texture library handle real import
		return True

	
##----------------------------------------------------------------##
def _convertAtlas( inputfile,  basepath ):
	f = open( inputfile, 'r' )
	items   = []
	atlases = []
	for line in f.readlines():
		parts = line.split('\t')
		path  = parts[1]
		if path.startswith('\"'):
			path = path[1:-1]
		path = os.path.relpath( path, basepath )
		name = os.path.basename( path )
		name = path
		atlasName = parts[0]
		if not atlasName in atlases:
			atlases.append( atlasName )
		atlasId = atlases.index( atlasName )
		data = {
			'atlas'  : atlasId,
			'name'   : name,
			'source' : path,
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

	def getName( self ):
		return 'texture_library'

	def getDependency( self ):
		return ['mock']

	def onLoad( self ):
		self.indexPath = self.getProject().getConfigPath( _TEXTURE_LIBRARY_INDEX_FILE )
		self.loadIndex()
		if not self.groups.get( 'default' ):
			self.addGroup( 'default' )

		_G = self.getModule( 'mock' ).getLuaEnv()
		_G['MOCK_TEXTURE_LIBRARY_INDEX'] = self.indexPath
		signals.connect( 'asset.post_import_all', self.postAssetImportAll )
		signals.connect( 'project.save', self.onSaveProject )
	
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

	def getGroup( self, name ):
		return self.groups.get( name, None )

	def loadIndex( self ):
		self.groups   = {}
		self.textureTable = {}
		indexPath = self.indexPath
		data = jsonHelper.tryLoadJSON( indexPath, 'texture index' ) or {}
		
		logging.info( 'loading texture library index' )
		groups = data.get( 'groups' )
		if groups:
			for name, gdata in groups.items():
				g = TextureGroup( name )
				g.fromJson( gdata )				
				if g.cache:
					CacheManager.get().touchCacheFile( g.cache )
				self.groups[ name ] = g
			
	def saveIndex( self ):
		logging.info( 'saving texture library index' )
		groupDatas = {}
		for k, g in self.groups.items():			
			groupDatas[ g.name ] = g.toJson()

		data = {
			'groups' : groupDatas,
		}
		jsonHelper.trySaveJSON( data, self.indexPath, 'texture index' )

	def pendImport( self, node ):
		groupName = node.getMetaData( 'group' )
		group = self.getGroup( groupName )
		n = self.pendingImportGroups.get( group )
		if not n:
			n = {}
			self.pendingImportGroups[ group ] = n
		n[ node ] = True
		
	def doPendingImports( self ):
		pendingImportGroups = self.pendingImportGroups
		self.pendingImportGroups = {}
		for group, nodes in pendingImportGroups.items():
			if group.atlas_allowed and group.wrapmode != 'wrap':
				#atlas
				self.buildAtlas( group, nodes )
			else:
				for node in nodes:
					self.buildSingleTexture( group, node )

	def buildAtlas( self, group, nodes ):
		logging.info( 'building atlas texture:' + group.name )
		#packing atlas
		sourceList = [ node.getAbsFilePath() for node in nodes ]
		atlasName = 'atlas_' + group.name

		tmpDir = CacheManager.get().getTempDir()
		prefix = tmpDir( atlasName )

		outputDir = CacheManager.get().getCacheDir( '<texture_group>/' + group.name  )
		
		arglist = [ 'python', _getModulePath('tools/AtlasGenerator.py'), '--prefix', prefix ]
		arglist += [ '1024', '1024' ]
		arglist += sourceList
		try:
			ex = subprocess.call( arglist ) #run packer
			#conversion
			srcFile = prefix + '.txt'
			data    = _convertAtlas( srcFile,  self.getProject().getAssetPath() )
			dstPath = outputDir
			#copy generated atlas
			for i in range( 0, len( data['atlases'] ) ):
				src = '%s%d.png' % ( prefix, i )
				dst = '%s/%s%d.png' % ( dstPath, atlasName, i )
				print( src, dst )
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

		#redirect asset node to sub_textures
		for node in nodes:
			self.buildSubTexture( group, node )
		#TODO
		return True

	def buildSingleTexture( self, group, node ):
		#conversion using external tool (PIL & psd_tools here)
		logging.info( 'building single texture: %s<%s>' % ( node.getPath(), group.name ) )
		compression = group.compression

		node.setObjectFile( 'pixmap', node.getCacheFile( 'pixmap' ) )
		arglist = [
			'python', 
			_getModulePath( 'tools/PNGConverter.py' ),
			node.getAbsFilePath(), #input file
			node.getAbsObjectFile( 'pixmap' ), #output file
			'png' #format
		 ]
		subprocess.call(arglist)
		node.setObjectFile( 'config', node.getCacheFile( 'config' ) )
		jsonHelper.trySaveJSON( group.toJson(), node.getAbsObjectFile( 'config' ) )
		#todo: check process result!

	def buildSubTexture( self, group, node ):
		node.setObjectFile( 'config', node.getCacheFile( 'config' ) )
		jsonHelper.trySaveJSON( group.toJson(), node.getAbsObjectFile( 'config' ) )

	def postAssetImportAll( self ):
		self.doPendingImports()

	def onSaveProject( self, prj ):
		self.saveIndex()

##----------------------------------------------------------------##
TextureAssetManager().register()
TextureLibrary().register()
