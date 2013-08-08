from gii.core              import *
from gii.moai.MOAIRuntime \
	import \
	MOAIRuntime, MOAILuaDelegate, LuaTableProxy, _G, _LuaTable, _LuaObject


##----------------------------------------------------------------##
_MOCK = LuaTableProxy( None )

def isMockInstance( obj, name ):
	if isinstance( obj, _LuaObject ):
		return  _MOCK.isInstanceOf( obj, _MOCK[name] )
	else:
		return False

##----------------------------------------------------------------##
class MockBridge( EditorModule ):
	
	def getDependency(self):
		return ['moai']

	def getName(self):
		return 'mock'

	def onLoad(self):
		self.runtime  = self.getManager().affirmModule( 'moai' )
		self.delegate = MOAILuaDelegate( self )

		_G['MOCK_ASSET_LIBRARY_INDEX'] = self.getAssetLibrary().assetIndexPath
		self.delegate.load( self.getModulePath( 'MockBridge.lua' ) )

		_MOCK._setTarget( _G['mock'] )
		_MOCK.setBasePaths( self.getProject().getPath(), self.getProject().getAssetPath() )

		signals.connect( 'project.load', self.onProjectLoaded )
		signals.connect( 'moai.reset', self.onMoaiReset )
		

	def onStart( self ):
		pass

	def syncAssetLibrary(self):
		self.delegate.safeCall( 'syncAssetLibrary' )

	def onProjectLoaded(self,prj):
		self.syncAssetLibrary()

	def onMoaiReset(self):		
		_MOCK._setTarget( _G['mock'] )

	def getMockEnv( self ):
		return _MOCK

	def getLuaEnv( self ):
		return _G

##----------------------------------------------------------------##	
MockBridge().register()


