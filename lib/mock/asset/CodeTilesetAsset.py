import os.path
import json
import yaml

from gii.core import AssetManager, AssetLibrary, getProjectPath, app, jsonHelper
from helper.psd2tileset import TilesetProject
from DataYAMLAsset import DataYAMLAssetManager

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class CodeTilesetAssetManager(DataYAMLAssetManager):
	def getName(self):
		return 'asset_manager.code_tileset'
	
	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		if not filepath.endswith( '.code_tileset' ): return False
		return True

	def importAsset(self, node, reload = False ):
		imported = super( CodeTilesetAssetManager, self ).importAsset( node, reload )
		node.assetType = 'code_tileset'
		return imported

CodeTilesetAssetManager().register()
AssetLibrary.get().setAssetIcon( 'code_tileset',  'cell' )
