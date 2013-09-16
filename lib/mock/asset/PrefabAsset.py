import os.path
import json
from gii.core import *

class PrefabAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.prefab'

	def acceptAssetFile( self, filePath ):
		if not os.path.isfile(filePath): return False		
		name,ext = os.path.splitext(filePath)
		if not ext in ['.prefab']: return False
		data = jsonHelper.tryLoadJSON( filePath )
		return data and data.get( '_assetType', None ) == 'prefab'

	def importAsset( self, node, reload = False ):
		node.assetType = 'prefab'		
		return True

	# def editAsset( self, node ):
		# editor = app.getModule( 'scenegraph_editor' )
		# if not editor:
		# 	return alertMessage( 'Editor not load', 'prefab Editor not found!' ) 
		# editor.openScene( node )

##----------------------------------------------------------------##
class PrefabCreator(AssetCreator):
	def getAssetType( self ):
		return 'prefab'

	def getLabel( self ):
		return 'prefab'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.prefab'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		data={
			'_assetType' : 'prefab', #checksum
			'map'     :False,
			'body'    :False #empty
		}
		if os.path.exists(fullpath):
			raise Exception('File already exist:%s'%fullpath)
		fp = open(fullpath,'w')
		json.dump( data, fp, sort_keys=True, indent=2 )
		fp.close()
		return nodepath

##----------------------------------------------------------------##
PrefabAssetManager().register()
PrefabCreator().register()

AssetLibrary.get().setAssetIcon( 'prefab',  'prefab' )
