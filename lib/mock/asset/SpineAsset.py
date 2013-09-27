import os.path
from gii.core import AssetManager, AssetLibrary, getProjectPath, app
import logging
##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class SpineAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.spine'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False
		if not filepath.endswith( '.spine.json' ): return False
		return True

	def importAsset(self, node, reload = False ):
		node.assetType = 'spine'
		node.setObjectFile( 'json', node.getFilePath() )

		#TODO
		#search bundled atlas  
		baseName, ext = os.path.splitext( node.getNodePath() )
		atlasPath   = baseName + '.atlas'
		atlasNode = app.getAssetLibrary().getAssetNode( atlasPath )
		
		if atlasNode:
			node.addDependencyR( atlasNode )
			atlasNode.setManager( self )
			atlasNode.assetType = 'spine_atlas'
			node.setObjectFile( 'atlas', atlasNode.getFilePath() )

		return True

	def deployAsset( self, node, context ):
		super( SpineAssetManager, self ).deployAsset( node, context )
		if not node.isType( 'spine' ): return
		#replace texture		
		try:
			absAtlasPath = node.getAbsObjectFile('atlas')
			fp = file( absAtlasPath )
			fp.readline()
			textureName = fp.readline().strip()
			fp.close()
			texturePath = os.path.dirname( node.getAbsFilePath() ) + '/' + textureName
			if os.path.exists( texturePath ):
				newPath   = context.addFile( texturePath )
				exportedAtlasPath = context.getAbsFile( node.getObjectFile( 'atlas' ) )
				context.replaceInFile( exportedAtlasPath, textureName, os.path.basename( newPath ) )
		except Exception, e:
			logging.exception( e )
		

SpineAssetManager().register()

AssetLibrary.get().setAssetIcon( 'spine', 'clip' )
AssetLibrary.get().setAssetIcon( 'spine_atlas', 'pack' )
