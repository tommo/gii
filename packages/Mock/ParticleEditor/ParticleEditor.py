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

from gii.moai.MOAIEditCanvas    import MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

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
		
		self.emitters = Box()
		self.emitters.items=[]
		
		self.states = Box()
		self.states.items=[]

		
	
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
		self.addTool( 'particle_editor/add_state',   label = '+ State')
		self.addTool( 'particle_editor/add_emitter', label = '+ Emitter')
		self.addTool( 'particle_editor/remove',      label = 'Delete')
		
		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('ParticleEditor2.ui')
		)
		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas( window.containerPreview )
		)
		self.tree = addWidgetWithLayout(
			ParticleTreeWidget( window.containerTree )
			)
		self.tree.module = self

		self.propEditor = addWidgetWithLayout(
			PropertyEditor( window.containerProperty )
			)
		
	def onStart( self ):
		self.canvas.loadScript( _getModulePath('ParticleEditor.lua') )

	def onSetFocus( self ):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def openAsset( self, node ):
		self.tree.rebuild()
		self.setFocus()


##----------------------------------------------------------------##
class ParticleTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',150), ('Type', 80) ]

	def getRootNode( self ):
		return self.module

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.module.emitters or node == self.module.states:
			return self.getRootNode()

		if node == self.module:
			return None

		return None

	def getNodeChildren( self, node ):
		if node == self.module.emitters or node == self.module.states:
			return node.items
		if node == self.module:
			return [ node.emitters, node.states ]
		return []

	def updateItemContent( self, item, node, **option ):
		if node == self.module.emitters:
			item.setText( 0, 'Emitters' )
			item.setIcon( 0, getIcon('folder') )
			item.setFlags( Qt.ItemIsEnabled | Qt.ItemIsSelectable )
		elif node == self.module.states:
			item.setText( 0, 'States' )
			item.setIcon( 0, getIcon('folder') )
			item.setFlags( Qt.ItemIsEnabled | Qt.ItemIsSelectable )
		else:
			item.setText( 0, '' )
			item.setIcon( 0, getIcon('obj') )
		
	def onItemSelectionChanged(self):
		selections = self.getSelection()

	def onItemChanged( self, item, col ):
		node = self.getNodeByItem( item )
		# app.getModule('layer_manager').changeLayerName( layer, item.text(0) )

##----------------------------------------------------------------##

##----------------------------------------------------------------##

ParticleEditor().register()
##----------------------------------------------------------------##
