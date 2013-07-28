import os.path

from gii.core import AssetManager

class ScriptAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.script'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		return ext in ('.py','.lua','.sh')

	def importAsset(self, node, option=None):
		node.assetType = 'script'
		return True

ScriptAssetManager().register()

