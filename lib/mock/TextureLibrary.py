from gii.core import Project,EditorModule
from gii.core import signals
from gii.core import jsonHelper

import logging

##----------------------------------------------------------------##
_TEXTURE_LIBRARY_INDEX_FILE = 'texture_index.json'

class TextureItem( object ):
	def __init__( self, path, group ):
		self.path      = path
		self.group     = group
		self.imported  = None
		self.atlas     = None
		self.width     = 0
		self.height    = 0  

	def doImport( self, path ):
		pass

	def __repr__( self ):
		return '%s <%s>' % ( self.path, self.group )

##----------------------------------------------------------------##
class TextureGroup( object ):
	_defaultGroupConfig = {
			'filter'            : 'nearest',
			'compression'       : None,
			'mipmap'            : False,
			'wrapmode'          : 'clamp',
			'atlas_allowed'     : True,
			'atlas_max_width'   : 1024,
			'atlas_max_height'  : 1024,
			'atlas_force_single': False
		}

	def __init__( self, name, config = None ):
		self.name = name
		self.config = config or TextureGroup._defaultGroupConfig.copy()
		self.atlases = []

##----------------------------------------------------------------##
class TextureLibrary( EditorModule ):
	def __init__( self ):
		self.textureTable = {}
		self.groupTable   = {}
		self.defaultGroup = TextureGroup( '<DEFAULT>' )

	def getName( self ):
		return 'texture_library'

	def getDependency( self ):
		return ['mock']

	def onLoad( self ):
		self.indexPath = self.getProject().getConfigPath( _TEXTURE_LIBRARY_INDEX_FILE )
		self.loadIndex()
		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )
		_G = self.getModule('mock').getLuaEnv()
		_G['MOCK_TEXTURE_LIBRARY_INDEX'] = self.indexPath

	def onUnload( self ):
		self.saveIndex()

	def addGroup( self, name ):
		g = TextureGroup( name )
		self.groupTable[ name ] = g
		return g

	def registerTexture( self, node, group = None ):
		logging.info( 'register texture: ' + node.getPath() )
		item = TextureItem( node.getPath(), group or True )
		self.textureTable[ node.getPath() ] = item

	def loadIndex( self ):
		self.groupTable   = {}
		self.textureTable = {}
		indexPath = self.indexPath
		data = jsonHelper.tryLoadJSON( indexPath, 'texture index' ) or {}
		
		logging.info( 'loading texture library index' )

		for gdata in data.get( 'groups', [] ):
			name = gdata['name']
			group = TextureGroup( name , gdata.get('config') )
			self.groupTable[ name ] = group

		for tdata in data.get( 'textures', [] ):
			path  = tdata['path']
			group = tdata['group']
			item  = TextureItem( path, group )
			self.textureTable[ path ] = item

	def saveIndex( self ):
		logging.info( 'saving texture library index' )
		groupDatas = []
		for k, g in self.groupTable.items():
			gdata = {
				'name'   : g.name,
				'config' : g.config
			}
			groupDatas.append( gdata )

		textureDatas = []
		for path, t in self.textureTable.items():
			tdata = {
				'path'     : t.path,
				'group'    : t.group,
				'imported' : t.imported
			}
			textureDatas.append( tdata )

		data = {
			'groups'   : groupDatas,
			'textures' : textureDatas,
		}
		jsonHelper.trySaveJSON( data, self.indexPath, 'texture index' )

	def scanAssetLibrary( self ):
		pass

	def onAssetRegister( self, node ):
		if not node.isType( 'image' ): return
		if not node.getMetaData( 'import_as_texture', True ): return
		self.registerTexture( node )

	def onAssetUnregister( self, node ):
		#TODO
		pass

TextureLibrary().register()
