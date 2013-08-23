import os
import os.path
import logging

from gii.core              import *
from gii.moai.MOAIRuntime \
	import \
	MOAIRuntime, MOAILuaDelegate, LuaTableProxy, _G, _LuaTable, _LuaObject



##----------------------------------------------------------------##
_MOCK = LuaTableProxy( None )

_MOCK_GAME_CONFIG_NAME = 'game.json'

def isMockInstance( obj, name ):
	if isinstance( obj, _LuaObject ):
		return  _MOCK.isInstanceOf( obj, _MOCK[name] )
	else:
		return False

def getMockClassName( obj ):
	if isinstance( obj, _LuaTable ):
		clas = obj.__class
		if clas: return clas.__name
	return None
	
##----------------------------------------------------------------##
class MockBridge( EditorModule ):
	
	def getDependency(self):
		return ['moai']

	def getName(self):
		return 'mock'

	def onLoad(self):
		self.affirmConfigFile()
		self.runtime  = self.getManager().affirmModule( 'moai' )

		self.setupLuaModule()		

		signals.connect( 'project.load', self.onProjectLoaded )
		signals.connect( 'moai.reset', self.onMoaiReset )
		signals.connect( 'moai.ready', self.onMoaiReady )


	def affirmConfigFile( self ):
		proj = self.getProject()
		self.configPath = proj.getConfigPath( _MOCK_GAME_CONFIG_NAME )
		indexPath = proj.getRelativePath( self.getAssetLibrary().assetIndexPath )

		if os.path.exists( self.configPath ):
			data = jsonHelper.loadJSON( self.configPath )
			#fix invalid field
			if data.get( 'asset_library', None ) != indexPath: #fix assetlibrary path
				data['asset_library'] = indexPath
				jsonHelper.trySaveJSON( data, self.configPath)
			return
		#create default config
		defaultConfigData = {
			"asset_library": indexPath ,
			"layers" : [
				{ "name" : "default",
					"sort" : "priority_ascending",
					"clear": False
				 },
			]
		}
		jsonHelper.trySaveJSON( defaultConfigData, self.configPath )


	def onStart( self ):
		self.initMockGame()

	def onStop( self ):
		game = _MOCK.game
		#game.saveConfig( game, self.configPath )

	def setupLuaModule( self ):
		self.runtime.runScript( self.getModulePath( 'MockBridge.lua' ) )
		self.runtime.runScript( self.getModulePath( 'ClassManager.lua' ) )
		self.runtime.runScript( self.getModulePath( 'MOAIModels.lua' ) )
		self.runtime.runScript( self.getModulePath( 'Commands.lua' ) )
		#TODO: use lua to handle editor modules
		self.runtime.runScript( self.getModulePath( 'EditorCanvasScene.lua' ) )
		self.runtime.runScript( self.getModulePath( 'EditorCanvasControls.lua' ) )

		_MOCK._setTarget( _G['mock'] )
		_MOCK.setBasePaths( self.getProject().getPath(), self.getProject().getAssetPath() )

	def syncAssetLibrary(self):
		#TODO:
		pass

	def initMockGame( self ):
		_MOCK.init( self.configPath, True )

	def onProjectLoaded(self,prj):
		self.syncAssetLibrary()

	def onMoaiReset(self):		
		self.setupLuaModule()

	def onMoaiReady( self ):
		self.initMockGame()

	def getMockEnv( self ):
		return _MOCK

	def getLuaEnv( self ):
		return _G

	def getComponentTypeList( self ):
		pass

	def getEntityTypeList( self ):
		pass


##----------------------------------------------------------------##	
MockBridge().register()

