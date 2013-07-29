import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.AssetEditor  import AssetEditorModule

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

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

_LOREM = '''Lorem ipsum dolor sit amet, consectetur adipisicing elit, '''

##----------------------------------------------------------------##
class TextureManager( AssetEditorModule ):
	"""docstring for MockStyleSheetEditor"""
	def __init__(self):
		super(TextureManager, self).__init__()
	
	def getName(self):
		return 'mock.texture_manager'

	def getDependency(self):
		return [ 'qt', 'moai' ]

	def onLoad(self):
		self.container = self.requestDocumentWindow( 'MockTextureManager',
				title       = 'TextureManager',
				size        = (500,300),
				minSize     = (500,300),
				# allowDock = False
			)

		self.container.hide()

		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('TextureCenter.ui')
		)
		
		self.previewCanvas = addWidgetWithLayout(
			MOAIEditCanvas( window.framePreview),
			window.framePreview
		)

		treeTextures = window.treeTextures
		#header item
		headerItem=QtGui.QTreeWidgetItem()		
		headerItem.setText( 0, 'Name' ) ;    treeTextures.setColumnWidth( 0, 80 )
		headerItem.setText( 1, 'Group' ) ;   treeTextures.setColumnWidth( 1, 50 )
		headerItem.setText( 2, 'Width' ) ;   treeTextures.setColumnWidth( 2, 20 )
		headerItem.setText( 3, 'Height' ) ;  treeTextures.setColumnWidth( 3, 20 )
		treeTextures.setHeaderItem(headerItem)

		# self.previewCanvas.loadScript(_getModulePath('StyleSheetPreview.lua'))

TextureManager().register()
