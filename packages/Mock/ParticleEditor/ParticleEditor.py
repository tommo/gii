import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *

from gii.qt           import *
from gii.qt.IconCache import getIcon
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget

from gii.qt.controls.PropertyEditor  import PropertyEditor

from gii.AssetEditor  import AssetEditorModule

from gii.moai.MOAIEditCanvas import MOAIEditCanvas
from gii.moai import _LuaObject

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from mock import getMockClassName
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
class Box(object):
	def __init__(self):
		self.items = []


##----------------------------------------------------------------##

class ParticleEditor( AssetEditorModule ):
	"""docstring for ParticleEditor"""
	def __init__(self):
		super(ParticleEditor, self).__init__()
		self.editingAsset  = None		
		self.editingConfig = None
		self.editingState  = None

		self.emitters = Box()
		self.emitters.items=[]
		
		self.states = Box()
		self.states.items=[]
		self.scriptModifyFlag = 0
	
	def getName(self):
		return 'particle_editor'

	def getDependency(self):
		return [ 'qt', 'mock' ]

	def onLoad(self):
		self.windowTitle = 'Particle System Editor'
		self.container = self.requestDocumentWindow('MockParticleEditor',
				title       = 'Particle System Editor',
				size        = (500,300),
				minSize     = (500,300),
				# allowDock = False
			)

		self.tool = self.addToolBar( 'particle_editor', self.container.addToolBar() )
		self.addTool( 'particle_editor/save',   label = 'Save', icon = 'save' )
		self.addTool( 'particle_editor/----' )
		self.addTool( 'particle_editor/add_state',   label = '+ State' )
		self.addTool( 'particle_editor/add_emitter', label = '+ Emitter' )
		self.addTool( 'particle_editor/remove',      label = 'Delete', icon = 'remove' )
		self.addTool( 'particle_editor/update',      label = 'Update', icon = 'refresh' )
		self.addTool( 'particle_editor/----' )
		self.addTool( 'particle_editor/start_preview', icon = 'play' )
		self.addTool( 'particle_editor/stop_preview', icon = 'stop' )

		
		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('ParticleEditor2.ui')
		)
		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas( window.containerPreview )
		)
		self.tree = addWidgetWithLayout(
			ParticleTreeWidget( window.containerTree, multiple_selection = False, editable = False )
			)
		self.tree.module = self

		self.propEditor = addWidgetWithLayout(
			PropertyEditor( window.containerProperty )
			)

		window.textScriptRender.textChanged.connect( self.onScriptModified )
		window.textScriptInit.textChanged.connect( self.onScriptModified )
		self.window.panelScript.setEnabled( False )

		self.propEditor.propertyChanged.connect( self.onPropertyChanged )

	def onStart( self ):
		self.canvas.loadScript( _getModulePath('ParticleEditor.lua') )
		# self.canvas.setDelegateEnv( 'editor', self )

	def onSetFocus( self ):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def openAsset( self, node ):
		self.setFocus()
		if self.editingAsset == node: return
		self.checkScriptTimer = self.container.startTimer( 3, self.checkScript )
		
		self.container.setDocumentName( node.getNodePath() )
		self.editingAsset  = node

		self.canvas.makeCurrent()
		self.editingConfig = self.canvas.safeCallMethod( 'preview', 'open', node.getPath() )
		
		self.tree.rebuild()
		self.tree.setAllExpanded( True )

	def saveAsset( self ):
		if not self.editingAsset: return
		self.canvas.safeCallMethod( 'preview', 'save', self.editingAsset.getAbsFilePath() )

	def closeAsset( self ):
		self.checkScriptTimer.stop()

	def changeState( self, state ):
		self.editingState = state
		if state:
			self.window.panelScript.setEnabled( True )
			self.window.textScriptRender.setPlainText( state.renderScript )
			self.window.textScriptInit.setPlainText( state.initScript )
			self.refreshScriptTitle()
		else:
			self.window.panelScript.setEnabled( False )

	def changeSelection( self, selection ):
		self.propEditor.setTarget( selection )
		self.canvas.safeCallMethod( 'preview', 'changeSelection', selection )


	def refreshScriptTitle( self ):
		state = self.editingState
		self.window.labelStateName.setText( 'current editing state script: <%s>' % state.name )
		# if not state: return
		# tabParent = self.window.panelScript
		# idx = tabParent.indexOf( self.window.tabInit )
		# tabParent.setTabText( idx, 'Init Script <%s>' % state.name )
		# idx = tabParent.indexOf( self.window.tabRender )
		# tabParent.setTabText( idx, 'Render Script <%s>' % state.name )

	def onScriptModified( self ):
		self.scriptModifyFlag = 1

	def checkScript( self ):
		if self.scriptModifyFlag == 0:
			self.canvas.safeCallMethod(
				'preview',
				'updateScript', 
				self.window.textScriptInit.toPlainText(),
				self.window.textScriptRender.toPlainText()
			 )
		if self.scriptModifyFlag >= 0:
			self.scriptModifyFlag -= 1

	def onPropertyChanged( self, obj, field, value ):
		if field == 'name':
			self.tree.refreshNodeContent( obj )
			if obj == self.editingState:
				self.refreshScriptTitle()
		else:
			self.canvas.safeCallMethod( 'preview', 'update', obj, field, value )

	def onTool( self, tool ):
		if tool.name == 'update':
			if self.editingAsset:				
				self.canvas.safeCallMethod( 'preview', 'rebuildSystem' )			

		elif tool.name == 'add_state':
			if self.editingAsset:				
				stConfig = self.canvas.safeCallMethod( 'preview', 'addState' )
				if stConfig:
					self.tree.addNode( stConfig )
					self.tree.selectNode( stConfig )
					self.tree.editNode( stConfig )

		elif tool.name == 'add_emitter':
			if self.editingAsset:				
				emConfig = self.canvas.safeCallMethod( 'preview', 'addEmitter' )
				if emConfig:
					self.tree.addNode( emConfig )
					self.tree.selectNode( emConfig )
					self.tree.editNode( emConfig )

		elif tool.name == 'remove':
			pass

		elif tool.name == 'save':
			self.saveAsset()

		elif tool.name == 'start_preview':
			self.canvas.safeCallMethod( 'preview', 'startPreview' )

		elif tool.name == 'stop_preview':
			self.canvas.safeCallMethod( 'preview', 'stopPreview' )
		


##----------------------------------------------------------------##
class ParticleTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name', -1) ]

	def getRootNode( self ):
		return self.module

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.module:
			return None

		if node == self.module.editingConfig:
			return self.module

		if node in [ self.module.emitters, self.module.states ]:
			return self.module.editingConfig

		clas = node.getClassName( node )
		if clas == 'ParticleEmitterConfig':
			return self.module.emitters

		if clas == 'ParticleStateConfig':
			return self.module.states

		return node.parent

	def getNodeChildren( self, node ):
		config = self.module.editingConfig
		if node == self.module:
			if config:
				return [ config ]
			else:
				return []

		if node == config:
			return [ self.module.emitters, self.module.states ] #virtual nodes
		
		if node == self.module.emitters:			
			return [ item for item in config.emitters.values() ]

		if node == self.module.states:
			return [ item for item in config.states.values() ]

		return []

	def updateItemContent( self, item, node, **option ):
		if node == self.module: return

		if node == self.module.emitters:
			item.setText( 0, 'Emitters' )
			item.setIcon( 0, getIcon('folder') )
		elif node == self.module.states:
			item.setText( 0, 'States' )
			item.setIcon( 0, getIcon('folder') )
		elif node == self.module.editingConfig:
			item.setText( 0, 'Particle System' )
			item.setIcon( 0, getIcon('particle') )
		elif node.getClassName( node ) in [ 'ParticleEmitterConfig', 'ParticleStateConfig' ]:
			item.setText( 0, node.name )
			item.setIcon( 0, getIcon('obj') )
		else:
			item.setText( 0, '' )
			item.setIcon( 0, getIcon('obj') )
		
	def onItemSelectionChanged(self):
		for selection in self.getSelection():
			self.module.changeSelection( selection )			
			break

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )
		# app.getModule('layer_manager').changeLayerName( layer, item.text(0) )

	# def onItemActivated( self, item, col ):
	# 	node = self.getNodeByItem( item )
	# 	if isinstance( node, _LuaObject ):
	# 		clas = node.getClassName( node )
	# 		if clas == 'ParticleStateConfig':
	# 			self.module.changeState( node )
	# 		elif clas == 'ParticleEmitterConfig':
	# 			self.module.canvas.safeCallMethod( 'preview', 'activateEmitter', node )
##----------------------------------------------------------------##

##----------------------------------------------------------------##

ParticleEditor().register()
##----------------------------------------------------------------##
