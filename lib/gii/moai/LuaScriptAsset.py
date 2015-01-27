import os.path
import subprocess
import hashlib

from MOAIRuntime import *
from MOAIRuntime import _G, _GII
from gii.core import *

##--------------------------------------------##
signals.register ( 'script.load'   )
signals.register ( 'script.reload' )
signals.register ( 'script.unload' )

##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
def _hashPath( path ):
	name, ext = os.path.splitext( os.path.basename( path ) )
	m = hashlib.md5()
	m.update( path.encode('utf-8') )
	return m.hexdigest()

def _convertToGameModuleName( path ):
	body, ext = os.path.splitext( path )
	return body.replace( '/', '.' )

##----------------------------------------------------------------##
_GII_SCRIPT_LIBRARY_EXPORT_NAME = 'script_library'

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

	def deployAsset( self, node, context ):
		pass

	def getMetaType( self ):
		return 'script'

##----------------------------------------------------------------##
class ScriptLibrary( EditorModule ):
	def getName( self ):
		return 'script_library'

	def getDependency( self ):
		return ['moai']

	def onLoad( self ):
		self.scripts = {}
		self.modifiedScripts = {}
		signals.connect( 'project.deploy', self.onDeploy )

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
		if _GII.GameModule.hasGameModule( path ):
			m, err = _GII.GameModule.reloadGameModule( path )
		else:
			m, err = _GII.GameModule.loadGameModule( path ) #force
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
		_GII.GameModule.unloadGameModule( self.convertScriptPath( node ) ) #force

	def onStart( self ):
		for node in self.getAssetLibrary().enumerateAsset( 'lua' ):
			_GII.GameModule.loadGameModule( self.convertScriptPath( node ) )

	def onDeploy( self, context ):
		version = context.meta.get( 'lua_version', 'lua' )
		exportIndex = {}
		for node in self.getAssetLibrary().enumerateAsset( 'lua' ):
			hashed = _hashPath( node.getFilePath() )
			dstPath = context.getAssetPath( hashed )
			# self.compileScript( node, dstPath, 'lua' )
			context._copyFile( node.getAbsFilePath(), dstPath )
			exportIndex[ _convertToGameModuleName( node.getNodePath() ) ] = 'asset/' + hashed

		jsonHelper.trySaveJSON(
				exportIndex, 
				context.getAssetPath( _GII_SCRIPT_LIBRARY_EXPORT_NAME ), 
				'script index' 
			)
		context.meta['mock_script_library'] = 'asset/' + _GII_SCRIPT_LIBRARY_EXPORT_NAME

	def compileScript( self, node, dstPath, version = 'luajit' ):
		# version = 'luajit'
		version = 'lua'
		if version == 'lua':
			_GII.GameModule.compilePlainLua( node.getAbsFilePath(), dstPath ) #lua version problem			
			#TODO: error handle
		elif version == 'luajit':
			# 'luajit -b -g $in $out'
			arglist =  [ 'luajit' ]
			arglist += [ '-b', '-g' ]
			arglist += [ node.getAbsFilePath(), dstPath ]
			try:
				code = subprocess.call( arglist )
			except Exception, e:
				raise Exception( 'error on luajit compliation: %s ' % e )

		else:
			raise Exception( 'unknown lua version %s' % version )

##----------------------------------------------------------------##
ScriptLibrary().register()
LuaScriptAssetManager().register()
##----------------------------------------------------------------##

class RemoteCommandReloadScript( RemoteCommand ):
	name = 'reload_script'
	def run( self, *args ):
		app.getAssetLibrary().scheduleScanProject()
		app.getAssetLibrary().tryScanProject()
		lib = app.getModule( 'script_library' )
		lib.loadModifiedScript()

