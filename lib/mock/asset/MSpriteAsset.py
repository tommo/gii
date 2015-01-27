import os.path
from gii.core import AssetManager, AssetLibrary, getProjectPath, app

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class MSpriteAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.msprite'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		if not filepath.endswith( '.msprite' ): return False
		return True

	def importAsset(self, node, reload = False ):
		# if node.assetType == 'quadlists': return True
		node.assetType = 'msprite'
		node.setObjectFile( 'def', node.getFilePath() )
		# node.createChildNode( 'frames', 'quadlists', manager = self )
		return True

MSpriteAssetManager().register()

AssetLibrary.get().setAssetIcon( 'animclip',   'clip' )
AssetLibrary.get().setAssetIcon( 'quadlists',  'cell' )
AssetLibrary.get().setAssetIcon( 'msprite',    'clip' )
