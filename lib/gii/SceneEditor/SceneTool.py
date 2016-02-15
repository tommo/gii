import os
import weakref

##----------------------------------------------------------------##
from gii.core     import *
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.controls.Menu import MenuManager
from gii.qt.IconCache                  import getIcon

from PyQt4 import QtCore,QtGui


##----------------------------------------------------------------##
class SceneToolMeta( type ):
	def __init__( cls, name, bases, dict ):
		super( SceneToolMeta, cls ).__init__( name, bases, dict )
		fullname = dict.get( 'name', None )
		shortcut = dict.get( 'shortcut', None )
		if not fullname: return
		app.getModule( 'scene_tool_manager' ).registerSceneTool( 
			fullname,
			cls,
			shortcut = shortcut
		 )

##----------------------------------------------------------------##
class SceneTool():
	__metaclass__ = SceneToolMeta

	def __init__( self ):
		self.category = None
		self.lastUseTime = -1

	def getId( self ):
		return 'unknown'

	def getName( self ):
		return 'Tool'

	def getIcon( self ):
		return 'null_thumbnail'

	def __repr__( self ):
		return '%s::%s' % ( repr(self.category), self.getId() )

	def onStart( self, **context ):
		pass

	def onStop( self ):
		pass


##----------------------------------------------------------------##
_SceneToolButtons = weakref.WeakKeyDictionary()

##----------------------------------------------------------------##
class SceneToolButton( QtGui.QToolButton ):
	def __init__( self, toolId, **options ):
		super( SceneToolButton, self ).__init__()
		self.toolId = toolId
		# self.setDown( True )
		iconPath = options.get( 'icon', 'tools/' + toolId )
		self.setIcon( getIcon( iconPath ) )
		_SceneToolButtons[ self ] = toolId
		self.setObjectName( 'SceneToolButton' )

	def mousePressEvent( self, event ):
		if self.isDown(): return;
		super( SceneToolButton, self ).mousePressEvent( event )
		app.getModule( 'scene_tool_manager' ).changeTool( self.toolId )

	def mouseReleaseEvent( self, event ):
		return


##----------------------------------------------------------------##
class SceneToolManager( EditorModule ):
	name = 'scene_tool_manager'
	dependency = [ 'scene_editor', 'mock' ]

	def __init__( self ):				
		#
		self.toolRegistry = {}
		self.currentToolId = None
		self.currentTool  = None
		self.currentAdhoc = False
		self.prevNonAdhocToolId = None

	def onLoad( self ):
		pass

	def onStart( self ):
		#register shortcuts
		for toolId, entry in self.toolRegistry.items():
			clas, options = entry
			shortcut = options.get( 'shortcut', None )
			if shortcut:
				self.addSceneToolShortcut( toolId, shortcut, context = 'main' )

	def registerSceneTool( self, toolId, clas, **options ):
		if self.toolRegistry.has_key( toolId ):
			logging.warning( 'duplicated scene tool id %s' % toolId )
			return
		self.toolRegistry[ toolId ] = ( clas, options )

	def addSceneToolShortcut( self, toolId, shortcut, **kwargs ):
		def shortcutAction():
			return self.changeTool( toolId )
		context = kwargs.get( 'context', 'main' )
		self.getModule( 'scene_editor' ).addShortcut( context, shortcut, shortcutAction )

	def changeTool( self, toolId, **context ):
		if self.currentToolId == toolId : return
		
		if context.get( 'adhoc', False ):
			if not self.currentAdhoc:
				self.prevNonAdhocToolId = self.currentToolId
			self.currentAdhoc = True
		else:
			self.currentAdhoc = False

		toolClas, options = self.toolRegistry.get( toolId, None )
		if not toolClas:
			logging.warning( 'No scene tool found: %s' % toolId )
			return
		toolObj = toolClas()
		toolObj._toolId = toolId

		if self.currentTool:
			self.currentTool.onStop()

		self.currentTool = toolObj
		self.currentToolId = toolId


		toolObj.onStart( **context )

		for button, buttonToolId in _SceneToolButtons.items():
			if buttonToolId == toolId:
				button.setDown( True )
			else:
				button.setDown( False )
		signals.emit( 'scene_tool.change', self.currentToolId )

	def startAdhocTool( self, toolId, **context ):
		context[ 'adhoc' ] = True
		self.changeTool( toolId, **context )

	def stopAdhocTool( self ):
		if self.currentAdhoc:
			self.changeTool( self.prevNonAdhocToolId )

	def isCurrentAdhoc( self ):
		return self.currentAdhoc

	def getCurrentTool( self ):
		return self.currentTool

	def getCurrentToolId( self ):
		return self.currentToolId
