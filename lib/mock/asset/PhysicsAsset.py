import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *
from mock import _MOCK

_PMATERIAL_EXT  = '.pmaterial'
_PMATERIAL_TYPE = 'physics_material'

##----------------------------------------------------------------##
class PhysicsAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.' + _PMATERIAL_TYPE

	def acceptAssetFile(self, filePath):
		if not os.path.isfile( filePath ): return False
		name, ext = os.path.splitext( filePath )
		if not ext in [ _PMATERIAL_EXT ]: return False
		return True

	def importAsset( self, node, reload = False ):
		node.assetType = _PMATERIAL_TYPE
		node.setObjectFile( 'def', node.getFilePath() )
		return True

##----------------------------------------------------------------##
class PhysicsAssetCreator(AssetCreator):
	def getAssetType( self ):
		return _PMATERIAL_TYPE

	def getLabel( self ):
		return 'Physics Material'

	def createAsset( self, name, contextNode, assetType ):
		filename = name + _PMATERIAL_EXT
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		
		_MOCK.createEmptySerialization( fullpath, 'mock.PhysicsMaterial' )
		return nodepath


##----------------------------------------------------------------##
PhysicsAssetManager().register()
PhysicsAssetCreator().register()

AssetLibrary.get().setAssetIcon( 'physics_material',  'crate' )
