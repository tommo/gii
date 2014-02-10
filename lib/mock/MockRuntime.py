import os
import os.path
import logging
import json

from gii.core              import *
from gii.moai.MOAIRuntime \
	import \
	MOAIRuntime, MOAILuaDelegate, LuaTableProxy, _G, _LuaTable, _LuaObject


signals.register ( 'mock.init' )
##----------------------------------------------------------------##
_MOCK = LuaTableProxy( None )

_MOCK_GAME_CONFIG_NAME = 'game_config.json'

def isMockInstance( obj, name ):
	if isinstance( obj, _LuaObject ):
		return  _MOCK.isInstance( obj, _MOCK[name] )
	else:
		return False

def getMockClassName( obj ):
	if isinstance( obj, _LuaTable ):
		clas = obj.__class
		if clas: return clas.__name
	return None
	
##----------------------------------------------------------------##
class MockRuntime( EditorModule ):
	
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

		signals.connect( 'project.post_deploy', self.post_deploy )
		signals.connect( 'project.save', self.onProjectSave )


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

	def post_deploy( self, context ):
		configPath = context.getPath( 'game_config' )
		game = _MOCK.game
		data = json.loads( game.saveConfigToString( game ) )
		data['asset_library']  = 'asset/asset_index'
		data['script_library'] = context.meta.get( 'mock_script_library', False )
		data['scenes']         = context.meta.get( 'mock_scenes', False )
		data['entry_scene']    = context.meta.get( 'mock_entry_scene', False )
		jsonHelper.trySaveJSON( data, configPath, 'deploy game info' )

	def setupLuaModule( self ):
		self.runtime.requireModule( 'mock_edit' )
		_MOCK._setTarget( _G['mock'] )
		_MOCK.setBasePaths( self.getProject().getPath(), self.getProject().getAssetPath() )

	def syncAssetLibrary(self):
		#TODO:
		pass

	def initMockGame( self ):
		try:
			self.runtime.changeRenderContext( 'game', 100, 100 )
			_MOCK.init( self.configPath, True )
			signals.emit( 'mock.init' )
		except Exception, e:
			raise e

	def onProjectLoaded(self,prj):
		self.syncAssetLibrary()

	def onProjectSave( self, prj ):
		game = _MOCK.game
		game.saveConfigToFile( game, self.configPath )

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
MockRuntime().register()

