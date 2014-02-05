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

class EffectEditor( AssetEditorModule ):
	def __init__(self):
		super(EffectEditor, self).__init__()
		self.editingAsset = None

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
		self.addTool( 'effect_editor/start_preview', icon = 'play' )
		self.addTool( 'effect_editor/stop_preview', icon = 'stop' )

		
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
					editable = False
				)
			)
		self.tree.module = self

		self.codebox = codebox = addWidgetWithLayout(
			CodeBox( window.containerScript )
		)
		settingData = jsonHelper.tryLoadJSON(
				self.getApp().findDataFile( 'script_settings.json' )
			)
		if settingData:
			codebox.applySetting( settingData )


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
		self.container.setDocumentName( node.getNodePath() )
		self.editingAsset  = node

	def saveAsset( self ):
		if not self.editingAsset: return
		self.canvas.safeCallMethod( 'editor', 'save', self.editingAsset.getAbsFilePath() )



##----------------------------------------------------------------##
class EffectNodeTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name', 140), ('Type', 50) ]

	def getRootNode( self ):
		return self.module.getCurrentConfig()

	def getNodeParent( self, node ):
		if node == self.getRootNode(): return None
		return self.getRootNode()

	def getNodeChildren( self, node ):		
		if node == self.getRootNode():
			return [ action for action in node.actions.values() ]
		else:
			return []

	def updateItemContent( self, item, node, **option ):
		if node == self.getRootNode():
			item.setText( 0, node['name'] )
			item.setIcon( 0, getIcon('character') )
		else:
			item.setText( 0, node['name'] )
			if node['loop']:
				item.setText( 1, 'true')
			else:
				item.setText( 1, '')
			item.setIcon( 0, getIcon('clip') )

	def onClicked(self, item, col):
		self.module.selectEditTarget( item.node )

	def onItemSelectionChanged(self):
		self.module.selectEditTarget( self.getFirstSelection() )

	def onItemChanged( self, item, col ):
		node = item.node
		self.module.renameAction( node, item.text(0) )


##----------------------------------------------------------------##
EffectEditor().register()
