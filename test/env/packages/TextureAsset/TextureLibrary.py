from gii.core import Project,EditorModule
from gii.core import signals
from gii.core import jsonHelper

import logging

_TEXTURE_LIBRARY_INDEX_FILE = 'texture_index.json'

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
		self.config = config or TextureGroup._defaultGroupConfig

		self.atlases = []

##----------------------------------------------------------------##
class TextureLibrary( EditorModule ):
	def __init__( self ):
		self.textureTable = {}
		self.groupTable   = {}

	def getName( self ):
		return 'texture_library'

	def getDependency( self ):
		return []

	def onLoad( self ):
		self.loadIndex()
		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )

	def onUnload( self ):
		self.saveIndex()

	def registerTexture( self, node, group = None ):
		logging.info( 'register texture: ' + node.getPath() )
		self.textureTable[ node.getPath() ] = group or True # default group


	def loadIndex( self ):
		self.groupTable   = {}
		self.textureTable = {}
		indexPath = Project.get().getConfigPath( _TEXTURE_LIBRARY_INDEX_FILE )
		data = jsonHelper.tryLoadJSON( indexPath, 'texture index' ) or {}
		
		logging.info( 'loading texture library index' )

		for gdata in data.get( 'groups', [] ):
			name = gdata['name']
			group = TextureGroup( name , gdata.get('config') )
			self.groupTable[ name ] = group

		for tdata in data.get( 'textures', [] ):
			path  = tdata['path']
			group = tdata['group']
			self.textureTable[ path ] = group

	def saveIndex( self ):
		indexPath = Project.get().getConfigPath( _TEXTURE_LIBRARY_INDEX_FILE )
		logging.info( 'saving texture library index' )
		groupDatas = []
		for k, g in self.groupTable.items():
			gdata = {
				'name'   : g.name,
				'config' : g.config
			}
			groupDatas.append( gdata )

		textureDatas = []
		for path, group in self.textureTable.items():
			tdata = {
				'path'  : path,
				'group' : group
			}
			textureDatas.append( tdata )

		data = {
			'groups'   : groupDatas,
			'textures' : textureDatas,
		}
		jsonHelper.trySaveJSON( data, indexPath, 'texture index' )


	def onAssetRegister( self, node ):
		if not node.isType( 'image' ): return
		meta = node.getMetaData()
		doImport = meta.get( 'import_as_texture', True )
		if not doImport: return
		self.registerTexture( node )

	def onAssetUnregister( self, node ):
		#TODO
		pass
		

TextureLibrary().register()