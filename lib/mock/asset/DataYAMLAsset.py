import os.path
import logging
import json
import yaml

from gii.core import AssetManager, AssetLibrary, getProjectPath, app, jsonHelper

##----------------------------------------------------------------##
class DataYAMLAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.data_yaml'
		
	def getMetaType( self ):
		return 'script'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name, ext = os.path.splitext(filepath)
		if not ext in ['.yaml']: return False		
		return True

	def importAsset(self, node, reload = False ):
		try:
			fp = open( node.getAbsFilePath(), 'r' )
			text = fp.read()
			data = yaml.load( text )
		except Exception, e:
			logging.warn( 'failed to parse yaml:%s' % node.getPath() )
			print e
			return False

		cachePath = node.getCacheFile( 'data' )
		if not jsonHelper.trySaveJSON( data, cachePath ):
			logging.warn( 'failed saving yaml data to json: %s' % cachePath )
			return False

		node.assetType = 'data_yaml'
		node.setObjectFile( 'data', cachePath )
		return True

DataYAMLAssetManager().register()
AssetLibrary.get().setAssetIcon( 'data_yaml', 'data' )
