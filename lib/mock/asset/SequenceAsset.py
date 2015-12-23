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
class SequenceAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.sequence'

	def acceptAssetFile( self, filePath ):
		if os.path.isdir(filePath): return False		
		if not filePath.endswith( '.sequence' ): return False
		return True

	def importAsset( self, node, reload = False ):
		node.assetType = 'sequence'
		node.setObjectFile( 'def', node.getFilePath() )
		return True

	def editAsset(self, node):	
		editor = app.getModule( 'sequence_editor' )
		if not editor: 
			return alertMessage( 'Editor not load', 'Asset Editor not found!' )
		else:
			editor.openAsset( node )

SequenceAssetManager().register()
AssetLibrary.get().setAssetIcon( 'sequence',  'story' )
