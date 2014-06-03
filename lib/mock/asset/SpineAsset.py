import os.path
from gii.core import *
import logging

from ImageHelpers import convertToPNG, convertToWebP, getImageSize
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
				skelPath = node.getCacheFile( 'skel' )
				node.setObjectFile( 'skel', skelPath )
				self._optimizeAnimation( fullPath, skelPath )				

			elif ext == '.atlas':
				internalAtlas = _MOCK.convertSpineAtlasToPrebuiltAtlas( fullPath )
				for page in internalAtlas.pages.values():
					page.source = filePath + '/' + page.texture
				atlasNode = node.affirmChildNode( node.getBaseName()+'_spine_atlas', 'prebuilt_atlas', manager = 'asset_manager.prebuilt_atlas' )
				atlasCachePath = atlasNode.getCacheFile( 'atlas' )
				atlasNode.setObjectFile( 'atlas', atlasCachePath )
				internalAtlas.save( internalAtlas, atlasCachePath )
				app.getModule( 'texture_library' ).scheduleImport( atlasNode )
				
		return True

	def getPriority(self):
		return 10

	def _optimizeAnimation( self, inputPath, outputPath ):
		data = jsonHelper.tryLoadJSON( inputPath )
		#todo: optimization		
		jsonHelper.trySaveJSON( data, outputPath )

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
