import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *
from mock import _MOCK

##----------------------------------------------------------------##
class FrameBufferAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.framebuffer'

	def acceptAssetFile(self, filePath):
		if not os.path.isfile( filePath ): return False
		name, ext = os.path.splitext( filePath )
		if not ext in [ '.framebuffer' ]: return False
		return _MOCK.checkSerializationFile( filePath, 'mock.FrameBuffer' )

	def importAsset( self, node, reload = False ):
		node.assetType = 'framebuffer'		
		node.setObjectFile( 'def', node.getFilePath() )
		return True

	# def editAsset(self, node):	
	# 	editor = app.getModule( 'framebuffer_editor' )
	# 	if not editor: 
	# 		return alertMessage( 'Editor not load', 'framebuffer Editor not found!' )
	# 	editor.openAsset( node )	

##----------------------------------------------------------------##
class FrameBufferCreator(AssetCreator):
	def getAssetType( self ):
		return 'framebuffer'

	def getLabel( self ):
		return 'FrameBuffer'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.framebuffer'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		
		_MOCK.createEmptySerialization( fullpath, 'mock.FrameBuffer' )
		return nodepath


##----------------------------------------------------------------##
FrameBufferAssetManager().register()
FrameBufferCreator().register()

AssetLibrary.get().setAssetIcon( 'framebuffer',  'framebuffer' )