# -*- coding: utf-8 -*-
import sys
import math

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor

from GraphicsViewHelper import *
from GraphNode import *

##----------------------------------------------------------------##
class GraphScene( QtGui.QGraphicsScene ):
	def __init__( self, parent ):
		super( GraphScene, self ).__init__( parent = parent )
		dummyPort = GraphNodePort()
		dummyPort.setFlag( dummyPort.ItemHasNoContents, True )
		dummyPort.hide()
		self.dummyPort = dummyPort
		self.addItem( dummyPort )
		self.connecting = None
		self.gridBackground = GridBackground()
		self.addItem( self.gridBackground )
		self.sceneRectChanged.connect( self.onRectChanged )

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def tryStartConnection( self, port ):
		targetPort = self.dummyPort
		conn = GraphNodeConnection( port, targetPort )
		if port.dir == -1:
			targetPort.dir = 1
		else:
			targetPort.dir = -1
		self.addItem( conn )
		self.connecting = conn
		return True

	def mousePressEvent( self, event ):
		item = self.itemAt( event.scenePos() )
		if not item: return
		if isinstance( item, GraphNodePort ):
			self.dummyPort.setPos( event.scenePos() )
			if self.tryStartConnection( item ): return
		super( GraphScene, self ).mousePressEvent( event )

	def mouseMoveEvent( self, event ):
		if self.connecting:
			if event.scenePos().x() > self.connecting.srcPort.scenePos().x():
				self.dummyPort.dir = -1
			else:
				self.dummyPort.dir = 1
			self.dummyPort.setPos( event.scenePos() )
			self.dummyPort.updateConnections()
		super( GraphScene, self ).mouseMoveEvent( event )

	def mouseReleaseEvent( self, event ):
		if self.connecting:
			self.dummyPort.setPos( event.scenePos() )
			item = self.itemAt( event.scenePos() )
			if isinstance( item, GraphNodePort ):
				self.connecting.setDstPort( item )
			else:
				self.connecting.delete()
			self.connecting = None
		super( GraphScene, self ).mouseReleaseEvent( event )

class GraphView( GLGraphicsView ):
	def __init__( self, *args, **kwargs ):
		super( GraphView, self ).__init__( *args, **kwargs )

class GraphWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( GraphWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )

		self.scene = GraphScene( parent = self )
		self.scene.setBackgroundBrush( Qt.black );
		self.view = GraphView( self.scene, parent = self )
		self.view.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		layout.addWidget( self.view )
		self.testData()

	def testData( self ):
		node1 = GraphNode()
		self.scene.addItem( node1 )
		node2 = GraphNode()
		self.scene.addItem( node2 )
		node3 = GraphNode()
		self.scene.addItem( node3 )
		node1.setPos( 200, 100 )
		conn = GraphNodeConnection( node1.getPort( 'out-1' ), node2.getPort( 'in-0' ) )
		self.scene.addItem( conn )
		conn = GraphNodeConnection( node2.getPort( 'out-1' ), node3.getPort( 'in-0' ) )
		self.scene.addItem( conn )

	def closeEvent( self, event ):
		self.view.deleteLater()

	def __del__( self ):
		self.deleteLater()


if __name__ == '__main__':
	import TestGraphView
	