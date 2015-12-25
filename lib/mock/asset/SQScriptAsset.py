import os.path
import subprocess
import shutil

from gii.core import *
from gii.qt.dialogs   import requestString, alertMessage

from mock import _MOCK


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
	
##----------------------------------------------------------------##
class SQScriptAssetCreator(AssetCreator):
	def getAssetType( self ):
		return 'sq_script'

	def getLabel( self ):
		return 'SQScript'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.sq_script'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )

		modelName = _MOCK.Model.findName( 'SQScript' )
		assert( modelName )
		_MOCK.createEmptySerialization( fullpath, modelName )
		return nodepath


##----------------------------------------------------------------##
class SQScriptAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.sq_script'

	def acceptAssetFile( self, filePath ):
		if os.path.isdir(filePath): return False		
		if not filePath.endswith( '.sq_script' ): return False
		return True

	def importAsset( self, node, reload = False ):
		node.assetType = 'sq_script'
		node.setObjectFile( 'data', node.getFilePath() )
		return True

	def editAsset(self, node):	
		editor = app.getModule( 'sq_script_editor' )
		if not editor: 
			return alertMessage( 'Editor not load', 'Asset Editor not found!' )
		else:
			editor.openAsset( node )

SQScriptAssetManager().register()
SQScriptAssetCreator().register()
AssetLibrary.get().setAssetIcon( 'sq_script',  'story' )
