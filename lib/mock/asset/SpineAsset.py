import os.path
from gii.core import AssetManager, AssetLibrary, getProjectPath, app
import logging

from ImageHelpers import convertToWebP
from mock import _MOCK

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class SpineAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.spine'

	def acceptAssetFile(self, filepath):
		if not os.path.isdir(filepath): return False
		if not filepath.endswith( '.spine' ): return False
		return True

	def importAsset(self, node, reload = False ):
		if not node.assetType in [ 'folder', 'spine' ] : return True
		node.assetType = 'spine'
		node.setBundle()
		filePath = node.getFilePath()
		nodePath = node.getNodePath()
		for fileName in os.listdir( node.getAbsFilePath() ):
			fullPath = filePath + '/' + fileName
			name, ext = os.path.splitext( fileName )
			if ext == '.json':
				node.setObjectFile( 'json', fullPath )
			elif ext == '.atlas':
				node.setObjectFile( 'atlas', fullPath )
				jsonPath = node.getCacheFile( 'atlas_json' )
				_MOCK.convertSpineAtlasToJson( fullPath, jsonPath )
				node.setObjectFile( 'atlas_json', jsonPath )
				
		return True

	def getPriority(self):
		return 10

	def optimizeAnimation( self, node ):
		pass

	def deployAsset( self, node, context ):
		super( SpineAssetManager, self ).deployAsset( node, context )
		if not node.isType( 'spine' ): return
		#replace texture		
		try:
			absAtlasPath = node.getAbsObjectFile('atlas')
			fp = open( absAtlasPath )
			nextLineTexture = False
			textures = []
			for line in fp:
				if nextLineTexture:
					textureName = line.strip()
					textures.append( textureName )
					nextLineTexture = False
				elif line.strip() == '':
					nextLineTexture = True
			fp.close()
			for textureName in textures:
				texturePath = node.getAbsFilePath() + '/' + textureName
				if os.path.exists( texturePath ):
					newPath   = context.addFile( texturePath )
					exportedAtlasPath = context.getAbsFile( node.getObjectFile( 'atlas' ) )
					context.replaceInFile( exportedAtlasPath, textureName, os.path.basename( newPath ) )
					#webp conversion
					fn = context.getAbsFile( texturePath )
					if context.isNewFile( fn ):
						convertToWebP( fn )
		except Exception, e:
			logging.exception( e )
		

SpineAssetManager().register()

AssetLibrary.get().setAssetIcon( 'spine', 'clip' )
AssetLibrary.get().setAssetIcon( 'spine_atlas', 'pack' )
