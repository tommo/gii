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
class GraphNodeViewScene( QtGui.QGraphicsScene ):
	def __init__( self, parent ):
		super( GraphNodeViewScene, self ).__init__( parent = parent )
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
		super( GraphNodeViewScene, self ).mousePressEvent( event )

	def mouseMoveEvent( self, event ):
		if self.connecting:
			if event.scenePos().x() > self.connecting.srcPort.scenePos().x():
				self.dummyPort.dir = -1
			else:
				self.dummyPort.dir = 1
			self.dummyPort.setPos( event.scenePos() )
			self.dummyPort.updateConnections()
		super( GraphNodeViewScene, self ).mouseMoveEvent( event )

	def mouseReleaseEvent( self, event ):
		if self.connecting:
			self.dummyPort.setPos( event.scenePos() )
			item = self.itemAt( event.scenePos() )
			if isinstance( item, GraphNodePort ):
				if not self.connecting.setDstPort( item ): #not accepted
					self.connecting.delete()
			else:
				self.connecting.delete()
			self.connecting = None
		super( GraphNodeViewScene, self ).mouseReleaseEvent( event )

class GraphNodeView( GLGraphicsView ):
	def __init__( self, *args, **kwargs ):
		super( GraphNodeView, self ).__init__( *args, **kwargs )

class GraphNodeViewWidget( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( GraphNodeViewWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )

		self.scene = GraphNodeViewScene( parent = self )
		self.scene.setBackgroundBrush( Qt.black );
		self.view = GraphNodeView( self.scene, parent = self )
		self.view.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		layout.addWidget( self.view )
		self.testData()

	def testData( self ):
		group = GraphNodeGroup()
		self.scene.addItem( group )

		node1 = GraphNode()
		node2 = GraphNode()
		node3 = GraphNode()

		node1.setPos( 200, 100 )
		
		self.scene.addItem( node1 )#.setParentItem( group )
		self.scene.addItem( node2 )#.setParentItem( group )
		self.scene.addItem( node3 )#.setParentItem( group )

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
	