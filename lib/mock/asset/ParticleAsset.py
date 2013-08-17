import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *

##----------------------------------------------------------------##
class ParticleSystemAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.particle'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext = os.path.splitext(filepath)
		return ext in [ '.particle' ]

	def importAsset( self, node, option = None ):
		node.assetType = 'particle_system'		
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
		data={
			'_assetType' : 'particle' #checksum			
		}
		if os.path.exists(fullpath):
			raise Exception('File already exist:%s'%fullpath)
		fp = open(fullpath,'w')
		json.dump( data, fp, sort_keys=True, indent=2 )
		fp.close()
		return nodepath


##----------------------------------------------------------------##
ParticleSystemAssetManager().register()
ParticleSystemCreator().register()

AssetLibrary.get().setAssetIcon( 'particle_system',  'particle' )
