import os.path
from gii.core import AssetManager, getProjectPath
import subprocess

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

class TextureAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.texture'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		return ext in ( '.texture' )

	def importAsset(self, node, option=None):
		node.assetType='texture'
		meta = node.getMetaData()
		meta['allowPack'] = True
		#conversion using external tool (PIL here)
		pngFile = node.getCacheFile('png')
		arglist = [
			'python', _getModulePath( 'tools/PNGConverter.py' ),
			node.getAbsFilePath(), #input file
			getProjectPath( pngFile ), #output file
			'png' #format
		 ]

		subprocess.call(arglist)
		#todo: check process result!
		node.setObjectFile('tex', pngFile)
		node.saveMetaData()
		return True

TextureAssetManager().register()

