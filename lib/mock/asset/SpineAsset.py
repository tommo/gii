import os.path
from gii.core import AssetManager, AssetLibrary, getProjectPath, app

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
		

SpineAssetManager().register()

AssetLibrary.get().setAssetIcon( 'spine', 'clip' )
AssetLibrary.get().setAssetIcon( 'spine_atlas', 'pack' )
