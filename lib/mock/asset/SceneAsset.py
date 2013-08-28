import os.path
import json
from gii.core import *

class SceneAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.scene'

	def acceptAssetFile( self, filePath ):
		if not os.path.isfile(filePath): return False		
		name,ext = os.path.splitext(filePath)
		if not ext in ['.scene']: return False
		data = jsonHelper.tryLoadJSON( filePath )
		return data and data.get( '_assetType', None ) == 'scene'

	def importAsset( self, node, reload = False ):
		node.assetType = 'scene'		
		return True

	def editAsset( self, node ):
		editor = app.getModule( 'scenegraph_editor' )
		if not editor:
			return alertMessage( 'Editor not load', 'Scene Editor not found!' ) 
		editor.openScene( node )

##----------------------------------------------------------------##
class SceneCreator(AssetCreator):
	def getAssetType( self ):
		return 'scene'

	def getLabel( self ):
		return 'Scene'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.scene'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		data={
			'_assetType' : 'scene', #checksum
			'map'     :{},
			'entities':[]
		}
		if os.path.exists(fullpath):
			raise Exception('File already exist:%s'%fullpath)
		fp = open(fullpath,'w')
		json.dump( data, fp, sort_keys=True, indent=2 )
		fp.close()
		return nodepath

##----------------------------------------------------------------##
SceneAssetManager().register()
SceneCreator().register()

AssetLibrary.get().setAssetIcon( 'scene',    'scene' )
