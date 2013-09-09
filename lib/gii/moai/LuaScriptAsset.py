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

	def importAsset(self, node, reload = False ):
		node.assetType = 'lua'
		if reload:			
			lib = app.getModule( 'script_library' )
			lib.markModified( node )
			return True
		else:
			lib = app.getModule( 'script_library' )
			lib.loadScript( node )
			return True		

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
		self.modifiedScripts = {}

	def convertScriptPath( self, node ):
		path = node.getNodePath()
		name, ext = os.path.splitext( path )
		return name.replace( '/', '.' )

	def markModified( self, node ):
		self.modifiedScripts[ node ] = True

	def isModified( self ):
		if self.modifiedScripts: return True
		return False

	def loadScript( self, node ):
		path = self.convertScriptPath( node )
		if _GII.hasGameModule( path ):
			m, err = _GII.reloadGameModule( path )
		else:
			m, err = _GII.loadGameModule( path ) #force
		if not m:
			for info in err.values():
				logging.error( 'script error <%s>: %s', info.path, info.msg )

	def loadModifiedScript( self ):
		logging.info( 'reloading modified scripts' )
		modified = self.modifiedScripts
		self.modifiedScripts = {}
		for node in modified:
			self.loadScript( node )
			
		signals.emit( 'script.reload' )

	def releaseScript( self, node ):
		_GII.unloadGameModule( self.convertScriptPath( node ) ) #force

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
##----------------------------------------------------------------##

class RemoteCommandReloadScript( RemoteCommand ):
	name = 'reload_script'
	def run( self, *args ):
		app.getAssetLibrary().tryScanProject()
		lib = app.getModule( 'script_library' )
		lib.loadModifiedScript()

