import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                   import getIcon
from gii.qt.controls.GenericTreeWidget  import GenericTreeWidget
from gii.qt.controls.Timeline.CurveView import CurveView
from gii.qt.controls.Timeline.TimelineView import TimelineView
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule, getSceneSelectionManager
from gii.qt.helpers       import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

def _fixDuplicatedName( names, name, id = None ):
	if id:
		testName = name + '_%d' % id
	else:
		id = 0
		testName = name
	#find duplicated name
	if testName in names:
		return _fixDuplicatedName( names, name, id + 1)
	else:
		return testName


##----------------------------------------------------------------##
class AnimatorView( SceneEditorModule ):
	name = 'animator'
	dependency = [ 'scene_editor' ]
	def onLoad( self ):
		#UI
		self.windowTitle = 'Animator'
		self.window = self.requestDockWindow( 'AnimatorView',
			title     = 'Animator',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'bottom'
			)

		#
		# self.delegate = MOAILuaDelegate( self )
		# self.delegate.load( _getModulePath( 'AnimatorView.lua' ) )
		self.tool = self.addToolBar( 'animator', self.window.addToolBar() )
		self.window.addWidget( TimelineView() )
		
		self.addTool( 'animator/add',    label = 'add',    icon = 'add' )
		self.addTool( 'animator/remove', label = 'remove', icon = 'remove' )
		self.addTool( 'animator/up',     label = 'up',     icon = 'arrow-up' )
		self.addTool( 'animator/down',   label = 'down',   icon = 'arrow-down' )
		
		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )

	def onStart( self ):
		print '...'
		pass

	def onMoaiClean( self ):
		self.tree.clear()

	def onTool( self, tool ):
		name = tool.name
		if name == 'add':
			layer = self.delegate.safeCall( 'addLayer' )
			self.tree.addNode( layer )
			self.tree.editNode( layer )
			self.tree.selectNode( layer )
			
		elif name == 'remove':
			for l in self.tree.getSelection():
				self.delegate.safeCall( 'removeLayer', l )
				self.tree.removeNode( l )
		elif name == 'up':
			for l in self.tree.getSelection():
				self.delegate.safeCall( 'moveLayerUp', l )
				self.tree.rebuild()
				self.tree.selectNode( l )
				break
		elif name == 'down':
			for l in self.tree.getSelection():
				self.delegate.safeCall( 'moveLayerDown', l )		
				self.tree.rebuild()
				self.tree.selectNode( l )
				break

