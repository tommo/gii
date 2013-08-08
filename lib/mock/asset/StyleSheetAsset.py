import os.path
from gii.core import AssetManager, AssetLibrary, AssetCreator, app
import json

##----------------------------------------------------------------##
class StyleSheetAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.stylesheet'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		if not ext in ['.stylesheet']: return False
		#validation 
		try:
			fp = open( filepath, 'r' )
			text = fp.read()
			fp.close()
			data = json.loads( text )
			return data.get( '_assetType', None ) == 'stylesheet'
		except Exception, e:
			pass
		return False

	def importAsset(self, node, option=None):
		node.assetType = 'stylesheet'
		#TODO: sub style?
		return True

	def editAsset(self, node):	
		editor = app.getModule('mock.stylesheet_editor')
		if not editor: 
			return alertMessage( 'Editor not load', 'Style Editor not found!' )
		editor.setFocus()
		editor.startEdit( node )

##----------------------------------------------------------------##
class StyleSheetCreator( AssetCreator ):
	def getAssetType( self ):
		return 'stylesheet'

	def getLabel( self ):
		return 'Style Sheet'

	def createAsset(self, name, contextNode, assetType):
		ext = '.stylesheet'
		filename = name + ext

		if contextNode.isType( 'folder' ):
			nodepath = contextNode.getChildPath(filename)
			print nodepath
		else:
			nodepath = contextNode.getSiblingPath(filename)

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		data={
			'_assetType':'stylesheet', #checksum
			'styles':[]
		}
		print fullpath
		if os.path.exists( fullpath ):
			raise Exception( 'File already exist: %s' % fullpath )
		fp = open( fullpath, 'w' )
		json.dump(data, fp, sort_keys=True,indent=2)
		fp.close()
		return nodepath


##----------------------------------------------------------------##
StyleSheetAssetManager().register()
StyleSheetCreator().register()

AssetLibrary.get().setAssetIcon('stylesheet', 'text')
