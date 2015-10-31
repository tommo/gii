# -*- coding: utf-8 -*-
import sys
import math

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor

from GraphicsViewHelper import *
from GraphNodeConnectionItem import *


##----------------------------------------------------------------##
class GraphNodeViewRoot( QtGui.QGraphicsItemGroup ):
	pass


##----------------------------------------------------------------##
class GraphNodeViewScene( GLGraphicsScene ):
	def __init__( self, parent ):
		super( GraphNodeViewScene, self ).__init__( parent = parent )
		dummyPort = GraphNodePortItem()
		dummyPort.setFlag( dummyPort.ItemHasNoContents, True )
		dummyPort.hide()
		self.rootItem = GraphNodeViewRoot()
		self.addItem( self.rootItem )

		self.dummyPort = dummyPort
		self.addItem( dummyPort )

		self.gridBackground = GridBackground()
		self.addItem( self.gridBackground )

		self.connecting = None
		self.sceneRectChanged.connect( self.onRectChanged )

	def clear( self ):
		super( GraphNodeViewScene, self ).clear()
		

	def onRectChanged( self, rect ):
		self.gridBackground.setRect( rect )

	def tryStartConnection( self, port ):
		targetPort = self.dummyPort
		conn = GraphNodeLineConnectionItem( port, targetPort )
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
		if isinstance( item, GraphNodePortItem ):
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
			if isinstance( item, GraphNodePortItem ):
				if not self.connecting.setDstPort( item ): #not accepted
					self.connecting.delete()
			else:
				self.connecting.delete()
			self.connecting = None
		super( GraphNodeViewScene, self ).mouseReleaseEvent( event )

##----------------------------------------------------------------##
class GraphicsViewDelegate():
	def mousePressEvent( self, view, ev ):
		return None

	def mouseReleaseEvent( self, view, ev ):
		return None

	def mouseMoveEvent( self, view, ev ):
		return None
		
##----------------------------------------------------------------##
class GraphicsItemMoveTool( GraphicsViewDelegate ):
	def mousePressEvent( self, view, ev ):
		item = view.itemAt( ev.pos() )
		return True

	def mouseReleaseEvent( self, view, ev ):
		return True

	def mouseMoveEvent( self, view, ev ):
		return True


##----------------------------------------------------------------##
class GraphNodeView( GLGraphicsView ):
	def __init__( self, *args, **kwargs ):
		super( GraphNodeView, self ).__init__( *args, **kwargs )
		self._delegate = GraphicsItemMoveTool()

	# def mousePressEvent( self, ev ):
	# 	print ev.pos()
	# # 	if self._delegate:
	# # 		result = self._delegate.mousePressEvent( self, ev )
	# # 		if result: return
	# 	return super( GraphNodeView, self ).mousePressEvent( ev )

	def mouseReleaseEvent( self, ev ):
	# 	if self._delegate:
	# 		result = self._delegate.mouseReleaseEvent( self, ev )
	# 		if result: return
		return super( GraphNodeView, self ).mouseReleaseEvent( ev )

	def mouseMoveEvent( self, ev ):
	# 	if self._delegate:
	# 		result = self._delegate.mouseMoveEvent( self, ev )
	# 		if result: return
		return super( GraphNodeView, self ).mouseMoveEvent( ev )

##----------------------------------------------------------------##
class GraphNodeViewWidget( QtGui.QWidget ):
		
	def __init__( self, *args, **kwargs ):
		super( GraphNodeViewWidget, self ).__init__( *args, **kwargs )		
		layout = QtGui.QVBoxLayout( self )

		self.scene = GraphNodeViewScene( parent = self )
		self.scene.setBackgroundBrush( Qt.black );
		self.view = GraphNodeView( self.scene, parent = self )
		self.view.setSceneRect( QRectF( 0,0, 10000, 10000 ) )
		layout.addWidget( self.view )
		layout.setSpacing( 0 )
		layout.setMargin( 0 )

		self.nodeToItem = {}

	def getItemByNode( self, node ):
		return self.nodeToItem.get( node )

	def getNodeByItem( self, item ):
		return item.node

	def addNode( self, node ):
		item = createItemForNode( node )
		item.node = node
		self.nodeToItem[ node ] = item
		return

	def removeNode( self, node ):
		item = self.getItemByNode( node )
		if not item: return
		del self.nodeToItem[ node ]
		item.delete()

	def createItemForNode( self, node ):
		item = GraphNodeItem()
		return item

	def rebuild( self ):
		pass

	def clear( self ):
		self.scene.clear()
		self.nodeToItem = {}

	def closeEvent( self, event ):
		self.view.deleteLater()

	def __del__( self ):
		self.deleteLater()


if __name__ == '__main__':
	import TestGraphView
	