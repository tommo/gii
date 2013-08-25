import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *
from mock import _MOCK

##----------------------------------------------------------------##
class ParticleSystemAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.particle'

	def acceptAssetFile(self, filePath):
		if not os.path.isfile( filePath ): return False
		name, ext = os.path.splitext( filePath )
		if not ext in [ '.particle' ]: return False
		return _MOCK.checkSerializationFile( filePath, 'mock.ParticleSystemConfig' )

	def importAsset( self, node, option = None ):
		node.assetType = 'particle_system'		
		node.setObjectFile( 'def', node.getFilePath() )
		return True

	def editAsset(self, node):	
		editor = app.getModule( 'particle_editor' )
		if not editor: 
			return alertMessage( 'Editor not load', 'Particle Editor not found!' )
		editor.openAsset( node )	

##----------------------------------------------------------------##
class ParticleSystemCreator(AssetCreator):
	def getAssetType( self ):
		return 'particle_system'

	def getLabel( self ):
		return 'Particle System'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.particle'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		
		_MOCK.createEmptySerialization( fullpath, 'mock.ParticleSystemConfig' )
		return nodepath


##----------------------------------------------------------------##
ParticleSystemAssetManager().register()
ParticleSystemCreator().register()

AssetLibrary.get().setAssetIcon( 'particle_system',  'particle' )
