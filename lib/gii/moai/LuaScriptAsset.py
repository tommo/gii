import os.path
from MOAIRuntime import *
from gii.core import *

class LuaScriptAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.script'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext = os.path.splitext(filepath)
		return ext in [ '.lua' ]

	def importAsset(self, node, option=None):
		node.assetType = 'lua'
		return True

	def reimportAsset( self, node, option=None):
		#TODO
		return super( LuaScriptAssetManager, self ).reimportAsset( node, option )

##----------------------------------------------------------------##
class ScriptLibrary( EditorModule ):
	def getName( self ):
		return 'script_library'

	def getDependency( self ):
		return ['moai']

	def onLoad( self ):
		self.delegate = MOAILuaDelegate( self )
		self.getApp().getPath( 'data/lua/runtime.lua' )

	def compileScripts( self ):
		pass


##----------------------------------------------------------------##
ScriptLibrary().register()
LuaScriptAssetManager().register()
