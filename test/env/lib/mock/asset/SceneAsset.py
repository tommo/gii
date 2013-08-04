import os.path
from gii.core import AssetLibrary, AssetManager, getProjectPath

class SceneAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.scene'

	def acceptAssetFile( self, filepath ):
		if not os.path.isfile(filepath): return False		
		name,ext = os.path.splitext(filepath)
		if not ext in ('.scene'): return False
		data = jsonHelper.tryLoadJSON( filePath )
		return data and data.get( '_assetType', None ) == 'scene'

	def importAsset( self, node, option = None ):
		filePath = node.getAbsFilePath()
		name,ext = os.path.splitext(filePath)
		if ext == '.ttf':
			node.assetType='font_ttf'
			node.setObjectFile( 'font', node.getFilePath() )		
		elif ext == '.fnt':
			#TODO: font validation
			node.assetType='font_bmfont'
			node.setObjectFile( 'font', node.getFilePath() )
			#replace texture path inside font file?

		return True

FontAssetManager().register()

AssetLibrary.get().setAssetIcon( 'font_ttf',    'font' )
AssetLibrary.get().setAssetIcon( 'font_bmfont', 'font' )