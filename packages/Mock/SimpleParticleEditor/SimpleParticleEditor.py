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

##----------------------------------------------------------------##

class SimpleParticleEditor( AssetEditorModule ):
	def __init__(self):
		super(SimpleParticleEditor, self).__init__()

	def getName(self):
		return 'simple_particle_editor'

	def getDependency(self):
		return [ 'qt', 'mock' ]

	def onLoad(self):
		self.windowTitle = 'Pex Editor'
		self.container = self.requestDocumentWindow('SimpleParticleEditor',
				title       = 'Pex Editor',
				size        = (500,300),
				minSize     = (500,300),
			)

		self.toolbar = self.addToolBar( 'simple_particle_editor', self.container.addToolBar() )

		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('SimpleParticleEditor.ui')
		)
		
		self.propEditor = addWidgetWithLayout(
			PropertyEditor( window.containerPropSystem )
		)

		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas( window.containerPreview )
		)

		self.canvas.loadScript( _getModulePath('SimpleParticleEditor.lua') )


		self.addTool( 'simple_particle_editor/save',          label = 'Save', icon = 'save' )
		self.addTool( 'simple_particle_editor/clone',         label = 'Clone', icon = 'clone' )

		self.propEditor .propertyChanged .connect(self.onPropertyChanged)
		signals.connect('asset.modified', self.onAssetModified)

		self.container.setEnabled( False )
		self.editingAsset = None
		self.updateSchduleTimer = QtCore.QTimer( self.container )
		self.updateSchduleTimer.setInterval( 50 )
		self.updateSchduleTimer.setSingleShot( True )
		self.updateSchduleTimer.timeout.connect( self.updatePreview )

	def onStop( self ):
		self.saveAsset()

	def onSetFocus(self):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def saveAsset(self):
		if not self.editingAsset: return
		self.canvas.callMethod( 'editor', 'save' , self.editingAsset.getAbsFilePath() )
		
	def openAsset(self, node, subnode=None):
		self.setFocus()
		if self.editingAsset != node:
			self.saveAsset()
			self.container.setEnabled( True )
			self.editingAsset = node
			self.container.setDocumentName( node.getNodePath() )
			self.canvas.makeCurrent()
			target = self.canvas.callMethod( 'editor', 'open' , node.getNodePath() )
			self.propEditor.setTarget( target )

	def scheduleUpdate( self ):
		self.updateSchduleTimer.stop()
		self.updateSchduleTimer.start()

	def updatePreview( self ):
		self.canvas.makeCurrent()
		self.canvas.callMethod( 'editor', 'updateParticle' )

	def onAssetModified( self, asset ):
		pass

	def onPropertyChanged( self, obj, id, value ):
		self.scheduleUpdate()

##----------------------------------------------------------------##
SimpleParticleEditor().register()
