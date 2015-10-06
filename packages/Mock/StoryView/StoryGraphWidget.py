import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.qt.controls.GraphicsView.GraphNodeView import  *

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

StoryGraphWidgetUI,BaseClass = uic.loadUiType( _getModulePath('StoryView.ui') )


##----------------------------------------------------------------##
class StoryGraphWidget( QtGui.QWidget, StoryGraphWidgetUI ):
	def __init__(self, *args, **kwargs ):
		super(StoryGraphWidget, self).__init__( *args, **kwargs )
		self.setupUi( self )
		self.owner = None
		self.graphView = addWidgetWithLayout( GraphNodeViewWidget( parent = self.containerGraph ) )
		self.containerContent.hide()
		self.buildTestData()

	def setOwner( self, owner ):
		self.owner = owner

	def buildTestData( self ):
		scene = self.graphView.scene
		group = GraphNodeGroupItem()
		scene.addItem( group )

		node1 = GraphNodeItem()
		node2 = GraphNodeItem()
		node3 = GraphNodeItem()
		node4 = GraphNodeItem()
		node5 = GraphNodeItem()

		node1.setPos( 200, 100 )
		
		scene.addItem( node1 )
		scene.addItem( node2 )
		scene.addItem( node3 )
		scene.addItem( node4 )
		scene.addItem( node5 )

		conn = GraphNodeConnectionItem( node1.getOutPort( 'p1' ), node2.getInPort( 'p0' ) )
		scene.addItem( conn )
		conn = GraphNodeConnectionItem( node2.getOutPort( 'p1' ), node3.getInPort( 'p0' ) )
		scene.addItem( conn )
		