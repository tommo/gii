import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *
from mock import _MOCK

##----------------------------------------------------------------##
class ShaderAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.shader'

	def acceptAssetFile(self, filePath):
		if not os.path.isfile( filePath ): return False
		name, ext = os.path.splitext( filePath )
		if not ext in [ '.shader' ]: return False
		return _MOCK.checkSerializationFile( filePath, 'mock.Shader' )

	def importAsset( self, node, reload = False ):
		node.assetType = 'shader'		
		node.setObjectFile( 'def', node.getFilePath() )
		return True

	# def editAsset(self, node):	
	# 	editor = app.getModule( 'framebuffer_editor' )
	# 	if not editor: 
	# 		return alertMessage( 'Editor not load', 'shader Editor not found!' )
	# 	editor.openAsset( node )	

##----------------------------------------------------------------##
class ShaderAssetCreator(AssetCreator):
	def getAssetType( self ):
		return 'shader'

	def getLabel( self ):
		return 'Shader'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.shader'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		
		_MOCK.createEmptySerialization( fullpath, 'mock.Shader' )
		return nodepath


##----------------------------------------------------------------##
ShaderAssetManager().register()
ShaderAssetCreator().register()

AssetLibrary.get().setAssetIcon( 'shader',  'shader' )
