import os.path
import re
import logging
from gii.core import AssetLibrary, AssetManager, getProjectPath

def getFntTexture( path ):
	fp = open( path, 'r' )
	txt = fp.read()
	fp.close()
	pattern = re.compile('page id=\w+ file="(\w+(\.\w+)?)"')
	result = []
	for mo in pattern.finditer( txt ):
		filename = mo.group( 1 )
		result.append( filename )
	return result

class FontAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.font'

	def acceptAssetFile( self, filepath ):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		return ext in ['.ttf','.fnt','.bdf', '.otf']

	def importAsset( self, node, reload = False ):
		filePath = node.getAbsFilePath()
		name,ext = os.path.splitext(filePath)
		if ext == '.ttf' or ext == '.otf':
			node.assetType='font_ttf'
			node.setObjectFile( 'font', node.getFilePath() )		
		elif ext == '.fnt':
			#TODO: font validation
			node.assetType='font_bmfont'
			node.setObjectFile( 'font', node.getFilePath() )
			base = os.path.dirname( node.getNodePath() )
			lib = AssetLibrary.get()
			n = 0
			for tex in getFntTexture( filePath ):
				texPath = base + '/' + tex
				texNode = lib.getAssetNode( texPath )
				if not texNode:
					logging.warn( 'BMFont texture not found: ' + texPath )
					continue
				n += 1
				depName = 'tex-%d' % n
				node.addDependency( depName, texNode )
		return True

FontAssetManager().register()

AssetLibrary.get().setAssetIcon( 'font_ttf',    'font' )
AssetLibrary.get().setAssetIcon( 'font_bmfont', 'font' )