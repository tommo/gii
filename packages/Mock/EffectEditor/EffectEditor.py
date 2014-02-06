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
from gii.scintilla import CodeBox

from gii.AssetEditor  import AssetEditorModule

from gii.moai.MOAIEditCanvas import MOAIEditCanvas
from gii.moai import _LuaObject

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt
from gii.SearchView import requestSearchView

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

class EffectEditor( AssetEditorModule ):
	def __init__(self):
		super(EffectEditor, self).__init__()
		self.editingAsset     = None
		self.editConfig       = None
		self.previewing       = False
		self.refreshFlag      = -1
		self.scriptModifyFlag = -1
		self.refreshingScript = False

	def getName(self):
		return 'effect_editor'

	def getDependency(self):
		return [ 'qt', 'mock' ]

	def onLoad(self):
		self.windowTitle = 'Effect System Editor'
		self.container = self.requestDocumentWindow('MockEffectEditor',
				title       = 'Effect Editor',
				size        = (500,300),
				minSize     = (500,300),
				# allowDock = False
			)

		self.tool = self.addToolBar( 'effect_editor', self.container.addToolBar() )
		self.addTool( 'effect_editor/save',   label = 'Save', icon = 'save' )
		self.addTool( 'effect_editor/----' )
		self.addTool( 'effect_editor/remove_node', icon = 'remove' )
		self.addTool( 'effect_editor/clone_node',  icon = 'clone'    )
		self.addTool( 'effect_editor/add_system',  label = '+System' )
		self.addTool( 'effect_editor/add_child',   label = '+Child' )
		self.addTool( 'effect_editor/----' )
		self.addTool( 'effect_editor/move_up',     icon = 'arrow-up' )
		self.addTool( 'effect_editor/move_down',   icon = 'arrow-down' )
		self.addTool( 'effect_editor/----' )
		self.addTool( 'effect_editor/toggle_preview', icon = 'play', type = 'check' )

		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('EffectEditor.ui')
		)
		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas( window.containerPreview )
		)
		
		self.tree = addWidgetWithLayout(
				EffectNodeTreeWidget( 
					window.containerTree, 
					multiple_selection = False,
					editable = True
				)
			)
		self.tree.module = self
		
		propLayout = QtGui.QVBoxLayout()
		window.containerEditor.setLayout( propLayout )
		propLayout.setSpacing( 2 )
		propLayout.setMargin ( 0 )

		self.nodePropEditor  = PropertyEditor( window.containerEditor )
		self.paramPropEditor = PropertyEditor( window.containerEditor )
				
		propLayout.addWidget( self.nodePropEditor )
		propLayout.addWidget( self.paramPropEditor )
		self.paramPropEditor.setVisible( False )
		window.containerScript.setVisible( False )

		self.codebox = codebox = addWidgetWithLayout(
			CodeBox( window.containerScript )
		)
		settingData = jsonHelper.tryLoadJSON(
				self.getApp().findDataFile( 'script_settings.json' )
			)
		if settingData:
			codebox.applySetting( settingData )
		
		#ShortCuts
		self.addShortcut( self.container, '+',  self.addSystem )
		self.addShortcut( self.container, '=',  self.promptAddChild )
		self.addShortcut( self.container, '-',  self.removeNode )
		# self.addShortcut( self.container, ']',  self.moveNodeUp )
		# self.addShortcut( self.container, '[',  self.moveNodeDown )
		self.addShortcut( self.container, 'ctrl+D',  self.cloneNode )
		self.addShortcut( self.container, 'f5',      self.togglePreview )

		#Signals
		self.nodePropEditor   .propertyChanged  .connect( self.onNodePropertyChanged  )
		self.paramPropEditor  .propertyChanged  .connect( self.onParamPropertyChanged )
		self.codebox          .textChanged      .connect( self.onScriptChanged )

	def onStart( self ):
		self.canvas.loadScript( _getModulePath('EffectEditor.lua') )

	def onSetFocus( self ):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def openAsset( self, node ):
		self.setFocus()
		if self.editingAsset == node: return
		self.editConfig = self.canvas.safeCallMethod( 'editor', 'open', node.getNodePath() )
		self.editingAsset  = node
		self.container.setDocumentName( node.getNodePath() )
		self.tree.rebuild()
		self.selectEditTarget( None )
		self.checkScriptTimer  = self.container.startTimer( 3, self.checkScript )
		self.checkRefreshTimer = self.container.startTimer( 10, self.checkRefresh )

	def saveAsset( self ):
		if not self.editingAsset: return
		self.canvas.safeCallMethod( 'editor', 'save', self.editingAsset.getAbsFilePath() )

	def closeAsset( self ):
		self.checkScriptTimer.stop()

	def getEditingConfig( self ):
		return self.editConfig

	def selectEditTarget( self, node ):
		self.editingTarget = node
		self.nodePropEditor.setTarget( node )
		#check tool button state
		# isSystem = isMockInstance( node, 'EffectNodeParticleSystem' )
		if isMockInstance( node, 'EffectNodeParticleState' ):
			self.window.containerScript.setVisible( True )
			self.paramPropEditor.setVisible( True )
			self.updateScript()
		else:
			self.window.containerScript.setVisible( False )
			self.paramPropEditor.setVisible( False )
			self.paramPropEditor.setTarget( None )

	def renameNode( self, node, name ):
		node['name'] = name
		if node == self.editingTarget:
			self.nodePropEditor.refreshField( 'name' )

	def postCreateNode( self, node ):
		self.tree.addNode( node )
		self.tree.selectNode( node )
		self.tree.editNode( node )
		self.markNodeDirty( node )

	def listParticleSystemChildTypes( self, typeId, context ):
		entries = [
			( 'state',            'State',              '', 'effect/state'            ),
			( 'emitter-timed',    'Emitter Timed',     '', 'effect/emitter-timed'    ),
			( 'emitter-distance', 'Emitter Distance',  '', 'effect/emitter-distance' ),
			( 'force-attractor',  'Force Attractor',   '', 'effect/force-attractor'  ),
			( 'force-basin',      'Force Basin',       '', 'effect/force-basin'      ),
			( 'force-linear',     'Force Linear',      '', 'effect/force-linear'     ),
			( 'force-radial',     'Force Radial',      '', 'effect/force-radial'     ),
		]
		return entries

	def addChildNode( self, childType ):
		if self.editingTarget:
			node = self.canvas.callMethod( 'editor', 'addChildNode', self.editingTarget, childType )
			self.postCreateNode( node )

	def removeNode( self ):
		if self.editingTarget:
			self.markNodeDirty( self.editingTarget )
			self.canvas.callMethod( 'editor', 'removeNode', self.editingTarget )
			self.tree.removeNode( self.editingTarget )

	def promptAddChild( self ):
		requestSearchView( 
			context      = 'effect_editor',
			type         = None,
			multiple_selection = False,
			on_selection = self.addChildNode,
			on_search    = self.listParticleSystemChildTypes				
		)

	def cloneNode( self ):
		if self.editingTarget:
			node = self.canvas.callMethod( 'editor', 'cloneNode', self.editingTarget )
			self.postCreateNode( node )

	def addSystem( self ):
		sys = self.canvas.callMethod( 'editor', 'addSystem' )
		self.postCreateNode( sys )

	def updateScript( self ):
		self.refreshingScript = True
		stateNode = self.editingTarget
		self.codebox.setText( stateNode.script or '' )
		self.updateParamProxy()
		self.refreshingScript = False
		#TODO: param

	def updateParamProxy( self ):
		stateNode = self.editingTarget
		self.paramProxy = stateNode.buildParamProxy( stateNode )
		self.paramPropEditor.setTarget( self.paramProxy )		

	def onScriptChanged( self ):
		if self.refreshingScript: return
		src = self.codebox.text()
		stateNode = self.editingTarget
		stateNode.script = src
		self.scriptModifyFlag = 1

	def togglePreview( self ):
		self.previewing = not self.previewing
		if self.previewing:
			self.canvas.callMethod( 'editor', 'startPreview' )
		else:
			self.canvas.callMethod( 'editor', 'stopPreview' )
		self.checkTool( 'effect_editor/toggle_preview', self.previewing )

	def onTool( self, tool ):
		name = tool.name
		if name == 'save':
			self.saveAsset()
		elif name == 'add_system':
			self.addSystem()

		elif name == 'add_child':
			self.promptAddChild()			
		
		elif name == 'remove_node':
			self.removeNode()			

		elif name == 'clone_node':
			self.cloneNode()

		elif name == 'toggle_preview':
			self.togglePreview()

	def onNodePropertyChanged( self, node, id, value ):
		if id == 'name':
			self.tree.refreshNodeContent( node )
		else:
			self.markNodeDirty( self.editingTarget )

	def onParamPropertyChanged( self, node, id, value ):
		self.markNodeDirty( self.editingTarget )

	def markNodeDirty( self, node ):
		self.canvas.callMethod( 'editor', 'markDirty', node )
		self.refreshFlag = 1

	def checkScript( self ):
		if self.scriptModifyFlag == 0:
			self.updateParamProxy()
			self.markNodeDirty( self.editingTarget )

		if self.scriptModifyFlag >= 0:
			self.scriptModifyFlag -= 1

	def checkRefresh( self ):
		if self.refreshFlag > 0 :
			self.canvas.callMethod( 'editor', 'refreshPreview' )
			self.refreshFlag = 0

##----------------------------------------------------------------##
class EffectNodeTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name', 140), ('Type', 50) ]

	def getRootNode( self ):
		config = self.module.getEditingConfig()
		return config and config._root or None

	def getNodeParent( self, node ):
		if node == self.getRootNode(): return None
		return node.parent

	def getNodeChildren( self, node ):		
		return [ node for node in node.children.values() ]

	def updateItemContent( self, item, node, **option ):
		if node == self.getRootNode():
			item.setText( 0, node['name'] )
			# item.setIcon( 0, getIcon('character') )
		else:
			typeName = node.getTypeName( node )
			item.setText( 0, node['name'] )
			item.setText( 1, typeName )
			item.setIcon( 0, getIcon( 'effect/' + typeName.lower() ) )

	def onClicked(self, item, col):
		self.module.selectEditTarget( item.node )

	def onItemSelectionChanged(self):
		self.module.selectEditTarget( self.getFirstSelection() )

	def onItemChanged( self, item, col ):
		node = item.node
		self.module.renameNode( node, item.text(0) )


##----------------------------------------------------------------##
EffectEditor().register()
