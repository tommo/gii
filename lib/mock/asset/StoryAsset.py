import os.path
import subprocess
import shutil

from gii.core import *

from tools.ml2story import StoryGraphParser

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
	
##----------------------------------------------------------------##
class StoryAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.story'

	def acceptAssetFile( self, filePath ):
		if not os.path.isdir(filePath): return False		
		if not filePath.endswith( '.story' ): return False
		return True

	def importAsset( self, node, reload = False ):
		node.assetType = 'story'
		node.setBundle()
		node.setObjectFile( 'def', node.getCacheFile( 'def' ) )
		parser = StoryGraphParser()
		if parser.parse( node.getAbsFilePath() ):
			outputFile = node.getAbsObjectFile( 'def' )
			parser.saveToJson( outputFile )
			return True
		else:
			return False

StoryAssetManager().register()
AssetLibrary.get().setAssetIcon( 'story',  'story' )
