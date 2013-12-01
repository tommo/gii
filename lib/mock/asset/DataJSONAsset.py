import os.path
import logging
import json

from gii.core import AssetManager, AssetLibrary, getProjectPath, app

##----------------------------------------------------------------##
class DataJSONAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.data_json'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name, ext = os.path.splitext(filepath)
		if not ext in ['.json']: return False
		try:
			fp = open( filepath, 'r' )
			text = fp.read()
			json.loads( text )
		except Exception, e:
			return False
		return True

	def importAsset(self, node, reload = False ):
		node.assetType = 'data_json'
		node.setObjectFile( 'data', node.getFilePath() )
		return True

DataJSONAssetManager().register()
AssetLibrary.get().setAssetIcon( 'data_json', 'data' )
