import os.path
from MOAIRuntime import *
from MOAIRuntime import _G, _GII
from gii.core import *

signals.register ( 'script.load'   )
signals.register ( 'script.reload' )
signals.register ( 'script.unload' )

##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path
##----------------------------------------------------------------##

class LuaScriptAssetManager( AssetManager ):
	def getName( self ):
		return 'asset_manager.script'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext = os.path.splitext(filepath)
		return ext in [ '.lua' ]

	def importAsset(self, node, option=None):
		node.assetType = 'lua'
		lib = app.getModule( 'script_library' )
		lib.registerScript( node )
		return True

	def reimportAsset( self, node, option=None):
		return super( LuaScriptAssetManager, self ).reimportAsset( node, option )

	def forgetAsset( self , node ):
		lib = app.getModule( 'script_library' )
		lib.releaseScript( node )

##----------------------------------------------------------------##
class ScriptLibrary( EditorModule ):
	def getName( self ):
		return 'script_library'

	def getDependency( self ):
		return ['moai']

	def onLoad( self ):
		self.scripts = {}

	def convertScriptPath( self, node ):
		path = node.getNodePath()
		name, ext = os.path.splitext( path )
		return name.replace( '/', '.' )

	def registerScript( self, node ):
		_GII.loadGameModule( self.convertScriptPath( node ), True ) #force

	def releaseScript( self, node ):
		_GII.releaseGameModule( self.convertScriptPath( node ) ) #force

	def onStart( self ):
		for node in self.getAssetLibrary().enumerateAsset( 'lua' ):
			_GII.loadGameModule( self.convertScriptPath( node ) )

	def compileScript( self, node, dstPath, version = 'lua' ):
		if version == 'lua':
			pass
		# 'luajit -b -g $in $out'
		# 'luac -o $out $in'


##----------------------------------------------------------------##
ScriptLibrary().register()
LuaScriptAssetManager().register()
